"""
pytest configuration for backend tests

This file runs automatically before all tests in this directory.
It loads environment variables from .env file so tests can access API keys.
"""

from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()