from ignorant.core import *
from ignorant.localuseragent import *

#https://github.com/yazeed44/social-media-detector-api

USERS_LOOKUP_URL = 'https://i.instagram.com/api/v1/users/lookup/'
SIG_KEY_VERSION = '4'
IG_SIG_KEY = 'e6358aeede676184b9fe702b30f4fd35e71744605e39d2181a34cede076b3c33'


def generate_signature(data):
    return 'ig_sig_key_version=' + SIG_KEY_VERSION + '&signed_body=' + hmac.new(IG_SIG_KEY.encode('utf-8'),data.encode('utf-8'),hashlib.sha256).hexdigest() + '.'+ urllib.parse.quote_plus(data)

def generate_data( phone_number_raw):
    data = {'login_attempt_count': '0',
            'directly_sign_in': 'true',
            'source': 'default',
            'q': phone_number_raw,
            'ig_sig_key_version': SIG_KEY_VERSION
            }
    return data

async def instagram(phone, country_code, client, out):
    name = "instagram"
    domain = "instagram.com"
    method = "other"
    frequent_rate_limit=False

    data=generate_signature(json.dumps(generate_data(str(country_code)+str(phone))))
    headers={
    "Accept-Language": "en-US",
    "User-Agent": "Instagram 101.0.0.15.120",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "X-FB-HTTP-Engine": "Liger",
    "Connection": "close"}
    try:
        r = await client.post(USERS_LOOKUP_URL,headers=headers,data=data)
        rep=r.json()
        if "message" in rep.keys() and rep["message"]=="No users found":
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": False})
        else:
            out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                        "rateLimit": False,
                        "exists": True})
    except :
        out.append({"name": name,"domain":domain,"method":method,"frequent_rate_limit":frequent_rate_limit,
                    "rateLimit": True,
                    "exists": False})
