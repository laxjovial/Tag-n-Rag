import sys
import os
import pytest

# Add the app directory to the Python path to allow for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.api.auth import get_password_hash, verify_password

def test_password_hashing():
    """
    Tests that password hashing and verification work correctly.
    """
    password = "a_strong_password"

    # 1. Hash the password
    hashed_password = get_password_hash(password)

    # Assert that the hash is not the same as the original password
    assert password != hashed_password

    # 2. Verify the password
    assert verify_password(password, hashed_password)

    # 3. Verify that a wrong password fails
    assert not verify_password("a_wrong_password", hashed_password)
