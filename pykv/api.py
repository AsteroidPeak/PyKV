from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from pykv.store import Store

def create_app(store: Optional[Store] = None) -> FastAPI:
    app = FastAPI()
    app.state.store = store if store is not None else Store()

    class ValueItem(BaseModel):
        value: object

    @app.put("/keys/{key}")
    async def put_key(key: str, item: ValueItem):
        app.state.store.set(key, item.value)
        return {"result": "ok"}

    @app.get("/keys/{key}")
    async def get_key(key: str):
        if not app.state.store.contains(key):
            raise HTTPException(status_code=404, detail="Key not found")
        return {"value": app.state.store.get(key)}

    @app.delete("/keys/{key}")
    async def delete_key(key: str):
        if not app.state.store.delete(key):
            raise HTTPException(status_code=404, detail="Key not found")
        return Response(status_code=204)

    @app.get("/keys")
    async def list_keys():
        return {"keys": app.state.store.keys()}

    return app
