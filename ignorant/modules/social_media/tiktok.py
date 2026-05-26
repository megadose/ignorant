from ignorant.core import *
from ignorant.localuseragent import *

# TikTok registration flow
# Submit phone to pre-register check endpoint
# Returns whether number is already registered

async def tiktok(phone, country_code, client, out):
    name = "tiktok"
    domain = "tiktok.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.tiktok.com",
        "Referer": "https://www.tiktok.com/",
    }

    try:
        resp = await client.post(
            "https://www.tiktok.com/passport/web/account/check/",
            headers=headers,
            data={
                "mobile": f"+{country_code}{phone}",
                "type": "mobile",
                "aid": "1988",
            }
        )

        result = resp.json()
        data = result.get("data", {})
        err_code = result.get("message", "")

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

        # is_registered: true = account exists
        is_registered = (
            data.get("is_registered", False) or
            data.get("account_sdk_source", "") != "" or
            "registered" in str(result).lower()
        )

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": is_registered
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