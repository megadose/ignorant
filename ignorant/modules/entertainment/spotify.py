from ignorant.core import *
from ignorant.localuseragent import *

# Spotify password reset flow
# Submit phone → Spotify returns whether number has an account
# Also leaks masked email in some regions

async def spotify(phone, country_code, client, out):
    name = "spotify"
    domain = "spotify.com"
    method = "password_reset"
    frequent_rate_limit = False
    email_recovery = None

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://accounts.spotify.com",
        "Referer": "https://accounts.spotify.com/en/password-reset",
    }

    try:
        # Step 1: Get CSRF token
        page_resp = await client.get(
            "https://accounts.spotify.com/en/password-reset",
            headers=headers
        )
        body = BeautifulSoup(page_resp.text, "html.parser")

        csrf_token = None
        csrf_input = body.find("input", {"name": "csrf_token"})
        if csrf_input:
            csrf_token = csrf_input.get("value")
        if not csrf_token:
            csrf_token = page_resp.cookies.get("csrf_token", "")

        # Step 2: Submit phone number
        data = {
            "username": f"+{country_code}{phone}",
            "csrf_token": csrf_token or ""
        }

        reset_resp = await client.post(
            "https://accounts.spotify.com/en/password-reset",
            headers=headers,
            data=data
        )

        # Step 3: Parse response
        try:
            result = reset_resp.json()
            if not result.get("error", True):
                email_recovery = result.get("email")
                out.append({
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True,
                    "emailrecovery": email_recovery
                })
            else:
                msg = result.get("message", "").lower()
                if "rate" in msg or "captcha" in msg:
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": True,
                        "exists": False,
                        "emailrecovery": None
                    })
                else:
                    out.append({
                        "name": name,
                        "domain": domain,
                        "method": method,
                        "frequent_rate_limit": frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False,
                        "emailrecovery": None
                    })
        except Exception:
            # Fallback: parse HTML response
            result_body = BeautifulSoup(reset_resp.text, "html.parser")
            page_text = result_body.get_text().lower()

            email_pattern = re.search(
                r'[a-zA-Z0-9\*\.]{1,30}@[a-zA-Z0-9\.\*]+\.[a-zA-Z]{2,}',
                page_text
            )
            if email_pattern:
                email_recovery = email_pattern.group(0)

            not_found = (
                "no account" in page_text or
                "couldn't find" in page_text or
                "not found" in page_text
            )

            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": False,
                "exists": not not_found,
                "emailrecovery": email_recovery
            })

    except Exception:
        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": True,
            "exists": False,
            "emailrecovery": None
        })