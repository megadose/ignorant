from ignorant.core import *
from ignorant.localuseragent import *

# Twitter/X registration flow
# Submit phone to registration check endpoint
# Returns whether number is already linked to an account

async def twitter(phone, country_code, client, out):
    name = "twitter"
    domain = "twitter.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
        "Origin": "https://twitter.com",
        "Referer": "https://twitter.com/",
    }

    try:
        # Step 1: Get guest token
        token_resp = await client.post(
            "https://api.twitter.com/1.1/guest/activate.json",
            headers=headers
        )
        guest_token = token_resp.json().get("guest_token")
        if not guest_token:
            raise Exception("No guest token")

        headers["x-guest-token"] = guest_token

        # Step 2: Check phone availability
        resp = await client.get(
            f"https://api.twitter.com/i/users/phone_number_available.json",
            headers=headers,
            params={"phone_number": f"+{country_code}{phone}"}
        )

        result = resp.json()

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

        # valid: false = number is taken = account exists
        # valid: true = number is available = no account
        valid = result.get("valid", True)
        reason = result.get("msg", "").lower()

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": not valid
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