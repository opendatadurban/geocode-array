import json
import logging
import pprint
import time
import urllib.error
import urllib.request

from geocode_array import REQUEST_HEADER_DICT, REQUEST_TRIES, REQUEST_DELAY


def _make_request(request_base_url, request_url_args, proxy_url) -> str or None:
    logging.debug(f"Request Args: {request_url_args.encode('utf-8')}")

    request_string = f"{request_base_url}?{request_url_args}"
    req = urllib.request.Request(
        request_string,
        headers={**REQUEST_HEADER_DICT}
    )
    if proxy_url is not None:
        proxy = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
        auth = urllib.request.HTTPBasicAuthHandler()
        opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
        urllib.request.install_opener(opener)

    tries = REQUEST_TRIES
    while tries > 0:
        try:
            resp = urllib.request.urlopen(req)
            tries = 0
        except urllib.error.URLError as e:
            logging.warning(f"URL request failed with {e.__class__}: '{e}'")

            tries -= 1
            if tries == 0:
                logging.error("Tries exceeded - giving up")
                return None
            else:
                delay = REQUEST_DELAY*(REQUEST_TRIES-tries+1)
                logging.debug(f"Sleeping for '{delay}'")
                time.sleep(delay)

    logging.debug(f"Response Code: {resp.getcode()}")
    code = resp.getcode()

    if code == 200:
        resp_raw = resp.read()
        # logging.debug(f"Raw Result: \n{pprint.pformat(resp_raw)}")
        result = json.loads(resp_raw.decode('utf-8'))
        # logging.debug(f"Result: \n{pprint.pformat(result)}")
    else:
        logging.debug(f'Got incorrect code: {code}')
        result = None

    return result


def _calc_euclidean_distance(coords_1, coords_2) -> float:
    x, y = coords_1
    x2, y2 = coords_2

    numbers_verified = all(
        map(
            lambda c: isinstance(c, float),
            (x, y, x2, y2)
        )
    )
    distance = ((x-x2)**2 + (y-y2)**2)**0.5 if numbers_verified else None
    if distance is not None:
        logging.debug(f"distance is {distance} in degrees decimal, ~{distance*100} m in Cape Town")

    return distance


class Geocoder:
    """
    Geocoder - base class for common geocoding behaviour
    """
    reverse_geocode_url = NotImplemented
    geocode_url = NotImplemented

    def __init__(self, proxy_url=None, **kwargs):
        self.proxy_url = proxy_url

    def _form_reverse_geocode_request_args(self, *args) -> str:
        raise NotImplementedError

    def _get_address_from_reverse_geocode(self, response) -> str or None:
        raise NotImplementedError

    def _reverse_geocode(self, *coords) -> str or None:
        result = _make_request(self.reverse_geocode_url, self._form_reverse_geocode_request_args(*coords), proxy_url=self.proxy_url)

        if result is None:
            return None

        address = self._get_address_from_reverse_geocode(result)

        return address

    def _form_geocode_request_args(self, *args) -> str:
        raise NotImplementedError

    def _get_coords_from_geocode(self, response) -> (float, float) or (None, None):
        raise NotImplementedError

    def _geocode(self, *address) -> (float, float) or None:
        result = _make_request(self.geocode_url, self._form_geocode_request_args(*address), proxy_url=self.proxy_url)

        if result is None:
            return None

        coords = self._get_coords_from_geocode(result)

        if None in coords:
            return None

        return coords

    def geocode(self, address_string, *extra_args) -> (float, float) or None:
        logging.debug(f"address_string={address_string}, extra_args={extra_args}")

        logging.debug(f"Geocod[ing] '{address_string}'")
        coords = self._geocode(address_string, *extra_args)
        logging.debug(f"Geocod[ed] '{address_string}' -> '{coords}'")

        return address_string, coords

    def double_geocode(self, address_string, *extra_args) -> (str or None, float or None, float or None, float or None):
        """
        Step 1: Uses geocoder to find initial co-ordinates.
        Step 2: Reverse initial co-ordinates to find verification address.
        Step 3: Reverse geocoded verification address to find verification co-ordinates.
        Step 4: Calculates distance between both sets of co-ordinates to be used as measure of error.

        Returns: verification address, initial_lat, initial_long, error (distance from step 4)
        """
        logging.debug(f"address_string={address_string}, extra_args={extra_args}")

        logging.debug(f"Geocod[ing] '{address_string}'")
        initial_coords = self._geocode(address_string, *extra_args)
        logging.debug(f"Geocod[ed] '{address_string}' -> '{initial_coords}'")

        if initial_coords is None:
            logging.warning("Initial geocoding failed - returning nulls")
            return None, None, None, None

        logging.debug(f"Reverse Geocod[ing] '{initial_coords}'")
        verification_address = self._reverse_geocode(*initial_coords, *extra_args)
        logging.debug(f"Reverse Geocod[ed] '{initial_coords}' -> '{verification_address}'")

        if verification_address is None:
            logging.warning("Verification reverse geocoding failed - returning unverified initial geocode")
            return address_string, *initial_coords, None

        logging.debug(f"Geocod[ing] '{verification_address}'")
        verification_coords = self._geocode(verification_address, *extra_args)
        logging.debug(f"Geocod[ed] '{verification_address}' -> '{verification_coords}'")

        if verification_coords is None:
            logging.error("Verification geocoding failed - raising runtime error as *this really* shouldn't happen")
            raise RuntimeError(f"Verification geocoding failed for '{address_string}'! "
                               "This means the geocoder and reverse geocoder are inconsistent")

        logging.debug(f"Calculat[ing] error")
        distance = _calc_euclidean_distance(initial_coords, verification_coords)
        logging.debug(f"Calculat[ed] error")

        # hey, it actually worked
        return verification_address, *initial_coords, distance
