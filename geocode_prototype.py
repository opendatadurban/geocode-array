# -*- coding: utf-8 -*-
"""
CCT Geocode Project:
This code reads in a list of addresses in json or csv format, attempts to geocode these addresses with the ArcGIS and Nominatim geocoders,
compares the results from both geocoders and selects the best. Then it attempts to geocode the addresses with the 
CCT geocoder and returns the output from the CCT geocoder as well as the best result from the combination of ArcGIS and Nominatim
in json and csv format.
"""

import sys
import json
import urllib
import urllib.request 
import argparse
import csv


def Google(add_ID, addr, API_Key):
    '''
    Parameters: add_ID (Address ID) , addr (Address) 
    Step 1: Uses Google geocoder to find address co-ordinates. 
    Step 2: Reverse geocodes to find address.
    Step 3: Geocodes reverse geocoded address to find new co-ordinates.
    Step 4: Calculates distance between both sets of co-ordinates to be used as measure of error.
    Returns: address_G (address from step 1), lat_G (latitude from step 1), lon_G (longitude from step 1), d_G (distance from step 4)
    '''
    try:
        values = {"address": addr,
                  "key":API_key}
        
        request_string = 'https://maps.googleapis.com/maps/api/geocode/json?{}'.format(urllib.parse.urlencode(values))
        
        req = urllib.request.Request(
            request_string,
            headers={
                'User-Agent': 'Chrome'
            }
        )
        r = urllib.request.urlopen(req)
        code = r.getcode()
        if code == 200:
            result_G = json.loads(r.read().decode('utf-8'))
        else:
            print('Got incorrect code: {}'.format(code))
            result_G = []
        address_G = result_G['results'][0]['formatted_address']
                
        # reverse
        lat_G, lon_G = result_G['results'][0]['geometry']['location']['lat'], result_G['results'][0]['geometry']['location']['lng']
              
        values = {"latlng": '{},{}'.format(lat_G,lon_G),
                "key":API_key}
        
        request_string = 'https://maps.googleapis.com/maps/api/geocode/json?{}'.format(urllib.parse.urlencode(values))
        req = urllib.request.Request(
            request_string,
            headers={
                'User-Agent': 'Chrome'
            }
        )
        r = urllib.request.urlopen(req)
        code = r.getcode()
        if code == 200:
            reverse_result_G = json.loads(r.read().decode('utf-8'))
        else:
            print('Got incorrect code: {}'.format(code))
            reverse_result_G = []
        
        local = reverse_result_G['results'][0]['formatted_address']
        
        values = {"address": local,
                  "key":API_key}
        
        request_string = 'https://maps.googleapis.com/maps/api/geocode/json?{}'.format(urllib.parse.urlencode(values))
        
        req = urllib.request.Request(
            request_string,
            headers={
                'User-Agent': 'Chrome'
            }
        )
        r = urllib.request.urlopen(req)
        code = r.getcode()
        if code == 200:
            result_rev2_G = json.loads(r.read().decode('utf-8'))
        else:
            print('Got incorrect code: {}'.format(code))
            result_rev2_G = []
       
        # reverse
        lat2_G, lon2_G = result_rev2_G['results'][0]['geometry']['location']['lat'], result_rev2_G['results'][0]['geometry']['location']['lng']
       
        # get distance between points
        d_G = ((float(lat2_G) - float(lat_G)) ** 2 + (float(lon2_G) - float(lon_G)) ** 2) ** 0.5
        
    except:
        d_G = 100000
        address_G = None
        lat_G = 'NaN'
        lon_G = 'NaN'
        
    return address_G, lat_G, lon_G, d_G


def ArcGIS(add_ID, addr):
    '''
    Parameters: add_ID (Address ID) , addr (Address) 
    Step 1: Uses ArcGIS geocoder to find address co-ordinates. 
    Step 2: Reverse geocodes to find address.
    Step 3: Geocodes reverse geocoded address to find new co-ordinates.
    Step 4: Calculates distance between both sets of co-ordinates to be used as measure of error.
    Returns: address_AG (address from step 1), lat_AG (latitude from step 1), lon_AG (longitude from step 1), d_AG (distance from step 4)
    '''
    try:
        request_string = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?'
        values = {"singleLine": addr,
                  "outSR": 4326, 
                  "f":"json"}
        req = urllib.request.Request(
            request_string,
            data=urllib.parse.urlencode(values).encode("utf-8"), 
            headers={
                'User-Agent': 'Chrome'
            }
        )
        f = urllib.request.urlopen(req)
        code = f.getcode()
        if code == 200:
            result_AG = json.loads(f.read().decode('utf-8'))
        else:
            result_AG = []
            print('Got incorrect code: {}'.format(code))
        
        
        address_AG = result_AG['candidates'][0]['address']
        
        # reverse
        lon_AG, lat_AG = result_AG['candidates'][0]['location']['x'], result_AG['candidates'][0]['location']['y']
        request_string = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode?'
        values = {"location": '{},{}'.format(lon_AG,lat_AG),
                  "outSR": 4326, 
                  "f":"pjson"}
        req = urllib.request.Request(
            request_string,
            data=urllib.parse.urlencode(values).encode("utf-8"), 
            headers={
                'User-Agent': 'Chrome'
            }
        )
        f = urllib.request.urlopen(req)
        code = f.getcode()
        if code == 200:
            reverse_result_AG = json.loads(f.read().decode('utf-8'))
        else:
            reverse_result_AG = []
            print('Got incorrect code: {}'.format(code))
        
        request_string = 'https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?'
        values = {"singleLine": reverse_result_AG['address']['LongLabel'],
                  "outSR": 4326, 
                  "f":"json"}
        req = urllib.request.Request(
            request_string,
            data=urllib.parse.urlencode(values).encode("utf-8"), 
            headers={
                'User-Agent': 'Chrome'
            }
        )
        f = urllib.request.urlopen(req)
        code = f.getcode()
        if code == 200:
            result_rev2_AG = json.loads(f.read().decode('utf-8'))
        else:
            result_rev2_AG = []
            print('Got incorrect code: {}'.format(code))
        
        lon2_AG, lat2_AG = result_rev2_AG['candidates'][0]['location']['x'], \
            result_rev2_AG['candidates'][0]['location']['y']
    
        # get distance between points
        d_AG = ((float(lat2_AG) - float(lat_AG)) ** 2 + (float(lon2_AG) - float(lon_AG)) ** 2) ** 0.5
        # print('distance: {}'.format(d_AG))
        
    except:
        d_AG = 100000
        address_AG = None
        lat_AG = 'NaN'
        lon_AG = 'NaN'

    return address_AG, lat_AG, lon_AG, d_AG


def Nominatim(add_ID, addr):
    '''
    Parameters: add_ID (Address ID) , addr (Address) 
    Step 1: Uses Nominatim geocoder to find address co-ordinates. 
    Step 2: Reverse geocodes to find address.
    Step 3: Geocodes reverse geocoded address to find new co-ordinates.
    Step 4: Calculates distance between both sets of co-ordinates to be used as measure of error.
    Returns: address_N (address from step 1), lat_N (latitude from step 1), lon_N (longitude from step 1), d_N (distance from step 4)
    '''

    try:
        values = {"q":addr}
        request_string = 'https://nominatim.openstreetmap.org/?addressdetails=1&format=json&limit=1&{}'.format(urllib.parse.urlencode(values))
        req = urllib.request.Request(
            request_string, 
            headers={'User-Agent': 'Chrome'}
        )
        f = urllib.request.urlopen(req)
        
        code = f.getcode()
        if code == 200:
            result_N = json.loads(f.read().decode('utf-8'))
        else:
            result_N = []
            print('Got incorrect code: {}'.format(code))
        
        address_N = result_N[0]['display_name']       
    
        # reverse
        lat_N, lon_N = result_N[0]['lat'], result_N[0]['lon']
        request_string = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={}&lon={}'.format(lat_N, lon_N)
    
        req = urllib.request.Request(
            request_string, 
            headers={'User-Agent': 'Chrome'}
        )
        f = urllib.request.urlopen(req)
        
        code = f.getcode()
        if code == 200:
            reverse_result_N = json.loads(f.read().decode('utf-8'))
        else:
            reverse_result_N = []
            print('Got incorrect code: {}'.format(code))
        
        #print('reverse: ',reverse_result_N['display_name'])
    
        local = reverse_result_N['display_name']
        values = {"q":local}
        request_string = 'https://nominatim.openstreetmap.org/?addressdetails=1&format=json&limit=1&{}'.format(urllib.parse.urlencode(values))
        req = urllib.request.Request(
            request_string, 
            headers={'User-Agent': 'Chrome'}
        )
        f = urllib.request.urlopen(req)
        
        code = f.getcode()
        if code == 200:
            result_rev2_N = json.loads(f.read().decode('utf-8'))
        else:
            result_rev2_N = []
            print('Got incorrect code: {}'.format(code))
        
        lat2_N, lon2_N = result_rev2_N[0]['lat'], result_rev2_N[0]['lon']
    
        # get distance between points
        d_N = ((float(lat2_N) - float(lat_N)) ** 2 + (float(lon2_N) - float(lon_N)) ** 2) ** 0.5
        # print('distance: {}'.format(d_N))
    except:
        d_N = 100000
        address_N = None
        lat_N = 'NaN'
        lon_N = 'NaN'

    return address_N, lat_N, lon_N, d_N


def CCT(add_ID, addr):
    '''
    Parameters: add_ID (Address ID) , addr (Address) 
    Step 1: Uses CCT geocoder to find address co-ordinates. 
    Step 2: Reverse geocodes to find address.
    Step 3: Geocodes reverse geocoded address to find new co-ordinates.
    Step 4: Calculates distance between both sets of co-ordinates to be used as measure of error.
    Returns: cct_address (address from step 1), cct_loc (latitude and longitude from step 1), cct_error (distance from step 4)
    '''
    
    try:
        request_string = 'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/geocodeAddresses'
        values = {"addresses": {"records": [{"attributes": {"OBJECTID": add_ID, "SingleLine": addr}}]},
                  "outSR": 4326, 
                  "f":"json"}    
        req = urllib.request.Request(request_string,
                                     data=urllib.parse.urlencode(values).encode("utf-8"), 
                                     headers={'User-Agent': 'Chrome'})
        r = urllib.request.urlopen(req)
        code = r.getcode()
        if code == 200:
            result_cct = json.loads(r.read().decode('utf-8'))
        else:
            print('Got incorrect code: {}'.format(code))
            result_cct = []
        # print(result_cct["locations"][0]['address'], result_cct["locations"][0]['location'])
        cct_address = result_cct["locations"][0]['address']
            
        cct_loc = result_cct["locations"][0]['location']
        cct_lat, cct_lon = result_cct["locations"][0]['location']['y'], result_cct["locations"][0]['location']['x']
        
        # print(cct_address, cct_lat, cct_lon)
        
        request_string = 'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/reverseGeocode'
        values = {"location": str(cct_loc),
                  "outSR": 4326, 
                  "f":"pjson"}  
          
        req = urllib.request.Request(request_string,
                                     data=urllib.parse.urlencode(values).encode("utf-8"), 
                                     headers={'User-Agent': 'Chrome'})
        r = urllib.request.urlopen(req)
        code = r.getcode()
        if code == 200:
            reverse_result = json.loads(r.read().decode('utf-8'))
        else:
            print('Got incorrect code: {}'.format(code))
            reverse_result = []
            
        #print(reverse_result['address']['Match_addr'])
        reverse_addr = reverse_result['address']['Match_addr']
        
        request_string = 'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/geocodeAddresses'
        values = {"addresses": {"records": [{"attributes": {"OBJECTID": add_ID, "SingleLine": reverse_addr}}]},
                  "outSR": 4326, 
                  "f":"json"}    
        req = urllib.request.Request(request_string,
                                     data=urllib.parse.urlencode(values).encode("utf-8"), 
                                     headers={'User-Agent': 'Chrome'})
        r = urllib.request.urlopen(req)
        
        code = r.getcode()
        if code == 200:
            result_rev2_cct = json.loads(r.read().decode('utf-8'))
        else:
            print('Got incorrect code: {}'.format(code))
            result_rev2_cct = []
        
        # print(result_rev2_cct["locations"][0]['address'], result_rev2_cct["locations"][0]['location'])
    
        cct_lat2, cct_lon2 = result_rev2_cct["locations"][0]['location']['y'], result_rev2_cct["locations"][0]['location']['x']
    
        # get distance between points
        d_cct = ((float(cct_lat2) - float(cct_lat)) ** 2 + (float(cct_lon2) - float(cct_lon)) ** 2) ** 0.5
        # print('distance: {}'.format(d_cct))
        # print(d_cct)
        cct_error = d_cct

    except:
        # print("address {} failed".format(add))
        cct_address = None
        cct_loc = 'NaN'
        cct_error = 'NaN'

    return cct_address, cct_loc, cct_error


def compare(address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_I, addr):
    # select best option  
    '''
    Compares outputs from ArcGIS and Nominatim and returns the most accurate result
    '''
    try:
        if d_AG == d_N:
            #option = "go with either"
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
                #option = 'neither one worked'
                lat = 'NaN'
                lon = 'NaN'
                address_name = addr
                error = 'NaN'

        if d_AG > d_N:
            if "cape town" in address_N.lower():
                #option = "go with Nominatim"
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
                #option = 'neither one worked'
                lat = 'NaN'
                lon = 'NaN'
                address_name = addr
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
                #option = 'neither one worked'
                lat = 'NaN'
                lon = 'NaN'
                address_name = addr
                error = 'NaN'

        #print("address ID: {}, address: {}, lat: {}, lon: {}, error: {}, option: {}".format(add_ID, address_name, lat, lon, error, option))
    except:
        print('did not work on address ID: {}'.format(add_ID))
        lat = 'NaN'
        lon = 'NaN'
        address_name = None
        error = 'NaN'
    return lat, lon, address_name, error

def compare_all(address_G, lat_G, lon_G, d_G, address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_ID,addr):
    try:
        dist = [d_G, d_AG, d_N]
        if d_G == 0.0 and "cape town" in address_G.lower():
            print('use google')
            lat = lat_G
            lon = lon_G
            address_name = address_G
            error = d_G
            
        elif d_AG == 0.0 and "cape town" in address_AG.lower():
            print('use ArcGIS')
            lat = lat_AG
            lon = lon_AG
            address_name = address_AG
            error = d_AG
            
        elif d_N == 0.0 and "cape town" in address_N.lower():
            print('use Nominatim')
            lat = lat_N
            lon = lon_N
            address_name = address_N
            error = d_N
            
        elif d_G == min(dist) and "cape town" in address_G.lower():
            print('use google because min dist')
            lat = lat_G
            lon = lon_G
            address_name = address_G
            error = d_G
            
        elif d_AG == min(dist) and "cape town" in address_AG.lower():
            print('use ArcGIS because min dist')
            lat = lat_AG
            lon = lon_AG
            address_name = address_AG
            error = d_AG
            
        elif d_N == min(dist) and "cape town" in address_N.lower():
            print('use Nominatim because min dist')
            lat = lat_N
            lon = lon_N
            address_name = address_N
            error = d_N
            
        else:
            print('did not work on address ID: {}'.format(add_ID))
            lat = 'NaN'
            lon = 'NaN'
            address_name = None
            error = 'NaN'
            
    except:
        print('did not work on address ID: {}'.format(add_ID))
        lat = 'NaN'
        lon = 'NaN'
        address_name = None
        error = 'NaN'
        
    return lat, lon, address_name, error


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="geocode using ArcGIS, Nominatim, and CCT geocoder. Example: >>python .\geocode_prototype.py csv sample sample_result None")
    parser.add_argument("input_filename_type", type=str, help="input file type. Options: csv, json")
    parser.add_argument("input_filename", type=str, help="input filename eg: sample")
    parser.add_argument("output_filename", type=str, help="output filename eg: sample")
    parser.add_argument("API_key", type=str, help="your Google API Key")
    args = parser.parse_args()


    if args.input_filename_type.lower() == 'csv':
        CSV = True
        JSON = False
    elif args.input_filename_type.lower() == 'json':
        JSON = True
        CSV = False
    input_filename = args.input_filename
    output_filename = args.output_filename
    API_key = args.API_key
    if API_key == 'None':
        API_key = None
        
    print('using Google API key: {}'.format(API_key))

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

    for add_ID, addr in inputs:
        address_AG, lat_AG, lon_AG, d_AG = ArcGIS(add_ID, addr)
        address_N, lat_N, lon_N, d_N = Nominatim(add_ID, addr)
        if API_key != None:
            try:
                print("API key detected")
                address_G, lat_G, lon_G, d_G = Google(add_ID, addr, API_key)
                lat, lon, address_name, error = compare_all(address_G, lat_G, lon_G, d_G, address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_ID,addr)
            except:
                print('Possible invalid API key')
                lat, lon, address_name, error = compare(address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_ID,
                                                addr)
        else:
            print("no API key detected")
            lat, lon, address_name, error = compare(address_AG, lat_AG, lon_AG, d_AG, address_N, lat_N, lon_N, d_N, add_ID,addr)
        lats.append(lat)
        lons.append(lon)
        addresses.append(address_name)
        errors.append(error)

        cct_address, cct_loc, cct_error = CCT(add_ID, addr)
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
        if addresses[i] == None:
            addresses[i] = address[i]
        addresses[i] = addresses[i].replace(',', '')
        if cct_addresses[i] != None:
            cct_addresses[i] = cct_addresses[i].replace(',', '')

        result[address_id[i]] = {'result': {'esri_global': {'address': addresses[i],
                                                            'lat': float(lats[i]),
                                                            'lon': float(lons[i]),
                                                            'error': float(errors[i])},
                                            'cct_geocoder': {'address': cct_addresses[i],
                                                             'lat': float(cct_lats[i]),
                                                             'lon': float(cct_lons[i]),
                                                             'error': float(cct_errors[i])}
                                            }}

        print(result[i])
    savename = output_filename + '.json'
    with open(savename, "w") as outfile:
        json.dump(result, outfile)

    # %% write as csv

    fields = ['Address_ID', 'Address', 'Lat', 'Lon', 'Error', 'CCT_Address', 'CCT_Lat', 'CCT_Lon', 'CCT_Error']
    # writing to csv file  
    savename = output_filename + '.csv'
    with open(savename, 'w') as csvfile:
        # creating a csv writer object  
        csvwriter = csv.writer(csvfile, lineterminator='\n')

        # writing the fields  
        csvwriter.writerow(fields)
        for i in range(len(address_id)):
            row = [address_id[i], addresses[i], lats[i], lons[i], errors[i], cct_addresses[i], cct_lats[i], cct_lons[i],
                   cct_errors[i]]
            # writing the data rows  
            csvwriter.writerow(row)
