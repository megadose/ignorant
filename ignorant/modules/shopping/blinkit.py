from ignorant.core import *
from ignorant.localuseragent import *

# Blinkit (formerly Grofers) login flow
# OTP-first login — phone submission reveals registration status
# Minimal bot protection, clean JSON responses

async def blinkit(phone, country_code, client, out):
    name = "blinkit"
    domain = "blinkit.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://blinkit.com",
        "Referer": "https://blinkit.com/",
        "Access-Control": "no-cors",
        "app_client": "consumer_web",
        "Web-Version": "2024010101",
    }

    try:
        resp = await client.post(
            "https://api.blinkit.com/v1/user/login/",
            headers=headers,
            json={
                "phone": str(phone),
                "country_code": f"+{country_code}",
            }
        )

        result = resp.json()
        message = result.get("message", "").lower()
        success = result.get("success", False)
        error = result.get("error", "").lower()

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

        # success: true or OTP message = registered
        is_existing = (
            success is True or
            "otp" in message or
            "sent" in message or
            result.get("status", 0) == 1
        )

        not_found = (
            "invalid" in message or
            "not found" in message or
            "invalid" in error
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