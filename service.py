from time import sleep

SLOW_RESPONSE_SECONDS = 80


def health() -> dict[str, str]:
    return {"status": "ok"}


def info() -> dict[str, str]:
    return {"framework": "linking", "profile": "light"}


def echo(message: str, count: int) -> dict[str, object]:
    return {"received": {"message": message, "count": count}}


def item(item_id: int, include_details: bool = False) -> dict[str, object]:
    response: dict[str, object] = {
        "item_id": item_id,
        "include_details": include_details,
    }
    if include_details:
        response["details"] = f"Reference item {item_id}"
    return response


def slow() -> dict[str, object]:
    sleep(SLOW_RESPONSE_SECONDS)
    return {"delay_seconds": SLOW_RESPONSE_SECONDS, "status": "completed"}
