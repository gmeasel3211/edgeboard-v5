import asyncio

from ..db import SessionLocal
from ..services.pipeline import Pipeline


async def main() -> None:
    delays = (0, 30, 120)
    last_error: Exception | None = None
    for attempt, delay in enumerate(delays, start=1):
        if delay:
            await asyncio.sleep(delay)
        try:
            with SessionLocal() as db:
                result = await Pipeline().refresh(db, triggered_by=f"scheduled-refresh-attempt-{attempt}")
                print(result)
                return
        except Exception as exc:
            last_error = exc
            print({"status": "retrying" if attempt < len(delays) else "failed", "attempt": attempt, "error": str(exc)})
    if last_error:
        raise last_error


if __name__ == "__main__":
    asyncio.run(main())
