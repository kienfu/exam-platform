from collections.abc import Callable
from typing import Any

Handler = Callable[[dict[str, Any]], None]


def default_handlers() -> dict[str, Handler]:
    from app.jobs.handlers.sample import echo

    return {"sample.echo": echo}
