from ignorant.core import *
from ignorant.localuseragent import *

# Facebook registration flow
# Submit phone → registration endpoint returns if number is already taken

async def facebook(phone, country_code, client, out):
    name = "facebook"
    domain = "facebook.com"
    method = "register"
    frequent_rate_limit = True

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Origin": "https://www.facebook.com",
        "Referer": "https://www.facebook.com/",
    }

    try:
        # Step 1: Get form tokens
        page_resp = await client.get(
            "https://www.facebook.com/r.php",
            headers=headers
        )
        body = BeautifulSoup(page_resp.text, "html.parser")

        data = {}
        for inp in body.select("input[type=hidden]"):
            if inp.get("name"):
                data[inp["name"]] = inp.get("value", "")

        # Step 2: Submit phone
        data["reg_email__"] = f"+{country_code}{phone}"
        data["reg_email_confirmation__"] = f"+{country_code}{phone}"
        data["firstname"] = "Test"
        data["lastname"] = "User"
        data["sex"] = "1"
        data["birthday_day"] = "1"
        data["birthday_month"] = "1"
        data["birthday_year"] = "1990"

        submit_resp = await client.post(
            "https://www.facebook.com/r.php",
            headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
            data=data,
            follow_redirects=True
        )

        result_body = BeautifulSoup(submit_resp.text, "html.parser")
        page_text = result_body.get_text().lower()

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

        taken_signals = [
            "already have an account",
            "number is already",
            "phone number is already registered",
            "this mobile number is already"
        ]
        exists = any(s in page_text for s in taken_signals)

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