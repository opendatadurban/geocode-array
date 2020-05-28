import logging
import unittest

from geocode_array.geocode_array import _find_mean_pos, _find_dist_mean, combine_geocode_results, \
    combine_double_geocode_results


class TestGeocodeArray(unittest.TestCase):
    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s-%(module)s.%(funcName)s [%(levelname)s]: %(message)s')

        self.result_tuples = (
            ("Geocoder 1", "Main & Fagen Rd Strand", -34.1001, 18.1001, 1.2020675644674855e-05),
            ("Geocoder 2", "Main & Fagen Rd Strand", -34.1002, 18.1002, 0.0),
            ("Geocoder 3", "Main & Fagen Rd Strand", -34.1003, 18.1003, 0.00012542609454913077),
        )
        self.mean_pos = (-34.1002, 18.1002,)
        self.dist_mean = 9.428090415798661e-05

    def test_find_pos_mean(self):
        test_vals = _find_mean_pos(self.result_tuples)

        self.assertAlmostEqual(self.mean_pos[0], test_vals[0], 7,
                               "Not finding the mean latitude to within 7 decimal places")
        self.assertAlmostEqual(self.mean_pos[1], test_vals[1], 7,
                               "Not finding the mean longitude to within 7 decimal places")

    def test_find_dist_mean(self):
        test_val = _find_dist_mean(self.mean_pos[0], self.mean_pos[1], self.result_tuples)
        logging.debug(f"test result: {test_val}")

        self.assertAlmostEqual(test_val, self.dist_mean, 7,
                               "Not finding mean distance to mean point within 7 decimal places")

    def test_combine_geocode_results(self):
        # Testing the happy case - i.e. all Geocoders with error values

        # Expected return structure: (mean lat, mean lon, error, [Geocoders])
        test_result = (*self.mean_pos, self.dist_mean, [gc for gc, *_ in self.result_tuples])
        combined_result = combine_geocode_results(self.result_tuples)

        logging.debug(f"combined_result: {combined_result}")

        self.assertTupleEqual(combined_result, test_result,
                              "Combined result of all geocoders wrong")

        # Testing one of the combination cases - expecting 4 to be excluded
        result_tuples_2 = (
            ("Geocoder 1", "Main & Fagen Rd Strand", -34.1001, 18.1001, None),
            ("Geocoder 3", "Main & Fagen Rd Strand", -34.1003, 18.1003, None),
            ("Geocoder 4", "Main & Fagen Rd Strand", -34.2001, 18.2001, None),
        )
        test_result_2 = (*self.mean_pos, self.dist_mean*3/2, ["Geocoder 1", "Geocoder 3"])

        combined_result_2 = combine_geocode_results(result_tuples_2)

        self.assertTupleEqual(combined_result_2, test_result_2,
                              "Combined result of subset of geocoders wrong")

        # Testing the failure case
        result_tuples_3 = (
            ("Geocoder 1", "Main & Fagen Rd Strand", -34.1001, 18.1001, None),
            ("Geocoder 4", "Main & Fagen Rd Strand", -34.2001, 18.2001, None),
            ("Geocoder 5", "Main & Fagen Rd Strand", -34.3001, 18.3001, None),
        )
        combined_result_3 = combine_geocode_results(result_tuples_3)

        self.assertIsNone(combined_result_3, "When the geocoders disagree, there should be a null result")

    def test_combine_double_geocode_results(self):
        # Testing the happy case - i.e. all Geocoders with error values. Really testing that the plumbing to
        # combine_geocode is working

        test_result = (*self.mean_pos, self.dist_mean, [gc for gc, *_ in self.result_tuples])
        combined_result = combine_double_geocode_results(self.result_tuples)

        logging.debug(f"combined_result: {combined_result}")

        self.assertTupleEqual(combined_result, test_result,
                              "Combined result of all geocoders wrong")

        # Testing what would be the failure case for the combined_geocode_results
        result_tuples_2 = (
            ("Geocoder 1", "Main & Fagen Rd Strand", -34.1001, 18.1001, 1.2020675644674855e-05),
            ("Geocoder 4", "Main & Fagen Rd Strand", -34.2001, 18.2001, 0.0012542609454913077),
            ("Geocoder 5", "Main & Fagen Rd Strand", -34.3001, 18.3001, 0),
        )
        test_result_2 = (-34.3001, 18.3001, 0, ["Geocoder 5"])

        combined_result_2 = combine_double_geocode_results(result_tuples_2)

        self.assertTupleEqual(combined_result_2, test_result_2, "Not selecting the single best geocoder")

        # Testing the failure case
        result_tuples_3 = (
            ("Geocoder 4", "Main & Fagen Rd Strand", -34.2001, 18.2001, 0.001),
            ("Geocoder 6", "Main & Fagen Rd Strand", -34.3001, 18.3001, 0.002),
            ("Geocoder 7", "Main & Fagen Rd Strand", -34.4001, 18.4001, 0.003),
        )
        combined_result_3 = combine_double_geocode_results(result_tuples_3)

        self.assertIsNone(combined_result_3, "Not getting a null result when there is no geocoder below threshold")

if __name__ == '__main__':
    unittest.main()
