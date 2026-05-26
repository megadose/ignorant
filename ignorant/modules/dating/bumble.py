from ignorant.core import *
from ignorant.localuseragent import *

# Bumble registration flow
# POST phone to Bumble's internal API → returns whether number is registered
# Bumble uses a token-based request system

async def bumble(phone, country_code, client, out):
    name = "bumble"
    domain = "bumble.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://bumble.com",
        "Referer": "https://bumble.com/",
        "X-Pingback": "1",
    }

    try:
        # Step 1: Get session token from homepage
        page_resp = await client.get("https://bumble.com/en/register", headers=headers)
        
        token = ""
        body = BeautifulSoup(page_resp.text, "html.parser")
        for script in body.find_all("script"):
            if script.string and "serverToken" in str(script.string):
                match = re.search(r'"serverToken"\s*:\s*"([^"]+)"', script.string)
                if match:
                    token = match.group(1)
                    break

        # Step 2: Submit phone number
        resp = await client.post(
            "https://bumble.com/api/users/phone",
            headers={
                **headers,
                "X-Token": token
            },
            json={
                "phone_number": f"+{country_code}{phone}",
                "country_code": str(country_code)
            }
        )

        result = resp.json()
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

        # "already registered" / "phone_exists" = exists
        exists = (
            "already" in text or
            "exists" in text or
            "registered" in text or
            result.get("result", {}).get("is_registered", False)
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