import urllib.parse

from geocode_array.Geocoder import Geocoder


class Nominatim(Geocoder):
    reverse_geocode_url = 'https://nominatim.openstreetmap.org/reverse'
    geocode_url = 'https://nominatim.openstreetmap.org/?'

    def _form_reverse_geocode_request_args(self, lat, long) -> str:
        values = {"lat": lat,
                  'lon': long,
                  "format": "jsonv2",
                  "countrycodes": "ZA"}

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_address_from_reverse_geocode(self, response) -> str or None:
        if 'display_name' in response:
            address = response['display_name']
        else:
            address = None

        return address

    def _form_geocode_request_args(self, address) -> str:
        values = {
            "addressdetails": "1",
            "limit": "1",
            "format": "json",
            "countrycodes": "ZA",
            "q": address,
        }

        urlified_values = urllib.parse.urlencode(values)

        return urlified_values

    def _get_coords_from_geocode(self, response) -> (float, float) or (None, None):
        if len(response) > 0 and 'lat' in response[0] and 'lon' in response[0]:
            first_response, *_ = response
            lat = float(first_response['lat'])
            long = float(first_response['lon'])
        else:
            lat = None
            long = None

        return lat, long
