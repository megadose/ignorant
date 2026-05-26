from ignorant.core import *
from ignorant.localuseragent import *

# Facebook account recovery flow
# Submit phone → Facebook shows masked email on "find your account" page
# e.g. "We'll send a login link to j***@gmail.com"

async def facebook(phone, country_code, client, out):
    name = "facebook"
    domain = "facebook.com"
    method = "password_reset"
    frequent_rate_limit = True
    email_recovery = None

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Origin": "https://www.facebook.com",
        "Referer": "https://www.facebook.com/",
    }

    try:
        # Step 1: Load find-account page to grab tokens
        page_resp = await client.get(
            "https://www.facebook.com/login/identify/",
            headers=headers
        )
        body = BeautifulSoup(page_resp.text, "html.parser")

        # Extract hidden form fields (lsd, jazoest, etc.)
        data = {}
        for inp in body.select("input[type=hidden]"):
            if inp.get("name"):
                data[inp["name"]] = inp.get("value", "")

        # Step 2: Submit phone number
        data["email"] = f"+{country_code}{phone}"
        data["did_submit"] = "Search"

        submit_resp = await client.post(
            "https://www.facebook.com/login/identify/",
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
            data=data,
            follow_redirects=True
        )

        result_body = BeautifulSoup(submit_resp.text, "html.parser")
        page_text = result_body.get_text()

        # Parse masked email — Facebook shows "Send code to j***@gmail.com"
        email_pattern = re.search(
            r'[a-zA-Z0-9\*\.]{1,30}@[a-zA-Z0-9\.\*]+\.[a-zA-Z]{2,}',
            page_text
        )
        if email_pattern:
            email_recovery = email_pattern.group(0)

        not_found_signals = [
            "your search returned no results",
            "no account found",
            "couldn't find your account"
        ]
        not_found = any(s in page_text.lower() for s in not_found_signals)

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