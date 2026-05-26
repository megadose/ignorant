from ignorant.core import *
from ignorant.localuseragent import *

# PhonePe login flow
# PhonePe is UPI/phone-first — checks if number has a PhonePe account
# Uses their internal merchant/consumer login API

async def phonepe(phone, country_code, client, out):
    name = "phonepe"
    domain = "phonepe.com"
    method = "login"
    frequent_rate_limit = False

    headers = {
        "User-Agent": random.choice(ua["browsers"]["chrome"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.phonepe.com",
        "Referer": "https://www.phonepe.com/",
        "X-Request-Id": ''.join(random.choices(string.ascii_lowercase + string.digits, k=32)),
    }

    try:
        resp = await client.post(
            "https://api.phonepe.com/apis/hermes/v3/user/login/mobile",
            headers=headers,
            json={
                "mobileNumber": str(phone),
                "countryCode": str(country_code),
                "merchantId": "PHONEPE",
                "transactionId": ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)),
            }
        )

        result = resp.json()
        code = result.get("code", "")
        message = result.get("message", "").lower()
        data = result.get("data", {})

        if resp.status_code == 429 or code == "RATE_LIMIT":
            out.append({
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False
            })
            return

        # SUCCESS or OTP_SENT = number is registered
        # USER_NOT_FOUND or INVALID = not registered
        is_existing = (
            code in ["SUCCESS", "OTP_SENT", "USER_EXISTS"] or
            data.get("userExists", False) or
            data.get("isRegistered", False) or
            "otp" in message or
            "success" in message
        )

        not_found = (
            code in ["USER_NOT_FOUND", "INVALID_MOBILE", "NOT_REGISTERED"] or
            "not found" in message or
            "not registered" in message or
            "invalid" in message
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