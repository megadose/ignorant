from ignorant.core import *
from ignorant.localuseragent import *

# LinkedIn registration flow
# Submit phone to check-phone endpoint
# Returns whether number is linked to an account

async def linkedin(phone, country_code, client, out):
    name = "linkedin"
    domain = "linkedin.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.linkedin.com",
        "Referer": "https://www.linkedin.com/",
        "X-Li-Lang": "en_US",
        "X-Li-Track": '{"clientVersion":"1.13.5765"}',
    }

    try:
        # Step 1: Get CSRF token
        page_resp = await client.get(
            "https://www.linkedin.com/signup/cold-join",
            headers=headers
        )
        csrf = page_resp.cookies.get("JSESSIONID", "").strip('"')

        headers["Csrf-Token"] = csrf

        # Step 2: Check phone
        resp = await client.post(
            "https://www.linkedin.com/signup/check-phone",
            headers=headers,
            data={
                "phone": f"+{country_code}{phone}",
                "csrfToken": csrf
            }
        )

        result = resp.json() if resp.text else {}
        text = str(result).lower()

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

        # "taken" or "already" in response = exists
        exists = (
            "taken" in text or
            "already" in text or
            "registered" in text or
            result.get("phoneExists", False)
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