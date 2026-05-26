from ignorant.core import *
from ignorant.localuseragent import *

# Reddit registration flow
# Submit phone → checks if number is already registered
# Uses Reddit's internal register endpoint

async def reddit(phone, country_code, client, out):
    name = "reddit"
    domain = "reddit.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.reddit.com",
        "Referer": "https://www.reddit.com/register",
    }

    try:
        # Step 1: Get CSRF token
        page_resp = await client.get(
            "https://www.reddit.com/register",
            headers=headers
        )
        csrf = page_resp.cookies.get("csrf_token") or ""

        # Step 2: Submit phone to check existence
        data = {
            "phone_number": f"+{country_code}{phone}",
            "csrf_token": csrf
        }

        resp = await client.post(
            "https://www.reddit.com/register/phone-number.json",
            headers=headers,
            data=data
        )
        result = resp.json()

        # "PHONE_NUMBER_TAKEN" → exists
        # "OK" → not registered
        status = result.get("status", "")
        errors = result.get("errors", [])
        taken = status == "PHONE_NUMBER_TAKEN" or any(
            "taken" in str(e).lower() or "already" in str(e).lower()
            for e in errors
        )

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": taken
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