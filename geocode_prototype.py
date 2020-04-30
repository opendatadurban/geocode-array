# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 18:12:23 2020
use urllib3
@author: heiko
"""

import sys
import json
import urllib3
import certifi
import csv

if len(sys.argv) > 1:  # we can accommodate anything here - they just need to tell us what they want.
    if sys.argv[1] == '--csv':  # python .\geocode_prototype.py --csv
        #
        CSV = True
        JSON = False
    elif sys.argv[1] == '--json':
        JSON = True
        CSV = False

    if len(sys.argv) > 2:  # python .\geocode_prototype.py --csv sample sample_result_2
        input_filename = sys.argv[2]
        output_filename = sys.argv[3]
    else:
        input_filename = 'sample'
        output_filename = 'sample_result'

else:  # currently for debugging, we can pull in final version
    print('default CSV')
    CSV = True
    JSON = False
    input_filename = 'sample_full'
    output_filename = 'sample_result_full'


def ArcGIS(add_ID, Add):
    # ArcGIS
    http = urllib3.PoolManager()
    local = add
    local = local.replace(' ', '%20')
    local = local.replace(',', '')
    request_string = 'http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?singleLine={}&outFields=*&f=pjson'.format(
        local)
    try:
        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")  # extract the data
        result_AG = json.loads(result)
        address_AG = result_AG['candidates'][0]['address']

        # reverse
        lon_AG, lat_AG = result_AG['candidates'][0]['location']['x'], result_AG['candidates'][0]['location']['y']
        request_string = 'http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?f=pjson&featureTypes=&location={}%2C{}'.format(
            lon_AG, lat_AG)

        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")  # extract the data
        reverse_result_AG = json.loads(result)

        local = reverse_result_AG['address']['LongLabel']
        local = local.replace(' ', '%20')
        local = local.replace(',', '')
        request_string = 'http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?singleLine={}&outFields=*&f=pjson'.format(
            local)

        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")  # extract the data
        result_rev2_AG = json.loads(result)

        lon2_AG, lat2_AG = result_rev2_AG['candidates'][0]['location']['x'], \
                           result_rev2_AG['candidates'][0]['location']['y']

        # get distance between points
        d_AG = ((float(lat2_AG) - float(lat_AG)) ** 2 + (float(lon2_AG) - float(lon_AG)) ** 2) ** 0.5
        # print('distance: {}'.format(d_AG))


    except:
        d_AG = 100000
        address_AG = 'None'
        lat_AG = 'NaN'
        lon_AG = 'NaN'

    return address_AG, lat_AG, lon_AG, d_AG


def Nominatim(add_ID, add):
    user_agent = {'user-agent': 'Chrome'}
    http = urllib3.PoolManager(headers=user_agent, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    # Nominatim
    local = add
    local = local.replace(' ', '+')
    local = local.replace(',', '')

    request_string = 'https://nominatim.openstreetmap.org/?addressdetails=1&q={}&format=json&limit=1'.format(local)

    try:
        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")
        result_N = json.loads(result)
        # print(result_N[0]['display_name'])
        address_N = result_N[0]['display_name']

        # reverse
        lat_N, lon_N = result_N[0]['lat'], result_N[0]['lon']
        request_string = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={}&lon={}'.format(lat_N, lon_N)

        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")
        reverse_result_N = json.loads(result)
        # print('reverse: ',reverse_result_N['display_name'])

        local = reverse_result_N['display_name']
        local = local.replace(' ', '+')
        local = local.replace(',', '')

        request_string = 'https://nominatim.openstreetmap.org/?addressdetails=1&q={}&format=json&limit=1'.format(local)

        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")
        result_rev2_N = json.loads(result)
        # print(result_rev2_N[0]['display_name'])
        lat2_N, lon2_N = result_rev2_N[0]['lat'], result_rev2_N[0]['lon']

        # get distance between points
        d_N = ((float(lat2_N) - float(lat_N)) ** 2 + (float(lon2_N) - float(lon_N)) ** 2) ** 0.5
        # print('distance: {}'.format(d_N))

    except:
        d_N = 100000
        address_N = 'None'
        lat_N = 'NaN'
        lon_N = 'NaN'

    return address_N, lat_N, lon_N, d_N


def CCT(add_ID, add):
    user_agent = {'user-agent': 'Chrome'}
    http = urllib3.PoolManager(headers=user_agent, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    local = add
    local = local.replace(' ', '+')
    local = local.replace(',', '')
    addresses = {"records": [{"attributes": {"OBJECTID": add_ID, "SingleLine": local}}]}
    addr = json.dumps(addresses)

    wke = "https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/geocodeAddresses"
    wkid = 4326
    output_format = "json"

    request_string = "{}?addresses={}&outSR={}&f={}".format(wke, addr, wkid, output_format)

    try:
        # print('first')
        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")  # extract the data

        result_cct = json.loads(result)

        # print(result_cct["locations"][0]['address'], result_cct["locations"][0]['location'])
        cct_address = result_cct["locations"][0]['address']
        cct_loc = result_cct["locations"][0]['location']
        cct_lat, cct_lon = result_cct["locations"][0]['location']['y'], result_cct["locations"][0]['location']['x']

        # print(cct_address, cct_lat, cct_lon)
        request_string = (
            'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/reverseGeocode')

        par = str(cct_loc)
        wke2 = 'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/reverseGeocode'
        wkid = 4326
        output_format = "pjson"
        request_string = "{}?location={}&outSR={}&f={}".format(wke2, par, wkid, output_format)
        r = http.request('POST', request_string)
        result = r.data.decode("utf-8")
        reverse_result = json.loads(result)

        local = reverse_result['address']['Match_addr']
        local = local.replace(' ', '+')
        local = local.replace(',', '')
        # print(local)
        addresses = {"records": [{"attributes": {"OBJECTID": add_ID, "SingleLine": local}}]}
        addr = json.dumps(addresses)
        request_string = "{}?addresses={}&outSR={}&f={}".format(wke, addr, wkid, output_format)

        r = http.request('POST', request_string)  # run the request
        result = r.data.decode("utf-8")  # extract the data
        # print(result)
        result_rev2_cct = json.loads(result)
        # print(result_rev2_cct["locations"][0]['address'], result_rev2_cct["locations"][0]['location'])

        cct_lat2, cct_lon2 = result_rev2_cct["locations"][0]['location']['y'], \
                             result_rev2_cct["locations"][0]['location']['x']

        # get distance between points
        d_cct = ((float(cct_lat2) - float(cct_lat)) ** 2 + (float(cct_lon2) - float(cct_lon)) ** 2) ** 0.5
        # print('distance: {}'.format(d_cct))
        # print(d_cct)
        cct_error = d_cct

    except:
        # print("address {} failed".format(add))
        cct_address = 'NaN'
        cct_loc = 'NaN'
        cct_error = 'NaN'

    return cct_address, cct_loc, cct_error


def compare(address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_I, add):
    # select best option  
    try:
        if d_AG == d_N:
            option = "go with either"
            if "cape town" in address_AG.lower():
                lat = lat_AG
                lon = lon_AG
                error = d_AG
                address_name = address_AG
            elif "cape town" in address_N.lower():
                lat = lat_N
                lon = lon_N
                error = d_N
                address_name = address_N
            else:
                option = 'neither one worked'
                lat = 'NaN'
                lon = 'NaN'
                address_name = add
                error = 'NaN'

        if d_AG > d_N:
            if "cape town" in address_N.lower():
                option = "go with Nominatim"
                lat = lat_N
                lon = lon_N
                error = d_N
                address_name = address_N
            elif "cape town" in address_AG.lower():
                lat = lat_AG
                lon = lon_AG
                error = d_AG
                address_name = address_AG
            else:
                option = 'neither one worked'
                lat = 'NaN'
                lon = 'NaN'
                address_name = add
                error = 'NaN'

        if d_AG < d_N:
            if "cape town" in address_AG.lower():
                lat = lat_AG
                lon = lon_AG
                error = d_AG
                address_name = address_AG
            elif "cape town" in address_N.lower():
                lat = lat_N
                lon = lon_N
                error = d_N
                address_name = address_N
            else:
                option = 'neither one worked'
                lat = 'NaN'
                lon = 'NaN'
                address_name = add
                error = 'NaN'

        print("address ID: {}, address: {}, lat: {}, lon: {}, error: {}, option: {}".format(add_ID, address_name, lat,
                                                                                            lon, error, option))
    except:
        print('did not work on address ID: {}'.format(add_ID))
        lat = 'NaN'
        lon = 'NaN'
        address_name = 'NaN'
        error = 'NaN'
    return lat, lon, address_name, error


if __name__ == "__main__":

    if JSON:
        # Opening JSON file
        loadname = input_filename + '.json'
        with open(loadname, 'r') as openfile:

            # Reading from json file
            data_j = json.load(openfile)

        address_id = []
        address = []
        for i in range(len(data_j)):
            address_id.append(data_j[str(i)]['Address_ID'])
            address.append(data_j[str(i)]['Address_Cleaned'])

    if CSV:
        loadname = input_filename + '.csv'
        with open(loadname, mode='r') as csv_file:
            # csv_reader = csv.DictReader(csv_file)
            csv_reader = csv.reader(csv_file)
            address_id = []
            address = []
            for row in csv_reader:
                address_id.append(row[0])
                address.append(row[1])

        address_id = address_id[1:]
        address_id = [int(x) for x in address_id]
        address = address[1:]
    # %%
    for i in range(len(address)):
        if "cape town" not in address[i].lower():
            address[i] = address[i] + ', Cape Town'
        if 'south africa' not in address[i].lower():
            address[i] = address[i] + ', South Africa'
    # %%
    inputs = zip(address_id, address)
    lats = []
    lons = []
    addresses = []
    errors = []
    cct_addresses = []
    cct_lats = []
    cct_lons = []
    cct_errors = []

    for add_ID, add in inputs:

        address_AG, lat_AG, lon_AG, d_AG = ArcGIS(add_ID, add)
        address_N, lat_N, lon_N, d_N = Nominatim(add_ID, add)
        lat, lon, address_name, error = compare(address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_ID,
                                                add)
        lats.append(lat)
        lons.append(lon)
        addresses.append(address_name)
        errors.append(error)

        cct_address, cct_loc, cct_error = CCT(add_ID, add)
        cct_addresses.append(cct_address)
        try:
            cct_lats.append(cct_loc['y'])
            cct_lons.append(cct_loc['x'])
        except:
            cct_lats.append('NaN')
            cct_lons.append('NaN')
        cct_errors.append(cct_error)
        print('address: {}, location: {}'.format(cct_address, cct_loc))

    # make a dictionary

    result = {}

    for i in range(len(address_id)):
        if addresses[i] == 'NaN':
            addresses[i] = address[i]
        addresses[i] = addresses[i].replace(',', '')
        cct_addresses[i] = cct_addresses[i].replace(',', '')
        # if error statement here resulting in a True or False 
        TF = False
        result[address_id[i]] = {'result': {'esri_global': {'address': addresses[i],
                                                            'lat': float(lats[i]),
                                                            'lon': float(lons[i]),
                                                            'error': float(errors[i])},
                                            'cct_geocoder': {'address': cct_addresses[i],
                                                             'lat': float(cct_lats[i]),
                                                             'lon': float(cct_lons[i]),
                                                             'error': float(cct_errors[i])},
                                            'error': TF}}

        print(result[i])
    savename = output_filename + '.json'
    with open(savename, "w") as outfile:
        json.dump(result, outfile)
        # test
    test = False
    if test:
        with open(savename, 'r') as openfile:

            # Reading from json file 
            result_2 = json.load(openfile)

        for i in range(len(result_2)):
            print(result_2[str(i)])

    # %% write as csv

    fields = ['Address_ID', 'Address', 'Lat', 'Lon', 'Error', 'CCT_Address', 'CCT_Lat', 'CCT_Lon', 'CCT_Error',
              'Overall_Error']
    # writing to csv file  
    savename = output_filename + '.csv'
    with open(savename, 'w') as csvfile:
        # creating a csv writer object  
        csvwriter = csv.writer(csvfile, lineterminator='\n')

        # writing the fields  
        csvwriter.writerow(fields)
        for i in range(len(address_id)):
            if addresses[i] == 'NaN':
                addresses[i] = address[i]
            addresses[i] = addresses[i].replace(',', '')
            cct_addresses[i] = cct_addresses[i].replace(',', '')
            # if error statement here resulting in a True or False 
            TF = False
            row = [address_id[i], addresses[i], lats[i], lons[i], errors[i], cct_addresses[i], cct_lats[i], cct_lons[i],
                   cct_errors[i], TF]
            # writing the data rows  
            csvwriter.writerow(row)
