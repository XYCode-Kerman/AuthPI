import asyncio
import importlib

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient


@pytest_asyncio.fixture(scope='function')
async def client():
    import main
    main = importlib.reload(main)
    return TestClient(main.app)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
