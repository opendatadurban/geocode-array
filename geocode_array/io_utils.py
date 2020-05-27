# -*- coding: utf-8 -*-
"""
CCT Geocode Project:
This code reads in a list of addresses in json or csv format, attempts to geocode these addresses with the ArcGIS and Nominatim geocoders,
compares the results from both geocoders and selects the best. Then it attempts to geocode the addresses with the
CCT geocoder and returns the output from the CCT geocoder as well as the best result from the combination of ArcGIS and Nominatim
in json and csv format.
"""

import csv
import json
import logging
import os
import pprint

from geocode_array import JSON_EXT, CSV_EXT, STD_OUT, ADDRESS_ID_FIELD, ADDRESS_FIELD, RESULT_KEY, INTERNAL_KEY, \
    EXTERNAL_KEY, API_KEY

DATA_READER_DICT = {
    JSON_EXT: lambda input_file: iter(json.load(input_file)),
    CSV_EXT: lambda input_file: csv.DictReader(input_file)
}


def _json_writer(data_file, data):
    json.dump(data, data_file)


def _csv_writer(data_file, data):
    # Using first entry to get column headers
    first_entry, *_ = data.values()
    headers = [ADDRESS_ID_FIELD.lower()]
    headers += [
        f"{prefix}_{key}"
        for prefix in [INTERNAL_KEY, EXTERNAL_KEY]
        for key in first_entry[RESULT_KEY][prefix].keys()
        if key != ADDRESS_ID_FIELD
    ]
    logging.debug(f"headers={', '.join(headers)}")
    csv_writer = csv.DictWriter(data_file, headers)
    csv_writer.writeheader()

    # Flattening everything down to match header structure
    data_dict = (
        {
            ADDRESS_ID_FIELD.lower(): add_id,
            **{
                f"{prefix}_{key}": value
                for prefix in [INTERNAL_KEY, EXTERNAL_KEY]
                for key, value in entry[RESULT_KEY][prefix].items()
                if key != ADDRESS_ID_FIELD
            }
        }
        for add_id, entry in data.items()
    )
    csv_writer.writerows(data_dict)


DATA_WRITER_DICT = {
    JSON_EXT: _json_writer,
    CSV_EXT: _csv_writer,
}


def _check_input_file_validity(input_filename):
    if not os.path.exists(input_filename):
        raise RuntimeError(f"I'm sorry, '{input_filename}' doesn't seem to exit.")
    elif not any(map(lambda ext: input_filename.endswith(ext), DATA_READER_DICT.keys())):
        raise RuntimeError(
            f"I'm sorry, I only know how to handle the following input formats: {', '.join(DATA_READER_DICT.keys())}"
        )


def _get_data(input_filename):
    with open(input_filename) as input_file:
        _, ext = os.path.splitext(input_filename)
        data_loading_func = DATA_READER_DICT[ext]
        data = data_loading_func(input_file)

        for entry in data:
            yield entry


def _check_data_entry_validity(entry):
    if ADDRESS_ID_FIELD not in entry or ADDRESS_FIELD not in entry:
        return False
    else:
        return True


def input_file_entries(input_filename):
    logging.debug("Checking file validity")
    _check_input_file_validity(input_filename)

    logging.debug("Creat[ing] data generator")
    data = _get_data(input_filename)
    logging.debug("Creat[ed] data generator")

    logging.debug("vending data back")
    for i, entry in enumerate(data):
        if _check_data_entry_validity(entry):
            logging.debug(f"Returning '{pprint.pformat(entry)}'")
            yield entry[ADDRESS_ID_FIELD], str(entry[ADDRESS_FIELD])
        else:
            logging.warning(f"I'm not processing entry #{i}: '{pprint.pformat(entry)}'")
            continue


def _check_output_file_validity(output_filename):
    if output_filename == STD_OUT:
        return

    if os.path.exists(output_filename):
        raise RuntimeError(f"I'm sorry, '{output_filename}' *already* seem to exit.")
    elif not any(map(lambda ext: output_filename.endswith(ext), DATA_WRITER_DICT.keys())):
        raise RuntimeError(
            f"I'm sorry, I only know how to handle the following input formats: {', '.join(DATA_WRITER_DICT.keys())}"
        )


def output_data(data, output_filename):
    logging.debug(f"Checking file validity of {output_filename}")
    _check_output_file_validity(output_filename)

    logging.debug("Writ[ing] output data")
    with open(output_filename, "w") as data_file:
        _, ext = os.path.splitext(output_filename)
        data_writer_func = DATA_WRITER_DICT.get(ext, _json_writer)
        logging.debug(f"Writing data: \n{pprint.pformat(data)}\n")
        data_writer_func(data_file, data)


def get_api_key(key_filename):
    with open(key_filename, "r") as key_file:
        key_data = json.load(key_file)

    return key_data[API_KEY]
