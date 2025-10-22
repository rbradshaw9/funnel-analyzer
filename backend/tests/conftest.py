import sys
import warnings
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure repository root is on the Python path so `backend` package resolves
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from backend.main import app  # noqa: E402  pylint: disable=wrong-import-position

# Silence httpx warning about deprecated `app=` shortcut while FastAPI migrates
warnings.filterwarnings(
    "ignore",
    message=r"The 'app' shortcut is now deprecated.*",
    category=DeprecationWarning,
)


@pytest.fixture()
def client() -> TestClient:
    """FastAPI test client fixture."""
    return TestClient(app)
