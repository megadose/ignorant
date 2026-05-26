from ignorant.core import *
from ignorant.localuseragent import *

# Tinder SMS auth flow
# POST phone number to auth/sms/send → response reveals if number is registered
# Does NOT send SMS to target if number isn't registered

async def tinder(phone, country_code, client, out):
    name = "tinder"
    domain = "tinder.com"
    method = "login"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://tinder.com",
        "Referer": "https://tinder.com/",
        "x-auth-token": "",
        "app-version": "1024",
        "platform": "web",
        "tinder-version": "4.7.0",
    }

    try:
        resp = await client.post(
            "https://api.gotinder.com/v2/auth/sms/send?auth_type=sms",
            headers=headers,
            json={
                "phone_number": f"+{country_code}{phone}"
            }
        )

        result = resp.json()
        data = result.get("data", {})
        status = data.get("sms_sent", False)
        otp_length = data.get("otp_length", 0)

        # sms_sent: true = number exists and is registered on Tinder
        # If number not registered, Tinder returns error or sms_sent: false
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

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": status is True
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