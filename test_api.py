import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

# Set environment variables for tests if needed, e.g., for database or API keys
os.environ["GOOGLE_API_KEY"] = "test_google_api_key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:" # Use in-memory SQLite for tests
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


# It's important that app is imported *after* the environment variables are set,
# especially if the app's configuration depends on them at import time.
from app.main import app
from app.database import engine, SessionLocal # Base is in app.models
from app.models import User, Base # Import User model and Base for table creation
from app.auth import create_access_token # If creating tokens for tests


# Setup a test database
@pytest.fixture(scope="session", autouse=True)
def db_setup_session():
    # Create tables in the in-memory SQLite database
    Base.metadata.create_all(bind=engine)
    yield
    # You could drop tables here if needed, but for in-memory, it's usually not necessary
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    """Provides a database session for tests."""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@pytest.fixture
def client(db_setup_session): # Ensure db_setup_session runs before client fixture
    """Provides a TestClient instance for making API requests."""
    return TestClient(app)

# --- Test for /generate-image endpoint ---

@patch("app.api.generate_image_with_imagen") # Patch the function in api.py
def test_generate_image_success(mock_generate_image_with_imagen, client: TestClient):
    """
    Tests successful image generation via the /generate-image endpoint.
    """
    mock_generate_image_with_imagen.return_value = "http://example.com/generated_image.png"

    response = client.post("/generate-image", json={"prompt": "A cute cat"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["image_url"] == "http://example.com/generated_image.png"
    mock_generate_image_with_imagen.assert_called_once_with("A cute cat")

@patch("app.api.generate_image_with_imagen")
def test_generate_image_api_error(mock_generate_image_with_imagen, client: TestClient):
    """
    Tests the /generate-image endpoint when the underlying service returns an error.
    """
    mock_generate_image_with_imagen.return_value = "Error: AI service unavailable"

    response = client.post("/generate-image", json={"prompt": "A fantasy landscape"})

    assert response.status_code == 500
    json_response = response.json()
    assert "Error: AI service unavailable" in json_response["detail"]
    mock_generate_image_with_imagen.assert_called_once_with("A fantasy landscape")

@patch("app.api.generate_image_with_imagen")
def test_generate_image_internal_server_error(mock_generate_image_with_imagen, client: TestClient):
    """
    Tests the /generate-image endpoint when an unexpected exception occurs.
    """
    mock_generate_image_with_imagen.side_effect = Exception("Unexpected internal error")

    response = client.post("/generate-image", json={"prompt": "A robot dog"})

    assert response.status_code == 500
    json_response = response.json()
    assert "Image generation failed: Unexpected internal error" in json_response["detail"]
    mock_generate_image_with_imagen.assert_called_once_with("A robot dog")

def test_generate_image_invalid_request_no_prompt(client: TestClient):
    """
    Tests the /generate-image endpoint with a missing prompt.
    """
    response = client.post("/generate-image", json={}) # Missing "prompt"

    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error
    json_response = response.json()
    assert "detail" in json_response
    assert any(detail["msg"] == "Field required" and "prompt" in detail["loc"] for detail in json_response["detail"])

# Example of testing with authentication (if you enable token verification in the endpoint)
# @patch("app.api.generate_image_with_imagen")
# @patch("app.api.verify_token") # Patch verify_token used in your endpoint
# def test_generate_image_with_auth_success(mock_verify_token, mock_generate_image, client: TestClient, db: Session):
#     # Create a dummy user for token generation
#     # This part depends on your User model and how users are created/retrieved
#     # For simplicity, we assume verify_token just needs to return a valid payload
#     mock_verify_token.return_value = {"sub": "testuser@example.com"}
#     mock_generate_image.return_value = "http://example.com/authed_image.png"

#     # Create a dummy token (in a real scenario, you might generate one properly)
#     # token = create_access_token(data={"sub": "testuser@example.com"})
#     token = "fake-test-token"


#     response = client.post(
#         "/generate-image",
#         json={"prompt": "A secure image"},
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     assert response.status_code == 200
#     assert response.json()["image_url"] == "http://example.com/authed_image.png"
#     mock_verify_token.assert_called_once_with(token)
#     mock_generate_image.assert_called_once_with("A secure image")

# @patch("app.api.verify_token")
# def test_generate_image_with_auth_invalid_token(mock_verify_token, client: TestClient):
#     mock_verify_token.return_value = None # Simulate invalid token

#     token = "invalid-fake-token"
#     response = client.post(
#         "/generate-image",
#         json={"prompt": "An image I should not get"},
#         headers={"Authorization": f"Bearer {token}"}
#     )
#     assert response.status_code == 401 # Unauthorized
#     assert "Invalid or expired token" in response.json()["detail"]

# TODO: Add more tests as needed, for example:
# - Different prompt types
# - What happens if the image generation returns other error formats
# - Test with authentication if you decide to enforce it on the endpoint
# - Test specific parameters passed to generate_image_with_imagen if the endpoint allows more customization

# A simple health check test for the root endpoint, good for basic setup verification
def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to Omeyo AI Agent API!"

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Remember to install test dependencies:
# pip install pytest httpx requests types-requests
# (httpx is used by TestClient, requests might be useful for other tests)
# Also, if you use SQLite in-memory, you might need `python-multipart` for form data, etc.
# but for JSON APIs, it's usually not required immediately.
# Ensure google-cloud-aiplatform is also available or properly mocked if its imports are at module level.
# For these tests, we are mocking at the point of use in `app.api` or `app.ai_agent`.
# The GOOGLE_API_KEY is set as an example; it's not directly used by these mocks but good practice for consistency.
# The DATABASE_URL is crucial for `app.database` to initialize correctly.
# SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES are for `app.auth` if you test auth-related parts.
# The `db_setup_session` fixture ensures that `Base.metadata.create_all(bind=engine)` is called
# once per test session, setting up the schema in the in-memory SQLite DB.
# The `client` fixture then uses this setup.
# The `db` fixture provides a short-lived session for tests that might need to interact with the DB directly.
# `autouse=True` on `db_setup_session` makes it run automatically for the session.
# The order of imports for `app.main.app` matters: it should come after `os.environ` modifications
# if the app's module-level code depends on those environment variables.
# If `app.models` or other modules are imported by `app.main` and they depend on `app.database.engine`
# (which depends on DATABASE_URL), then DATABASE_URL must be set before `from app.main import app`.

# To run these tests:
# Ensure pytest is installed: pip install pytest
# Navigate to the root directory of your project (where test_api.py and test_ai_agent.py are)
# Run: pytest
# Or: pytest test_api.py test_ai_agent.py
# You might need to add `__init__.py` to your `app` directory if it's not already there
# and potentially set PYTHONPATH if pytest has trouble finding your `app` module:
# export PYTHONPATH=. (from the root directory)
# pytest
#
# If you see errors related to "Event loop is closed", especially with async code and TestClient,
# ensure your test functions using TestClient with async endpoints are not marked `async def`.
# TestClient handles the event loop for you. `pytest.mark.asyncio` is for testing async functions directly.
# In `test_ai_agent.py`, we use `@pytest.mark.asyncio` because we are `await`ing the async function.
# In `test_api.py`, the test functions are synchronous, and `TestClient` calls the async API endpoints.
#
# Ensure your `app.ai_agent.PROJECT_ID` is either set or mocked if `generate_image_with_imagen`
# is called directly without mocking it (which we are mocking in `test_api.py`).
# In `test_ai_agent.py`, `aiplatform.init` is mocked, so `PROJECT_ID`'s value within that mock context
# doesn't hit the actual GCP services.
#
# The `google-cloud-aiplatform` library might have its own dependencies or expectations
# regarding authentication (like GOOGLE_APPLICATION_CREDENTIALS). Since we are mocking
# the calls to this library, we bypass the need for actual credentials during these unit tests.
# If you were writing integration tests that hit the actual Vertex AI, you'd need credentials.
#
# The provided tests cover:
# 1. `test_ai_agent.py`: Unit tests for `generate_image_with_imagen` focusing on its internal logic and error handling,
#    mocking out the actual `google.cloud.aiplatform` calls.
# 2. `test_api.py`: Integration-style tests for the `/generate-image` FastAPI endpoint, mocking the call
#    to `generate_image_with_imagen` to isolate endpoint logic (request/response handling, error propagation).
#    It also includes basic setup for an in-memory SQLite database for other potential API tests.
#
# This structure allows you to test the AI logic and API logic separately.
#
# A note on mocking `app.api.generate_image_with_imagen` vs `app.ai_agent.generate_image_with_imagen`:
# In `test_api.py`, we use `@patch("app.api.generate_image_with_imagen")`. This is because `app.api`
# imports `generate_image_with_imagen` from `app.ai_agent`. When testing `app.api`, you need to patch
# the function where it's looked up *by `app.api`*, which is `app.api.generate_image_with_imagen`.
# If you patched `app.ai_agent.generate_image_with_imagen`, the `app.api` module would still use
# its original imported version unless that import itself was manipulated.
# This is a common pattern: "patch where the object is used, not where it's defined."
# (See https://docs.python.org/3/library/unittest.mock.html#where-to-patch)
#
# The `os.environ` settings at the top of `test_api.py` are crucial. They configure the application
# for a test environment *before* `from app.main import app` is executed. This ensures that
# modules like `app.database` or `app.auth` initialize with test-specific configurations
# (e.g., in-memory SQLite DB, dummy secret keys).
#
# If `app.models` or other parts of your application implicitly rely on `app.database.engine`
# being configured at import time, this setup is necessary. The `db_setup_session` fixture
# then uses this engine to create tables.

# Add a conftest.py if you have many shared fixtures or hooks.
# For now, placing fixtures in test_api.py is fine if they are specific to API tests
# or if this is the main test file requiring DB setup.
# If `test_ai_agent.py` also needed DB access (it doesn't currently),
# you might move db fixtures to `conftest.py`.
#
# Final check on dependencies for testing:
# `pytest`
# `httpx` (for TestClient)
# `sqlalchemy` (if using DB, which we are for `test_api.py` setup)
# `psycopg2-binary` or `sqlite3` (Python built-in for sqlite) - we use sqlite for tests.
# `google-cloud-aiplatform` (even if mocked, its presence might be checked by imports,
#  or types from it might be used in type hints, so it's good to have in the test env's venv)
#
# The `test_generate_image_invalid_request_no_prompt` checks for a 422 error, which is FastAPI's
# default response for Pydantic validation errors. The structure of the error detail
# can be inspected to confirm it's due to the missing "prompt" field.
#
# The commented-out authentication tests provide a template for how you might test
# token-protected endpoints. You'd need to mock `verify_token` (or your actual token
# validation logic) and potentially create users/tokens if your tests involve user-specific logic.
# For the current plan, the image generation endpoint does not strictly require authentication
# in its basic form, but the stubs are there if you add that requirement.
# The current implementation of the `/generate-image` endpoint in `app/api.py` has token verification
# commented out. If you uncomment it, these auth tests become relevant.
#
# The `client` fixture depends on `db_setup_session` to ensure the database is set up
# before any tests using the client (and thus potentially the app) are run. This is good practice.
#
# The `db` fixture provides a database session for tests that need to directly manipulate the database,
# for example, to set up specific data states before an API call or to verify data changes after an API call.
# It ensures the session is properly closed after the test.
#
# To improve, consider a `conftest.py` for shared fixtures like `client`, `db`, and `db_setup_session`
# if you have multiple test files that need them. This keeps your test files cleaner.
#
# One final thought on `GOOGLE_API_KEY` in `test_api.py`:
# `os.environ["GOOGLE_API_KEY"] = "test_google_api_key"`
# This is set, but `app.ai_agent.py` (where `genai.configure` happens) might be imported
# before this line in `test_api.py` gets a chance to run if `app.main` imports `app.api` which imports `app.ai_agent`.
# The order of imports and environment variable setting is critical.
# If `genai.configure` in `app.ai_agent.py` runs at module import time, it uses whatever
# `GOOGLE_API_KEY` is set at that exact moment.
# To be safe, environment variables needed by module-level configurations should be set
# *as early as possible*, potentially in `conftest.py` before any app modules are imported,
# or by using a `.env.test` file loaded by `python-dotenv` if your app supports it for tests.
# However, since `generate_image_with_imagen` (Vertex AI) typically uses Application Default Credentials
# or `GOOGLE_APPLICATION_CREDENTIALS` env var, and `call_gemini_api` (Generative AI) uses `GOOGLE_API_KEY`,
# ensure the correct auth method is mocked/handled for each.
# For `generate_image_with_imagen`, `aiplatform.init()` is called inside the function, so `PROJECT_ID` is the main concern there.
# For `call_gemini_api`, `genai.configure()` is at module level. If `test_api.py` calls an endpoint that uses `call_gemini_api`,
# that `GOOGLE_API_KEY` better be set correctly before `app.ai_agent` is first imported by the test runner's path.
# Since `test_api.py` is focused on `/generate-image`, which uses `generate_image_with_imagen`, this is less of an immediate issue
# for *these specific tests* but important for overall test suite stability if other endpoints are tested.
# The `client` fixture implicitly imports `app.main.app`, which then imports other app modules.
# So, `os.environ` lines at the top of `test_api.py` *should* take effect before `app.ai_agent`'s module-level code runs
# *for the context of tests run from `test_api.py`*.
# If `test_db.py` or another test file is run first by pytest and it also imports `app.ai_agent` without setting the key,
# then the module might be cached with the wrong (or no) key.
# This is why `conftest.py` is often the best place for session-wide setup that must happen before any app code is imported.
# For now, this setup should be okay given the test focus.
#
# The `pytest-asyncio` library is needed if you have async test functions (like in test_ai_agent.py).
# Install it with: pip install pytest-asyncio
# Ensure it's in your requirements-dev.txt or similar.
#
# Test collection notes:
# Pytest will discover files named `test_*.py` or `*_test.py`.
# Inside those files, it will collect functions prefixed with `test_`.
# If you have classes, they should be prefixed with `Test`, and methods within them prefixed with `test_`.
# The current structure with top-level test functions is standard and works well.
#
# Running tests with coverage:
# pip install pytest-cov
# pytest --cov=app .  (run from root, assuming your app code is in 'app/' and tests are in root)
# This will show you test coverage for your application code.
# You can configure coverage options in `pyproject.toml` or `.coveragerc`.
