from typing import final

from src.core import ModuleResult
from json import dumps
from urllib import parse
from hashlib import sha256
import hmac
from httpx import AsyncClient
from src.module import Module, ModuleResult

# https://github.com/yazeed44/social-media-detector-api

USERS_LOOKUP_URL = "https://i.instagram.com/api/v1/users/lookup/"
SIG_KEY_VERSION = "4"
IG_SIG_KEY = "e6358aeede676184b9fe702b30f4fd35e71744605e39d2181a34cede076b3c33"
HEADERS = {
    "Accept-Language": "en-US",
    "User-Agent": "Instagram 101.0.0.15.120",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "X-FB-HTTP-Engine": "Liger",
    "Connection": "close",
}


@final
class Instagram(Module):
    @staticmethod
    def generate_signature(data: str) -> str:
        return (
            "ig_sig_key_version="
            + SIG_KEY_VERSION
            + "&signed_body="
            + hmac.new(
                IG_SIG_KEY.encode("utf-8"), data.encode("utf-8"), sha256
            ).hexdigest()
            + "."
            + parse.quote_plus(data)
        )

    @staticmethod
    def generate_data(phone_number_raw: str):
        data = {
            "login_attempt_count": "0",
            "directly_sign_in": "true",
            "source": "default",
            "q": phone_number_raw,
            "ig_sig_key_version": SIG_KEY_VERSION,
        }
        return data

    @final
    async def run(
        self,
        phone: str,
        country_code: str,
        client: AsyncClient,
    ) -> ModuleResult:
        name = "instagram"
        domain = "instagram.com"
        method = "other"
        frequent_rate_limit = False

        data = self.generate_signature(
            dumps(self.generate_data(str(country_code) + str(phone)))
        )
        try:
            r = await client.post(USERS_LOOKUP_URL, headers=HEADERS, data=data)
            rep = r.json()
            if "message" in rep.keys() and rep["message"] == "No users found":
                return {
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": False,
                }
            else:
                return {
                    "name": name,
                    "domain": domain,
                    "method": method,
                    "frequent_rate_limit": frequent_rate_limit,
                    "rateLimit": False,
                    "exists": True,
                }
        except:
            return {
                "name": name,
                "domain": domain,
                "method": method,
                "frequent_rate_limit": frequent_rate_limit,
                "rateLimit": True,
                "exists": False,
            }
