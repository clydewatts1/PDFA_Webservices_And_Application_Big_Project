"""Shared session/auth guard decorators for Quart routes."""

from __future__ import annotations

import inspect
from functools import wraps
from typing import Any, Callable

from quart import redirect, request, session


def _is_authenticated() -> bool:
    return bool(session.get("actor_name"))


def _has_active_workflow() -> bool:
    return bool(session.get("active_workflow_name"))


def _safe_next_param() -> str:
    path = request.path or "/"
    if path.startswith("/"):
        return path
    return "/"


def login_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Require an authenticated session before executing a route."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _is_authenticated():
            return redirect(f"/login?next={_safe_next_param()}")
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    return wrapper


def workflow_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Require active workflow context in session before executing a route."""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not _is_authenticated():
            return redirect(f"/login?next={_safe_next_param()}")
        if not _has_active_workflow():
            return redirect("/dashboard")
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return await result
        return result

    return wrapper
