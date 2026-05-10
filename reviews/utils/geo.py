from django.contrib.gis.geoip2 import GeoIP2

g = GeoIP2()

def get_country_code(ip_address):
    try:
        result = g.country(ip_address)
        return result["country_code"]
    except Exception:
        return "GB"