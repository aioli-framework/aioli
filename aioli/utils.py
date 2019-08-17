import re

import ujson

from starlette.responses import Response


def jsonify(content, status=200, **kwargs):
    return Response(
        content=ujson.dumps(content, ensure_ascii=False, **kwargs).encode("utf8"),
        status_code=status,
        headers={"content-type": "application/json"},
    )


def format_path(*parts):
    path = ""

    for part in parts:
        path = f"/{path}/{part}"

    return re.sub(r"/+", "/", path.rstrip("/"))
