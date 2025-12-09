from pprint import pprint

def check_ip_in_portugal(ip):
    import requests
    try:
        # No token used here, but recommended to add your token as ?token=YOUR_TOKEN if needed
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("bogon", True):
                # pprint(f"Bogon IP detected: {ip}")
                return True  # Bogon IPs are treated as local/trusted

            country_code = data.get("country", "").upper()
            region = data.get("region", "").lower()
            # Check country PT and region Lisboa or Lisbon (case insensitive)
            if country_code == "PT" and region in ["lisboa", "lisbon"]:
                return True
    except Exception as e:
        print(f"IP geolocation failed: {e}")
    return False
