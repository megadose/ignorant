from typing import Any, Optional, TypedDict

from httpx import AsyncClient
from abc import ABC, abstractmethod


class ModuleResult(TypedDict):
    name: str
    domain: Any
    rateLimit: bool
    exists: bool
    method: Optional[str]
    frequent_rate_limit: bool


class Module(ABC):
    @abstractmethod
    async def run(
        self,
        phone: str,
        country_code: str,
        client: AsyncClient,
    ) -> ModuleResult:
        raise NotImplementedError()
