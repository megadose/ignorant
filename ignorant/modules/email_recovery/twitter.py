from ignorant.core import *
from ignorant.localuseragent import *

# Twitter/X password reset flow
# Submit phone → Twitter returns masked email like "jo***@gmail.com"
# Uses public onboarding/task.json API (no auth needed beyond guest token)

async def twitter(phone, country_code, client, out):
    name = "twitter"
    domain = "twitter.com"
    method = "password_reset"
    frequent_rate_limit = True
    email_recovery = None

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Content-Type": "application/json",
        "Accept": "application/json",
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

        # Step 2: Init password reset flow
        flow_resp = await client.post(
            "https://api.twitter.com/1.1/onboarding/task.json?flow_name=password_reset",
            headers=headers,
            json={
                "input_flow_data": {
                    "flow_context": {
                        "debug_overrides": {},
                        "start_location": {"location": "unknown"}
                    }
                },
                "subtask_versions": {}
            }
        )
        flow_token = flow_resp.json().get("flow_token")
        if not flow_token:
            raise Exception("No flow token")

        # Step 3: Submit phone number
        result_resp = await client.post(
            "https://api.twitter.com/1.1/onboarding/task.json",
            headers=headers,
            json={
                "flow_token": flow_token,
                "subtask_inputs": [{
                    "subtask_id": "EnterUserIdentifier",
                    "enter_text": {
                        "text": f"+{country_code}{phone}",
                        "link": "next_link"
                    }
                }]
            }
        )
        result = result_resp.json()

        # Step 4: Parse masked email from subtasks
        for subtask in result.get("subtasks", []):
            for banner in subtask.get("select_banner", {}).get("banners", []):
                text = banner.get("header", {}).get("text", "")
                if "@" in text:
                    email_recovery = text

        errors = result.get("errors", [])
        not_found = any(e.get("code") in [236, 32, 326] for e in errors)

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