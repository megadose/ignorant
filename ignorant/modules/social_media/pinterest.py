from ignorant.core import *
from ignorant.localuseragent import *

# Pinterest registration flow
# Submit phone to register endpoint
# Returns whether number is already registered

async def pinterest(phone, country_code, client, out):
    name = "pinterest"
    domain = "pinterest.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.pinterest.com",
        "Referer": "https://www.pinterest.com/",
        "X-Requested-With": "XMLHttpRequest",
        "X-Pinterest-AppState": "active",
    }

    try:
        # Step 1: Get CSRF token
        page_resp = await client.get(
            "https://www.pinterest.com/",
            headers=headers
        )
        csrf = page_resp.cookies.get("csrftoken", "")

        headers["X-CSRFToken"] = csrf

        # Step 2: Submit phone
        resp = await client.post(
            "https://www.pinterest.com/resource/UserPhoneNumberResource/create/",
            headers=headers,
            data={
                "source_url": "/",
                "data": json.dumps({
                    "options": {
                        "phone_number": f"+{country_code}{phone}",
                        "phone_country": str(country_code)
                    },
                    "context": {}
                })
            }
        )

        result = resp.json()
        message = result.get("message", "").lower()
        status = result.get("status", "")
        data = result.get("data", {})

        if resp.status_code == 429:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
            return

        exists = (
            "already" in message or
            "taken" in message or
            "registered" in message or
            status == "failure" and "phone" in message
        )

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": exists
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