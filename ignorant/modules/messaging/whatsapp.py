from ignorant.core import *
from ignorant.localuseragent import *

# WhatsApp registration flow
# Uses the internal v/exist endpoint from WhatsApp Web
# Checks if number is registered without sending anything to target

async def whatsapp(phone, country_code, client, out):
    name = "whatsapp"
    domain = "whatsapp.com"
    method = "register"
    frequent_rate_limit = True  # Meta kills automated checks fast

    headers = {
        "User-Agent": "WhatsApp/2.23.20.0 A",
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://web.whatsapp.com",
        "Referer": "https://web.whatsapp.com/",
    }

    try:
        resp = await client.post(
            "https://v.whatsapp.net/v2/exist",
            headers=headers,
            data={
                "cc": str(country_code),
                "in": str(phone),
                "lg": "en",
                "lc": "US",
                "authkey": "",
                "id": "-1",
                "token": hashlib.md5(
                    f"PdA2DJyKoUrwLw1Bg6EIhzh502dF9noR9uFCSDNt{country_code}{phone}".encode()
                ).hexdigest()
            }
        )

        result = resp.json()
        status = result.get("status", "")

        # "ok" = number exists on WhatsApp
        # "fail" = not registered
        if status == "ok":
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True
            })
        elif status == "fail":
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False
            })
        else:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })

    except Exception:
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False
        })