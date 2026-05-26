from ignorant.core import *
from ignorant.localuseragent import *

# Discord registration flow
# Submit phone → Discord returns whether number is already in use
# Uses Discord's internal phone number check endpoint

async def discord(phone, country_code, client, out):
    name = "discord"
    domain = "discord.com"
    method = "register"
    frequent_rate_limit = True  # Discord fingerprints hard

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/register",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2MzE2Niwi"
    }

    try:
        resp = await client.post(
            "https://discord.com/api/v9/auth/register",
            headers=headers,
            json={
                "phone": f"+{country_code}{phone}",
                "username": "test",
                "email": "test@test.com",
                "password": "Test1234!",
                "consent": True,
                "date_of_birth": "1998-01-01"
            }
        )
        result = resp.json()

        # If phone is taken, Discord returns errors with "phone" key
        errors = result.get("errors", {})
        phone_errors = errors.get("phone", {})
        codes = [e.get("code", "") for e in phone_errors.get("_errors", [])]
        taken = any(c in ["PHONE_NUMBER_ALREADY_USED", "INVALID_PHONE_NUMBER"] for c in codes)
        # PHONE_NUMBER_ALREADY_USED = exists
        # anything else = not found or rate limited

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

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": "PHONE_NUMBER_ALREADY_USED" in codes
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