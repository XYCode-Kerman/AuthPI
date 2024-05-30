from fastapi import Request
from odmantic import AIOEngine


def require_engine(request: Request) -> AIOEngine:
    return request.app.db_engine
