import logging
from typing import Any

logger = logging.getLogger(__name__)


def echo(payload: dict[str, Any]) -> None:
    """Sample job: proves enqueue, claim, handler and complete work end to end."""
    if payload.get("fail"):
        raise RuntimeError("sample.echo asked to fail")
    logger.info("sample.echo payload=%s", payload)
