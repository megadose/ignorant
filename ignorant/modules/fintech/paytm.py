from ignorant.core import *
from ignorant.localuseragent import *

# PayTM login flow
# PayTM is phone-first — login endpoint directly tells you if number is registered
# Clean JSON response, minimal bot protection

async def paytm(phone, country_code, client, out):
    name = "paytm"
    domain = "paytm.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://paytm.com",
        "Referer": "https://paytm.com/",
        "X-Channel": "web",
        "X-Platform": "web",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        resp = await client.post(
            "https://login.paytm.com/v2/login/init",
            headers=headers,
            json={
                "mobile": str(phone),
                "country_code": str(country_code),
                "client_id": "merchant-panel",
            }
        )

        result = resp.json()
        status = result.get("status", "")
        response_code = result.get("responseCode", "")
        body = result.get("body", {})

        # PayTM returns different flows for existing vs new users
        # existing user → goes to OTP/password flow
        # new user → goes to registration flow
        is_existing = (
            body.get("isExistingUser", False) or
            body.get("userExists", False) or
            response_code in ["SUCCESS", "USER_EXISTS"] or
            "existing" in str(result).lower() or
            "registered" in str(result).lower()
        )

        is_new = (
            body.get("isNewUser", False) or
            response_code == "NEW_USER" or
            "new_user" in str(result).lower()
        )

        if resp.status_code == 429 or "rate" in str(result).lower():
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
            "exists": is_existing and not is_new
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