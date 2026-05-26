from ignorant.core import *
from ignorant.localuseragent import *

# Telegram uses the official MTProto API via the web client endpoint
# auth.sendCode → tells us if number is registered without alerting target
# api_id and api_hash are from the official Telegram web app (public)

async def telegram(phone, country_code, client, out):
    name = "telegram"
    domain = "telegram.org"
    method = "other"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://web.telegram.org",
        "Referer": "https://web.telegram.org/",
    }

    try:
        resp = await client.post(
            "https://my.telegram.org/auth/send_password",
            headers=headers,
            data={"phone": f"+{country_code}{phone}"}
        )

        result = resp.json()
        text = str(result).lower()

        # "random_hash" in response = number exists and is registered
        # "error" with "invalid phone" = not registered
        if "random_hash" in result:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": True
            })
        elif "error" in text and ("invalid" in text or "not registered" in text):
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": False
            })
        else:
            # flood wait or unknown response
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