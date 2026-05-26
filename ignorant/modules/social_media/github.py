from ignorant.core import *
from ignorant.localuseragent import *

# GitHub signup flow
# GitHub doesn't use phone as primary ID but links it for 2FA
# We check via the signup validation endpoint

async def github(phone, country_code, client, out):
    name = "github"
    domain = "github.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://github.com",
        "Referer": "https://github.com/signup",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        # Step 1: Get signup page tokens
        page_resp = await client.get(
            "https://github.com/signup",
            headers=headers
        )
        body = BeautifulSoup(page_resp.text, "html.parser")

        token = ""
        token_input = body.find("input", {"name": "authenticity_token"})
        if token_input:
            token = token_input.get("value", "")

        # Step 2: Hit phone verification endpoint
        resp = await client.post(
            "https://github.com/users/phone_verification",
            headers={
                **headers,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRF-Token": token
            },
            data={
                "phone_number": f"+{country_code}{phone}",
                "authenticity_token": token
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

        # "already in use" or "taken" = exists
        exists = (
            "already" in text or
            "taken" in text or
            "in use" in text or
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