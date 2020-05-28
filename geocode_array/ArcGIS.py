import logging
import pprint
import urllib.parse

from geocode_array.Geocoder import Geocoder


class ArcGIS(Geocoder):
    reverse_geocode_url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode'
    geocode_url = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates'

    def _form_reverse_geocode_request_args(self, lat, long) -> str:
        values = {"location": f'{long},{lat}',
                  "outSR": 4326,
                  "f": "pjson"}
        logging.debug(f"reverse geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_address_from_reverse_geocode(self, response) -> str or None:
        if 'address' in response and 'LongLabel' in response['address']:
            address = response['address']['LongLabel']
        elif 'address' in response and 'Match_addr' in response['address']:
            address = response['address']['Match_addr']
        else:
            address = None

        return address

    def _form_geocode_request_args(self, address) -> str:
        values = {
            "singleLine": address,
            "outSR": 4326,
            "f": "pjson"
        }
        logging.debug(f"geocode values={pprint.pformat(values)}")

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_coords_from_geocode(self, response) -> (float, float) or (None, None):
        if 'candidates' in response and len(response['candidates']) > 0:
            first_candidate, *_ = response['candidates']
            lat = float(first_candidate['location']['y'])
            long = float(first_candidate['location']['x'])
        else:
            lat = None
            long = None

        return lat, long
