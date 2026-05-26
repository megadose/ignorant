from ignorant.core import *
from ignorant.localuseragent import *

# Viber registration flow
# POST to Viber's account check endpoint
# Returns whether number has a Viber account

async def viber(phone, country_code, client, out):
    name = "viber"
    domain = "viber.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://account.viber.com",
        "Referer": "https://account.viber.com/",
    }

    try:
        resp = await client.post(
            "https://account.viber.com/api/v3/send-otp",
            headers=headers,
            json={
                "phone_number": f"+{country_code}{phone}",
                "channel": "sms"
            }
        )

        result = resp.json()
        status = result.get("status", "")
        error = result.get("error", {})
        error_code = error.get("code", "") if isinstance(error, dict) else ""

        # status 0 or "ok" = number exists, OTP sent
        # error code for invalid/unregistered varies
        if resp.status_code == 200 and (status == 0 or status == "ok"):
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True
            })
        elif "invalid" in str(result).lower() or "not found" in str(result).lower():
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