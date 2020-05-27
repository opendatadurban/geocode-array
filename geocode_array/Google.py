import logging
import pprint
import urllib.parse

from geocode_array.Geocoder import Geocoder


class Google(Geocoder):
    reverse_geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    geocode_url = reverse_geocode_url

    def __init__(self, proxy_url=None, api_key=None, **kwargs):
        super().__init__(proxy_url=proxy_url)
        self.api_key = api_key


    def _form_reverse_geocode_request_args(self, lat, long) -> str:
        values = {
            "latlng": f'{lat},{long}',
            "key": self.api_key
        }
        logging.debug(f"reverse geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_address_from_reverse_geocode(self, response) -> str or None:
        if 'results' in response and len(response['results']) > 0:
            first_result, *_ = response['results']
            address = first_result['formatted_address']
        else:
            address = None

        return address

    def _form_geocode_request_args(self, address) -> str:
        values = {
            "address": address,
            "key": self.api_key
        }
        logging.debug(f"geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_coords_from_geocode(self, response) -> (float, float) or (None, None):
        if 'results' in response and len(response['results']) > 0:
            first_result, *_ = response['results']
            lat = float(first_result['geometry']['location']['lat'])
            long = float(first_result['geometry']['location']['lng'])
        else:
            lat = None
            long = None

        return lat, long
