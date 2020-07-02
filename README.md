# geocode-array
This code reads in a list of addresses in json or csv format, attempts to geocode these addresses with the ArcGIS and Nominatim geocoders,
compares the results from both geocoders and selects the best. Then it attempts to geocode the addresses with the 
CCT geocoder and returns the output from the CCT geocoder as well as the best result from the combination of ArcGIS and Nominatim in json and csv format.

## Getting Started

### Installing
* If you have access to the Internet (and have git installeed): `pip3 install git+https://github.com/cityofcapetown/geocode-array`
* If you don't have access to the Internet (or Git):
  1. Download the package from [here](https://codeload.github.com/cityofcapetown/geocode-array/zip/master)
  2. Unzip, and in the root of the unpacked files: `python3 setup.py install`
  
### Using
#### The Library
* The code now be imported inside Python:
  ```python
  from geocode_array.Nominatim import Nominatim
   
  nom = Nominatim() 
  nom_address = nom.geocode("My test address")
  ```

#### Command Line Script
The package also comes with a command line script that does some of the heavy lifting for ensemble geocoding.

* Linux/MacOS: run from the command line script: `$ geocode-array --help`
* Windows: in the root directory of the repository, run `$ python bin\geocode-array --help`
