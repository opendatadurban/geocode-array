# geocode-array
This code reads in a list of addresses in json or csv format, attempts to geocode these addresses with the ArcGIS and Nominatim geocoders,
compares the results from both geocoders and selects the best. Then it attempts to geocode the addresses with the 
CCT geocoder and returns the output from the CCT geocoder as well as the best result from the combination of ArcGIS and Nominatim
in json and csv format.

## Getting Started

### Installing
* If you have access to the Internet: `pip3 install git+https://github.com/opendatadurban/geocode-array`
* If you don't have to the Internet:
  1. Download the package from [here](https://codeload.github.com/opendatadurban/geocode-array/zip/master)
  2. Unzip, and in the root of the unpacked files: `python3 setup.py install`
  
### Using
* The code now be imported inside Python:
  ```python
  from geocode_array import geocode_array
   
  nom_address = geocode_array.Nominatim("My test address")
  ```
* Or run from the command line script: `$ geocode-array --help`