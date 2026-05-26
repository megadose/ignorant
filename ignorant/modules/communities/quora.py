from ignorant.core import *
from ignorant.localuseragent import *

# Quora registration flow
# Submit phone → Quora's signup endpoint returns whether number is taken

async def quora(phone, country_code, client, out):
    name = "quora"
    domain = "quora.com"
    method = "register"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.quora.com",
        "Referer": "https://www.quora.com/",
    }

    try:
        # Step 1: Get formkey from homepage
        page_resp = await client.get("https://www.quora.com/", headers=headers)
        body = BeautifulSoup(page_resp.text, "html.parser")

        formkey = ""
        meta = body.find("meta", {"name": "fc"})
        if meta:
            formkey = meta.get("content", "")

        # Fallback: check window.Q config in scripts
        if not formkey:
            for script in body.find_all("script"):
                if script.string and "formkey" in script.string:
                    match = re.search(r'"formkey"\s*:\s*"([^"]+)"', script.string)
                    if match:
                        formkey = match.group(1)
                        break

        # Step 2: Submit phone number
        data = {
            "phone_number": f"+{country_code}{phone}",
            "formkey": formkey
        }

        resp = await client.post(
            "https://www.quora.com/graphql/gql_para_POST?q=PhoneNumberSignupMutation",
            headers=headers,
            data=data
        )
        result = resp.json()

        # Parse response — Quora returns errors if phone is taken
        errors = result.get("errors", [])
        page_text = str(result)
        taken = (
            "already" in page_text.lower() or
            "registered" in page_text.lower() or
            "exists" in page_text.lower()
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