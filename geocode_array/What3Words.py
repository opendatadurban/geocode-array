import logging
import pprint
import urllib.parse

from geocode_array.Geocoder import Geocoder


class what3words(Geocoder):
    reverse_geocode_url = "https://api.what3words.com/v3/convert-to-3wa"
    geocode_url = "https://api.what3words.com/v3/convert-to-coordinates" 

    def __init__(self, proxy_url=None, api_key=None, **kwargs):
        super().__init__(proxy_url=proxy_url)
        self.api_key = api_key


    def _form_reverse_geocode_request_args(self, lat, long) -> str:
        values = {
            "coordinates": f'{lat},{long}',
            "key": self.api_key
        }
        logging.debug(f"reverse geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_address_from_reverse_geocode(self, response) -> str or None:
        if 'words' in response and len(response['words']) > 0:
            address = response['words']
        else:
            address = None

        return address

    def _form_geocode_request_args(self, the_three_words) -> str:
        values = {
            "words": f'{the_three_words}',
            "key": self.api_key
        }
        logging.debug(f"geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)
        
        return urlified_values

    def _get_coords_from_geocode(self, response) -> (float, float) or (None, None):
        if 'coordinates' in response and len(response['coordinates']) > 0:
            first_result = response['coordinates']
            lat = float(first_result['lat'])
            long = float(first_result['lng'])
        else:
            lat = None
            long = None

        return lat, long
