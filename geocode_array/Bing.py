import json
import logging
import pprint
import time
import urllib.parse

from geocode_array.Geocoder import Geocoder, _make_request
from geocode_array import REQUEST_HEADER_DICT, REQUEST_TRIES, REQUEST_DELAY


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
                               path_parameters=True)

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
