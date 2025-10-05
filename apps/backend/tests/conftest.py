"""
pytest configuration for backend tests

This file runs automatically before all tests in this directory.
It loads environment variables from .env file so tests can access API keys.
"""

import asyncio
import pytest
import pytest_asyncio
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    """
    Create a session-scoped event loop.

    This overrides pytest-asyncio's default function-scoped event_loop
    to allow session-scoped async fixtures.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db_pool():
    """
    Initialize database connection pool before tests run.

    - scope="session": Runs once for entire test session
    - autouse=True: Automatically used by all tests (no need to explicitly request)

    This fixture:
    1. Initializes the DB pool before any tests run
    2. Yields control to run tests
    3. Closes the pool after all tests complete
    """
    from app.db.client import init_db_pool, close_db_pool

    # Setup: Initialize pool before tests
    await init_db_pool()
    print("\n✅ Test database pool initialized")

    # Run tests
    yield

    # Teardown: Close pool after all tests
    await close_db_pool()
    print("\n✅ Test database pool closed")