import pytest
import asyncio
import httpx
import pytest_asyncio
from pykv.store import Store
from pykv.api import create_app

@pytest.fixture
def wal_path(tmp_path):
    return tmp_path / "wal.log"

@pytest.fixture
def store(wal_path):
    # Each test gets its own Store with an isolated WAL.
    return Store(wal_path=wal_path)

@pytest.fixture
def test_app(store):
    # Application factory receives the fresh Store.
    return create_app(store)

@pytest_asyncio.fixture
async def client(test_app):
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

# 1. PUT with a string value
@pytest.mark.asyncio
async def test_put_string(client):
    resp = await client.put("/keys/foo", json={"value": "bar"})
    assert resp.status_code == 200
    assert resp.json() == {"result": "ok"}

# 2. PUT with a numerical value
@pytest.mark.asyncio
async def test_put_number(client):
    resp = await client.put("/keys/num", json={"value": 123})
    assert resp.status_code == 200
    # Verify later with GET
    get_resp = await client.get("/keys/num")
    assert get_resp.status_code == 200
    assert get_resp.json() == {"value": 123}

# 3. PUT with a dictionary
@pytest.mark.asyncio
async def test_put_dict(client):
    data = {"a": 1, "b": "x"}
    resp = await client.put("/keys/dict", json={"value": data})
    assert resp.status_code == 200
    get_resp = await client.get("/keys/dict")
    assert get_resp.status_code == 200
    assert get_resp.json() == {"value": data}

# 4. PUT with None
@pytest.mark.asyncio
async def test_put_none(client):
    resp = await client.put("/keys/null", json={"value": None})
    assert resp.status_code == 200
    get_resp = await client.get("/keys/null")
    assert get_resp.status_code == 200
    assert get_resp.json() == {"value": None}

# 5. GET existing key (already covered above, but include a simple one)
@pytest.mark.asyncio
async def test_get_existing(client):
    await client.put("/keys/item", json={"value": "val"})
    resp = await client.get("/keys/item")
    assert resp.status_code == 200
    assert resp.json() == {"value": "val"}

# 6. GET missing key -> 404
@pytest.mark.asyncio
async def test_get_missing(client):
    resp = await client.get("/keys/doesnotexist")
    assert resp.status_code == 404

# 7. DELETE existing key -> 204
@pytest.mark.asyncio
async def test_delete_success(client):
    await client.put("/keys/todel", json={"value": "x"})
    resp = await client.delete("/keys/todel")
    assert resp.status_code == 204
    # Ensure it is gone
    get_resp = await client.get("/keys/todel")
    assert get_resp.status_code == 404

# 8. DELETE missing key -> 404
@pytest.mark.asyncio
async def test_delete_missing(client):
    resp = await client.delete("/keys/absent")
    assert resp.status_code == 404

# 9. GET /keys list
@pytest.mark.asyncio
async def test_list_keys(client):
    await client.put("/keys/a", json={"value": 1})
    await client.put("/keys/b", json={"value": 2})
    resp = await client.get("/keys")
    assert resp.status_code == 200
    data = resp.json()
    assert "keys" in data
    assert set(data["keys"]) >= {"a", "b"}

# 10. 50 concurrent PUTs and verification
@pytest.mark.asyncio
async def test_concurrent_puts(client):
    keys = [f"key{i}" for i in range(50)]
    values = [i * 10 for i in range(50)]
    # Prepare coroutines for PUT
    put_coros = [client.put(f"/keys/{k}", json={"value": v}) for k, v in zip(keys, values)]
    put_resps = await asyncio.gather(*put_coros)
    for resp in put_resps:
        assert resp.status_code == 200
    # Verify each key
    get_coros = [client.get(f"/keys/{k}") for k in keys]
    get_resps = await asyncio.gather(*get_coros)
    for k, v, resp in zip(keys, values, get_resps):
        assert resp.status_code == 200
        assert resp.json() == {"value": v}

