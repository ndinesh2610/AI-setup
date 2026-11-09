import httpx

from mock_sdk.client import MockAPIClient


def test_get_meta_uses_fake_transport():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/meta"
        return httpx.Response(
            200,
            json={
                "variant": 3,
                "domain": "Parcels",
                "entity": "parcels",
                "pagination": "offset",
                "total": 237,
            },
        )

    transport = httpx.MockTransport(handler)
    client = MockAPIClient(transport=transport)

    try:
        result = client.get_meta()
        assert result["variant"] == 3
        assert result["total"] == 237
    finally:
        client.close()


def test_get_parcels_passes_pagination_params():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["offset"] == "5"
        assert request.url.params["limit"] == "2"

        return httpx.Response(
            200,
            json={
                "items": [],
                "offset": 5,
                "limit": 2,
                "total": 10,
            },
        )

    client = MockAPIClient(transport=httpx.MockTransport(handler))

    try:
        result = client.get_parcels(offset=5, limit=2)
        assert result["offset"] == 5
    finally:
        client.close()
