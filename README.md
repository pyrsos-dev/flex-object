<img src="./flexobject-with-text.svg" alt="Flex Object Logo" width="400" height="160"/>

# FlexObject — Flexible Data Aggregation & Object Creation

**FlexObject** is a Python base class designed for flexible, on-demand data aggregation & object creation. It supports synchronous and asynchronous field methods, optional parallel execution, and lazy evaluation — computing fields only when requested, avoiding unnecessary work.

Consider it a creational design pattern that dynamically constructs structured objects based on runtime input, making it useful for APIs, adapters, view-models, etc - while eliminating the need for repetitive if-ology by allowing individual fields to be defined as self-contained methods.

## Features

* **Dynamic fields:** Define data suppliers as methods decorated with `@field` or `@base_field`.
* **Selective field retrieval:** Compute only the fields you ask for, on-demand.
* **Lazy evaluation:** Field methods run *only if* included in the requested fields.
* **Async & sync support:** Handles both types seamlessly.
* **Optional parallel execution:** Run async fields concurrently to speed up processing.
* **Clear error handling:** Raises errors if unknown fields are requested.

## How Lazy Evaluation Works

When you create a FlexObject instance with a specific list of fields, **only those fields are computed** when you call `.create()`. Base fields are always included. This means your program avoids unnecessary data fetching or computation, optimizing performance and resource use.

## Usage with Lazy Evaluation

```python
from flexobject import base_field, field, FlexObject
import asyncio

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

obj = DummyButFlexObject(id="123")

# Lazy evaluation means only 'field_a' and 'field_b' + base fields run
data = await obj.create(fields=["field_a", "field_b"])
```

## Parallel and Lazy Evaluation Together

```python
obj = DummyButFlexObject(id="123")

# Lazy evaluation means only 'field_a' and 'field_b'
data = await obj.create(fields=["field_a", "field_b"], parallel=True)  # async fields run concurrently
```

### Thread Safety & Parallelism

| Case                      | Description                                  | Parallel Safe? | Notes                                         |
|---------------------------|----------------------------------------------|----------------|-----------------------------------------------|
| Pure async functions      | Async, no side effects                       | ✅ Yes         | Ideal — run concurrently                      |
| Pure sync functions       | Sync, no side effects                        | ✅ Yes         | Run before async to avoid blocking            |
| CPU-bound pure functions  | Heavy but stateless sync logic               | ⚠️ Caution      | Can block loop — consider `run_in_executor`  |
| Impure functions          | Modify global/shared state                   | ❌ No          | Can cause race conditions                     |
| Async with side effects   | External writes (DB, cache, etc.)            | ⚠️ Caution      | Ensure idempotency / isolation               |
| Stateful logic            | Relies on order or mutable shared state      | ❌ No          | Not safe for parallel execution               |

> ⚠️ **Note on `parallel`**
>
> The `parallel=True` flag enables concurrent execution of async field methods using `asyncio`. 
> This improves performance for I/O-bound tasks (e.g. DB calls), but is **not** true multithreading or multiprocessing.
> The term *parallel* is used for clarity, though it technically refers to *concurrent* async execution.

## Summary

| Feature                  | Description                                         |
| ------------------------ | --------------------------------------------------- |
| **Lazy evaluation**      | Compute only requested fields, on-demand.           |
| **Parallel execution**   | Run async fields concurrently with `parallel=True`. |
| **Sync & Async support** | Mix synchronous and asynchronous field methods.     |
| **Selective retrieval**  | Specify exactly which fields to fetch.              |

## Example

If you have `uv` start the example with:

`uv run -m src` and visit: [OpenAPI Docs](http://localhost:5005/docs)

## License 

MIT License
