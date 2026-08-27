import pytest
import httpx

def is_local_server_running() -> bool:
    try:
        httpx.get("http://127.0.0.1:8000/", timeout=2.0)
        return True
    except Exception:
        return False

@pytest.fixture(autouse=False)
def require_local_server():
    if not is_local_server_running():
        pytest.skip(
            "Local test server not running. "
            "Start it with: "
            "cd test_site && python -m http.server 8000"
        )
