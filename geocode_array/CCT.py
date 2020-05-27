from geocode_array.ArcGIS import ArcGIS


class CCT(ArcGIS):
    reverse_geocode_url = 'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/reverseGeocode'
    geocode_url = 'https://citymaps.capetown.gov.za/agsext1/rest/services/Here/GC_CoCT/GeocodeServer/findAddressCandidates'
