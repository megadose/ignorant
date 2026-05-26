from ignorant.core import *
from ignorant.localuseragent import *

# Flipkart login flow
# Phone-first login — endpoint returns whether number is registered
# Clean JSON API, low bot protection

async def flipkart(phone, country_code, client, out):
    name = "flipkart"
    domain = "flipkart.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.flipkart.com",
        "Referer": "https://www.flipkart.com/",
        "X-User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 FKUA/5.0.32/5.0.32/Website:Windows:Web",
    }

    try:
        # Step 1: Get request context token
        page_resp = await client.get(
            "https://www.flipkart.com/",
            headers=headers
        )
        csrf = page_resp.cookies.get("csrf_token", "")

        # Step 2: Submit phone number to login endpoint
        resp = await client.post(
            "https://www.flipkart.com/api/3/user/otp/generate",
            headers={
                **headers,
                "X-Csrf-Token": csrf,
            },
            json={
                "loginId": f"+{country_code}{phone}",
                "type": "mobileno"
            }
        )

        result = resp.json()
        status = result.get("RESPONSE", {}).get("status", "")
        error = result.get("RESPONSE", {}).get("errorMessage", "").lower()
        code = result.get("RESPONSE", {}).get("code", "")

        if resp.status_code == 429 or "rate" in error:
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
            return

        # OTP sent = number registered
        # "invalid mobile" or "not registered" = doesn't exist
        is_existing = (
            status == "SUCCESS" or
            code in ["OTP_SENT", "USER_EXISTS"] or
            "otp" in str(result).lower()
        )

        not_found = (
            "invalid" in error or
            "not registered" in error or
            "no account" in error or
            code == "INVALID_MOBILE"
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