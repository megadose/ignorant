from ignorant.core import *
from ignorant.localuseragent import *

# Zepto login flow
# Phone-first OTP login — clean API, minimal protection
# Response directly indicates if number is registered

async def zepto(phone, country_code, client, out):
    name = "zepto"
    domain = "zeptonow.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.zeptonow.com",
        "Referer": "https://www.zeptonow.com/",
        "requestid": ''.join(random.choices(string.ascii_lowercase + string.digits, k=16)),
    }

    try:
        resp = await client.post(
            "https://api.zeptonow.com/api/v2/user/login/",
            headers=headers,
            json={
                "phone_number": str(phone),
                "country_code": f"+{country_code}",
                "platform": "WEB"
            }
        )

        result = resp.json()
        message = result.get("message", "").lower()
        status = result.get("status", "")
        data = result.get("data", {})

        if resp.status_code == 429 or "rate" in message:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
            return

        is_existing = (
            status == "SUCCESS" or
            data.get("userExists", False) or
            data.get("isRegistered", False) or
            "otp" in message or
            "sent" in message
        )

        not_found = (
            "not found" in message or
            "invalid" in message or
            "not registered" in message or
            status == "USER_NOT_FOUND"
        )

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": is_existing and not not_found
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