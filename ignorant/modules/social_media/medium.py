from ignorant.core import *
from ignorant.localuseragent import *

# Medium login flow
# Medium supports phone login via SMS
# Submit phone → response reveals if account exists

async def medium(phone, country_code, client, out):
    name = "medium"
    domain = "medium.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://medium.com",
        "Referer": "https://medium.com/",
        "X-Obvious-CID": "web",
        "X-Client-Date": str(int(time.time() * 1000)),
    }

    try:
        resp = await client.post(
            "https://medium.com/_/api/users/phone/request-otp",
            headers=headers,
            json={
                "phone": f"+{country_code}{phone}",
            }
        )

        result = resp.json()
        success = result.get("success", False)
        error = result.get("error", {})
        error_code = error.get("code", "") if isinstance(error, dict) else ""
        message = str(result).lower()

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

        # success: true = OTP sent = number is registered
        # error with "not found" = no account
        not_found = (
            "not found" in message or
            "no account" in message or
            error_code in ["NOT_FOUND", "USER_NOT_FOUND"]
        )

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": success and not not_found
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