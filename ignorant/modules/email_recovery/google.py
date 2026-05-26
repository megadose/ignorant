from ignorant.core import *
from ignorant.localuseragent import *

# Google account recovery flow
# NOTE: no-JS brute-force endpoint patched June 6 2025 (BruteCat disclosure)
# This uses the standard recovery flow — still leaks account existence

async def google(phone, country_code, client, out):
    name = "google"
    domain = "google.com"
    method = "account_recovery"
    frequent_rate_limit = True
    email_recovery = None

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Origin": "https://accounts.google.com",
        "Referer": "https://accounts.google.com/",
    }

    try:
        # Step 1: Load recovery page, grab hidden tokens
        page_resp = await client.get(
            "https://accounts.google.com/signin/recovery",
            headers=headers
        )
        body = BeautifulSoup(page_resp.text, "html.parser")

        data = {}
        for inp in body.select("input[type=hidden]"):
            if inp.get("name"):
                data[inp["name"]] = inp.get("value", "")

        # Step 2: Submit phone number
        data["phoneNumber"] = f"+{country_code}{phone}"
        data["continue"] = "https://accounts.google.com/signin/recovery"

        submit_resp = await client.post(
            "https://accounts.google.com/signin/recovery",
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
            data=data
        )

        result_body = BeautifulSoup(submit_resp.text, "html.parser")
        page_text = result_body.get_text()

        # Parse masked email if leaked
        email_pattern = re.search(
            r'[a-zA-Z0-9\*\.]{1,30}@[a-zA-Z0-9\.\*]+\.[a-zA-Z]{2,}',
            page_text
        )
        if email_pattern:
            email_recovery = email_pattern.group(0)

        not_found_signals = [
            "couldn't find your google account",
            "no account found",
            "we couldn't find an account"
        ]
        found_signals = [
            "verify it's you",
            "check your",
            "we found your account",
            "confirm your recovery"
        ]

        page_lower = page_text.lower()
        not_found = any(s in page_lower for s in not_found_signals)
        found = any(s in page_lower for s in found_signals) or email_recovery is not None

        out.append({
            "name": name,
            "domain": domain,
            "method": method,
            "frequent_rate_limit": frequent_rate_limit,
            "rateLimit": False,
            "exists": found and not not_found,
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