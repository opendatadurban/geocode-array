import json
import logging
import pprint
import time
import urllib.parse

from geocode_array.Geocoder import Geocoder, _make_request
from geocode_array import REQUEST_HEADER_DICT, REQUEST_TRIES, REQUEST_DELAY


def _form_rev_bing_request(request_base_url, request_url_args, proxy_url) -> urllib.request.Request:
        request_string = f"{request_base_url}{request_url_args}"
        req = urllib.request.Request(
            request_string,
            headers={**REQUEST_HEADER_DICT}
        )
        if proxy_url is not None:
            proxy = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
            auth = urllib.request.HTTPBasicAuthHandler()
            opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
            urllib.request.install_opener(opener)

        return req

def _make_bing_rev_request(request_base_url, request_url_args, proxy_url) -> str or None:
    logging.debug(f"Request Args: {request_url_args.encode('utf-8')}")

    req = _form_rev_bing_request(request_base_url, request_url_args, proxy_url)
    tries = REQUEST_TRIES
    while tries > 0:
        try:
            resp = urllib.request.urlopen(req)
            tries = 0
        except Exception as e:
            logging.warning(f"URL request failed with {e.__class__}: '{e}'")

            tries -= 1
            if tries == 0:
                logging.error("Tries exceeded - giving up")
                return None
            else:
                delay = REQUEST_DELAY*(REQUEST_TRIES-tries+1)
                logging.debug(f"Sleeping for '{delay}' - {tries} remaining")
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

class Bing(Geocoder):
    reverse_geocode_url = "http://dev.virtualearth.net/REST/v1/Locations/" 
    geocode_url = "http://dev.virtualearth.net/REST/v1/Locations" 

    def __init__(self, proxy_url=None, api_key=None, **kwargs):
        super().__init__(proxy_url=proxy_url)
        self.api_key = api_key

    # overwrite the _reverse_geocode method for Bing
    def _reverse_geocode(self, *coords) -> str or None:
        result = _make_request(self.reverse_geocode_url,
                               self._form_reverse_geocode_request_args(*coords),
                               proxy_url=self.proxy_url,
                               bing_reverse=True)

        if result is None:
            return None

        address = self._get_address_from_reverse_geocode(result)

        return address
    
    def _form_reverse_geocode_request_args(self, lat, long) -> str:
        
        urlified_values = f"{lat},{long}?&o=json&key={self.api_key}"

        return urlified_values

    def _get_address_from_reverse_geocode(self, response) -> str or None:
        
        if 'resourceSets' in response and 'resources' in response['resourceSets'][0] and len(response['resourceSets'][0]['resources']) > 0:
            first_result = response['resourceSets'][0]['resources'][0]['address']
            address = first_result['formattedAddress']
        else:
            address = None

        return address

    def _form_geocode_request_args(self, address) -> str:
        values = {
            "q": address,
            "o": "json",
            "key": self.api_key,
        }
        logging.debug(f"geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_coords_from_geocode(self, response) -> (float, float) or (None, None):
        
        if 'resourceSets' in response and 'resources' in response['resourceSets'][0] and len(response['resourceSets'][0]['resources']) > 0:
            first_result = response['resourceSets'][0]['resources'][0]['point']['coordinates']
            lat = float(first_result[0])
            long = float(first_result[1])
        else:
            lat = None
            long = None

        return lat, long
