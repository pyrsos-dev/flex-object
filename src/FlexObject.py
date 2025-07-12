import asyncio
from typing import Any, Callable, Optional
from abc import ABC


class UnknownFieldError(Exception):
    def __init__(self, field_name: str, allowed_fields: list[str]):
        super().__init__(
            f"Unknown field requested: '{field_name}'. Allowed fields: {', '.join(allowed_fields)}"
        )


def field(func: Callable) -> Callable:
    func._is_field = True
    func._is_base_field = False
    return func


def base_field(func: Callable) -> Callable:
    func._is_field = True
    func._is_base_field = True
    return func


class FlexObject(ABC):
    @classmethod
    def flex_fields(cls) -> list[str]:
        return [
            attr
            for attr in dir(cls)
            if callable(getattr(cls, attr))
            and getattr(getattr(cls, attr), "_is_field", False)
        ]

    @classmethod
    def flex_base_fields(cls) -> list[str]:
        return [
            attr
            for attr in dir(cls)
            if callable(getattr(cls, attr))
            and getattr(getattr(cls, attr), "_is_base_field", False)
        ]

    async def create(
        self,
        fields: Optional[list[str]] = None,
        parallel: bool = False,
    ) -> dict[str, Any]:
        response = {}

        # Always included base fields
        base_methods = [getattr(self, base) for base in self.flex_base_fields()]

        # Requested fields (or all available ones if not specified)
        fields = fields or self.flex_fields()
        requested_fields = [f for f in fields if f not in self.flex_base_fields()]
        conditional_methods = []

        for field_name in requested_fields:
            method = getattr(self, field_name, None)
            if not callable(method) or not getattr(method, "_is_field", False):
                raise UnknownFieldError(field_name, self.flex_fields())
            conditional_methods.append(method)

        all_methods = base_methods + conditional_methods

        if not parallel:
            # Sequential execution
            for method in all_methods:
                if asyncio.iscoroutinefunction(method):
                    response.update(await method())
                else:
                    response.update(method())
        else:
            # Run sync methods first
            for method in all_methods:
                if not asyncio.iscoroutinefunction(method):
                    response.update(method())

            # Run async methods concurrently
            async_methods = [m for m in all_methods if asyncio.iscoroutinefunction(m)]
            if async_methods:
                results = await asyncio.gather(*(m() for m in async_methods))
                for res in results:
                    response.update(res)

        return response
