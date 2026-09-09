"""
Comprehensive Authentication Flow Tests for Sahakar Sahayak (India)
Tests:
1. Register with name, email, phone (+91 Indian format), password
2. Prevent duplicate email (409 Conflict)
3. Prevent duplicate phone (409 Conflict with +91 country code checks)
4. Login using registered email
5. Login using registered phone number (+91 or 10-digit format)
6. Reject incorrect password (401 Unauthorized)
7. Reject unregistered email/phone (404 Not Found)
8. Verify authenticated profile endpoint /api/auth/me using Bearer token
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import SessionLocal, Base, engine
from backend.models.user import User

client = TestClient(app)


class TestSahakarSahayakAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create fresh tables
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        # Clean up users table before each test
        db = SessionLocal()
        try:
            db.query(User).delete()
            db.commit()
        finally:
            db.close()

    def test_01_register_with_email_and_phone(self):
        """Register a new user with name, email, Indian phone number, and password."""
        payload = {
            "name": "Ramesh Kumar",
            "email": "ramesh@example.gov.in",
            "phone": "+919876543210",
            "password": "Password@123",
            "userType": "Cooperative Member",
            "preferredLanguage": "hi",
        }
        res = client.post("/api/auth/register", json=payload)
        self.assertEqual(res.status_code, 201, f"Expected 201, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], "ramesh@example.gov.in")
        self.assertEqual(data["user"]["phone"], "+919876543210")
        self.assertEqual(data["user"]["name"], "Ramesh Kumar")
        self.assertEqual(data["user"]["userType"], "Cooperative Member")
        self.assertEqual(data["user"]["preferredLanguage"], "hi")
        print("PASS: test_01_register_with_email_and_phone")

    def test_02_prevent_duplicate_email(self):
        """Prevent registration when email is already registered."""
        payload1 = {
            "name": "First User",
            "email": "duplicate@example.com",
            "phone": "+919800000001",
            "password": "Password123",
        }
        res1 = client.post("/api/auth/register", json=payload1)
        self.assertEqual(res1.status_code, 201)

        payload2 = {
            "name": "Second User",
            "email": "duplicate@example.com",  # Duplicate email
            "phone": "+919800000002",  # Different phone
            "password": "Password456",
        }
        res2 = client.post("/api/auth/register", json=payload2)
        self.assertEqual(res2.status_code, 409)
        self.assertIn("Email is already registered", res2.json().get("detail", ""))
        print("PASS: test_02_prevent_duplicate_email")

    def test_03_prevent_duplicate_phone(self):
        """Prevent registration when Indian phone number is already registered (+91 vs 10 digits)."""
        payload1 = {
            "name": "First User",
            "email": "first@example.com",
            "phone": "+91 9845012345",
            "password": "Password123",
        }
        res1 = client.post("/api/auth/register", json=payload1)
        self.assertEqual(res1.status_code, 201)

        payload2 = {
            "name": "Second User",
            "email": "second@example.com",  # Different email
            "phone": "+91 9845012345",  # Duplicate phone (same normalized)
            "password": "Password456",
        }
        res2 = client.post("/api/auth/register", json=payload2)
        self.assertEqual(res2.status_code, 409)
        self.assertIn("Phone number is already registered", res2.json().get("detail", ""))

        # Also test with 10 digits without +91 country prefix
        payload3 = {
            "name": "Third User",
            "email": "third@example.com",
            "phone": "9845012345",  # Same Indian phone without +91 prefix
            "password": "Password789",
        }
        res3 = client.post("/api/auth/register", json=payload3)
        self.assertEqual(res3.status_code, 409)
        self.assertIn("Phone number is already registered", res3.json().get("detail", ""))
        print("PASS: test_03_prevent_duplicate_phone")

    def test_04_login_using_email(self):
        """Authenticate successfully using registered email and password."""
        # Register user
        client.post("/api/auth/register", json={
            "name": "Sunita Sharma",
            "email": "sunita@example.com",
            "phone": "+919851122334",
            "password": "SecretPassword1",
        })

        # Login using email
        login_res = client.post("/api/auth/login", json={
            "identifier": "sunita@example.com",
            "password": "SecretPassword1",
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["email"], "sunita@example.com")
        self.assertEqual(data["user"]["name"], "Sunita Sharma")
        self.assertIn("token", data)
        print("PASS: test_04_login_using_email")

    def test_05_login_using_phone(self):
        """Authenticate successfully using registered Indian phone number (+91 or 10-digits) and password."""
        # Register user with +91 prefix
        client.post("/api/auth/register", json={
            "name": "Anil Verma",
            "email": "anil@example.com",
            "phone": "+919876501234",
            "password": "VermaPassword!1",
        })

        # Login using +91 formatted phone
        login_res = client.post("/api/auth/login", json={
            "identifier": "+91 98765 01234",
            "password": "VermaPassword!1",
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["phone"], "+919876501234")
        self.assertEqual(data["user"]["email"], "anil@example.com")
        self.assertIn("token", data)

        # Login using 10 digits directly without +91 prefix
        login_res2 = client.post("/api/auth/login", json={
            "identifier": "9876501234",
            "password": "VermaPassword!1",
        })
        self.assertEqual(login_res2.status_code, 200)
        self.assertTrue(login_res2.json().get("success"))
        print("PASS: test_05_login_using_phone")

    def test_06_reject_incorrect_password(self):
        """Reject authentication when password does not match."""
        client.post("/api/auth/register", json={
            "name": "Test User",
            "email": "wrongpwd@example.com",
            "phone": "+919811122233",
            "password": "CorrectPassword123",
        })

        res = client.post("/api/auth/login", json={
            "identifier": "wrongpwd@example.com",
            "password": "WrongPassword456",
        })
        self.assertEqual(res.status_code, 401)
        self.assertIn("Incorrect password", res.json().get("detail", ""))
        print("PASS: test_06_reject_incorrect_password")

    def test_07_reject_unregistered_email_and_phone(self):
        """Reject authentication when email or phone does not exist in database."""
        # Unregistered email
        res1 = client.post("/api/auth/login", json={
            "identifier": "unknown@example.com",
            "password": "SomePassword123",
        })
        self.assertEqual(res1.status_code, 404)
        self.assertIn("No account found", res1.json().get("detail", ""))

        # Unregistered phone
        res2 = client.post("/api/auth/login", json={
            "identifier": "+919899999999",
            "password": "SomePassword123",
        })
        self.assertEqual(res2.status_code, 404)
        self.assertIn("No account found", res2.json().get("detail", ""))
        print("PASS: test_07_reject_unregistered_email_and_phone")

    def test_08_verify_authenticated_endpoint_works(self):
        """Verify that protected route /api/auth/me returns valid user info with token."""
        reg_res = client.post("/api/auth/register", json={
            "name": "Bikash Thapa",
            "email": "bikash@example.gov.in",
            "phone": "+919841998877",
            "password": "ThapaPassword123",
            "userType": "Cooperative Manager",
        })
        token = reg_res.json()["token"]

        # Call /api/auth/me with Authorization header
        me_res = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_res.status_code, 200)
        user_info = me_res.json()
        self.assertEqual(user_info["email"], "bikash@example.gov.in")
        self.assertEqual(user_info["phone"], "+919841998877")
        self.assertEqual(user_info["name"], "Bikash Thapa")
        self.assertEqual(user_info["userType"], "Cooperative Manager")

        # Unauthenticated request must be rejected (401)
        unauth_res = client.get("/api/auth/me")
        self.assertEqual(unauth_res.status_code, 401)
        print("PASS: test_08_verify_authenticated_endpoint_works")


if __name__ == "__main__":
    unittest.main(verbosity=2)
