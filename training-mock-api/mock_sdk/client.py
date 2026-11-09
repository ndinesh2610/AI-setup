import random
import time
from collections.abc import Iterator

import httpx

from mock_sdk.models import Parcel


class MockAPIClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:9001",
        max_retries: int = 3,
        transport: httpx.BaseTransport | None = None,
    ):
        self.client = httpx.Client(
            base_url=base_url,
            timeout=httpx.Timeout(10.0),
            transport=transport,
        )
        self.max_retries = max_retries

    def get(self, path: str, params: dict | None = None) -> dict:
        for attempt in range(self.max_retries + 1):
            response = self.client.get(path, params=params)

            if response.status_code == 429 or response.status_code >= 500:
                if attempt == self.max_retries:
                    response.raise_for_status()

                retry_after = response.headers.get("Retry-After")

                if retry_after:
                    delay = float(retry_after)
                else:
                    delay = (2**attempt) + random.uniform(0, 1)

                time.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        raise RuntimeError("Retry limit exceeded")

    def get_meta(self) -> dict:
        return self.get("/v1/meta")

    def get_parcels(self, offset: int = 0, limit: int = 5) -> dict:
        return self.get(
            "/v1/parcels",
            params={"offset": offset, "limit": limit},
        )

    def close(self) -> None:
        self.client.close()

    def iter_parcels(self, limit: int = 5) -> Iterator[Parcel]:
        offset = 0
        total = None
        seen_ids: set[int] = set()

        while total is None or offset < total:
            page = self.get_parcels(offset=offset, limit=limit)
            total = page["total"]

            for record in page["items"]:
                parcel = Parcel.model_validate(record)

                if parcel.id not in seen_ids:
                    seen_ids.add(parcel.id)
                    yield parcel

            offset += limit
