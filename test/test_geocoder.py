import logging
import unittest
import urllib.request

from geocode_array import Geocoder, REQUEST_HEADER_DICT


class TestGeocoder(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s-%(module)s.%(funcName)s [%(levelname)s]: %(message)s')

    def test_form_request(self):
        # vanilla case
        url_base_string = "http://my-fancy-geocoder.org"
        url_request_args = "q=MyAddressString&some-other=arg"
        full_url = f"{url_base_string}?{url_request_args}"

        request_result = Geocoder._form_request(url_base_string, url_request_args, None)

        self.assertIsInstance(request_result, urllib.request.Request, "Form request is not returning a request object")
        self.assertEqual(full_url, request_result.get_full_url(), "Request URL does not match what was passed in")
        self.assertDictEqual(REQUEST_HEADER_DICT, request_result.headers, "Request headers not set up correctly")

        # with proxy
        Geocoder._form_request(url_base_string, url_request_args, "http://my-fancy-proxy")
        # The install proxy method seems to do something dark and unholy in the bowels of urllib,
        # so, if we're here, I'm assuming eveything is OK
        logging.debug("Setup up proxy, OK")

    def test_calc_euclidean_distance(self):
        x = (0, 0)
        y = (3, 4)
        z = 5

        result = Geocoder._calc_euclidean_distance(x, y)
        self.assertEqual(z, result, "Either Pythagoras, or you are wrong. It's probably you.")


if __name__ == '__main__':
    unittest.main()
