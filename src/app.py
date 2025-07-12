import asyncio
import time
from typing import Any
from fastapi import APIRouter, Query, Path, HTTPException
from .FlexObject import base_field, field, FlexObject, UnknownFieldError

router = APIRouter()

class DummyButFlexObject(FlexObject):
    def __init__(self, id: str):
        self.id = id

    @base_field
    def base_fields(self) -> dict[str, Any]:
        return {"id": self.id}

    @field
    async def field_a(self) -> dict[str, Any]:
        await asyncio.sleep(0.1)  # simulate async operation
        return {"field_a": "value retrieved from mongo"}

    @field
    def field_b(self) -> dict[str, Any]:
        return {"field_b": "static value b"}

    @field
    async def field_c(self) -> dict[str, Any]:
        await asyncio.sleep(0.9)
        return {"field_c": f"value retrieved from postgres"}

    @field
    def field_d(self) -> dict[str, Any]:
        return {"field_d": "static value d"}

    @field
    async def field_e(self) -> dict[str, Any]:
        await asyncio.sleep(2)
        return {"field_e": "value retrieved from some heavy calculations"}


@router.get("/flex/{id}")
async def get_flex_object(
    id: str = Path(..., description="The ID of the object"),
    fields: list[str] = Query(
        default=[],
        description=f"Allowed fields: {', '.join(DummyButFlexObject.flex_fields())}",
    ),
    parallel: bool = Query(
        default=False,
        description="Create object in parallel"
    )
):
    try:
        flex_object = DummyButFlexObject(id=id)
        start_time = time.perf_counter()
        result = await flex_object.create(fields=fields, parallel=parallel)
        duration = time.perf_counter() - start_time

        return {
            "object_created": result,
            "took": round(duration, 4),
        }
    except UnknownFieldError as e:
        raise HTTPException(status_code=400, detail=str(e))

