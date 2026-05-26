from ignorant.core import *
from ignorant.localuseragent import *

# Hinge registration flow
# POST phone to Hinge's API → response differs based on whether
# number is already registered vs new

async def hinge(phone, country_code, client, out):
    name = "hinge"
    domain = "hinge.co"
    method = "login"
    frequent_rate_limit = True

    headers = {
        "User-Agent": "Hinge/9.0.0 (iPhone; iOS 16.0; Scale/3.00)",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-App-Version": "9.0.0",
        "X-Platform": "ios",
    }

    try:
        resp = await client.post(
            "https://prod-api.hingeaws.net/identity/phone",
            headers=headers,
            json={
                "phone": f"+{country_code}{phone}",
                "device_id": ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
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

        # Hinge returns "is_existing_user": true if registered
        # or routes to signup flow if not
        is_existing = (
            result.get("is_existing_user", False) or
            result.get("existing_user", False) or
            "existing" in text
        )

        not_found = (
            "not found" in text or
            "does not exist" in text or
            resp.status_code == 404
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