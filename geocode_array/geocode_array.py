# -*- coding: utf-8 -*-
"""
CCT Geocode Project:
This code reads in a list of addresses in json or csv format, attempts to geocode these addresses with the ArcGIS and Nominatim geocoders,
compares the results from both geocoders and selects the best. Then it attempts to geocode the addresses with the 
CCT geocoder and returns the output from the CCT geocoder as well as the best result from the combination of ArcGIS and Nominatim
in json and csv format.
"""

import itertools
from multiprocessing.pool import ThreadPool
import logging

from geocode_array import DISPERSION_THRESHOLD, Geocoder


def threaded_geocode(geocoder_list, address):
    for gc in geocoder_list:
        assert isinstance(gc, Geocoder.Geocoder), f"{gc} isn't a Geocoder, I'm afriad"

    with ThreadPool(len(geocoder_list)) as thread_pool:
        results = thread_pool.map(lambda gc: gc.geocode(address), geocoder_list)

    return results


def threaded_double_geocode(geocoder_list, address):
    for gc in geocoder_list:
        assert isinstance(gc, Geocoder.Geocoder), f"{gc} isn't a Geocoder, I'm afriad"

    with ThreadPool(len(geocoder_list)) as thread_pool:
        results = thread_pool.map(lambda gc: gc.double_geocode(address), geocoder_list)

    return results


def _get_geocoders(result_tuples) -> [str]:
    gc_classes = [
        result_tuple[0] for result_tuple in result_tuples
    ]

    return gc_classes


def _find_mean_pos(result_tuples) -> float:
    lat_sum = sum([result_tuple[2] for result_tuple in result_tuples])
    lon_sum = sum([result_tuple[3] for result_tuple in result_tuples])
    tuple_len = len(result_tuples)

    lat_mean = lat_sum / tuple_len
    lon_mean = lon_sum / tuple_len

    return lat_mean, lon_mean


def _find_dist_mean(lat_mean, lon_mean, result_tuples) -> float:
    """Find the average Euclidean distance to a point"""
    dist_sum = sum([
        ((result_tuple[2] - lat_mean) ** 2 + (result_tuple[3] - lon_mean) ** 2) ** 0.5
        for result_tuple in result_tuples
    ])
    tuple_len = len(result_tuples)

    return dist_sum / tuple_len


def combine_results(result_tuples) -> (float or None, float or None, float or None, [str] or None):
    """
    Compares outputs from various geocoders. Assumes that there are no null values

    Uses the following algorithm:
        1. Finds the average location for the combination of results that has the lowest dispersion (mean distance to
        centre, within a certain threshold (~one hectare). Starts out with trying to combine everything, then work
        through the permutations.
        2. If there is no combination that has a dispersion below that threshold, select the result with the lowest
        internal error
        3. Finally, if that isn't possible, just take the first value
    """
    # Finding the average location
    logging.debug(f"Trying all results from {_get_geocoders(result_tuples)}...")
    lat_mean, lon_mean = _find_mean_pos(result_tuples)
    dispersion = _find_dist_mean(lat_mean, lon_mean, result_tuples)

    if dispersion < DISPERSION_THRESHOLD:
        logging.debug("Returning mean of all results")
        return lat_mean, lon_mean, dispersion, _get_geocoders(result_tuples)

    # Working through various permutations
    for c in range(len(result_tuples) - 1, 1, -1):
        logging.debug(f"Taking {c} values...")
        perm_means = [
            _find_mean_pos(perm_tuples)
            for perm_tuples in itertools.permutations(result_tuples, c)
        ]

        perm_results = [
            (*perm_coords, _find_dist_mean(*perm_coords, perm_tuples), _get_geocoders(perm_tuples))
            for perm_coords, perm_tuples in zip(perm_means, itertools.permutations(result_tuples, c))
        ]

        min_result = min(perm_results,
                         key=lambda perm_result: perm_result[-2])
        if min_result[-2] < DISPERSION_THRESHOLD:
            logging.debug(f"Returning best combination of {c} results")
            return min_result

    # Finding the single result with the lowest internal error
    min_result = min(result_tuples,
                     key=lambda result_tuple: (result_tuple[-1] if result_tuple[-1] is not None
                                               else DISPERSION_THRESHOLD))
    if min_result[-1] is None or min_result[-1] >= DISPERSION_THRESHOLD:
        # OK, just returning the first result
        first_result, *_ = result_tuples
        logging.debug("Just returning the first result")
        return first_result[2], first_result[3], None, [first_result[0]]

    elif min_result[-1] is not None and min_result[-1] < DISPERSION_THRESHOLD:
        logging.debug("Returning single best result")
        return min_result[2], min_result[3], min_result[-1], _get_geocoders([min_result])

    else:
        logging.warning("NO VALID RESULTS FOUND")
        return None, None, None, None


