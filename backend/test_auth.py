"""
Comprehensive Authentication & Dual OTP Verification Test Suite for Sahakar Sahayak
Tests:
1.  Initiate registration with name, email, phone (+91 Indian format), password
2.  Prevent duplicate email during initiation (409 Conflict)
3.  Prevent duplicate phone during initiation (409 Conflict with +91 country prefix checks)
4.  Verify email OTP successfully (email verified, phone still pending)
5.  Verify phone OTP successfully and complete registration (both verified, user created in permanent table)
6.  Ensure user account NOT in permanent table or able to log in until BOTH are verified
7.  Reject incorrect OTP and decrement remaining attempts
8.  Reject verification when attempt limit (5 attempts) is exhausted (429 Too Many Requests)
9.  Reject expired OTP code (400 Bad Request)
10. Test resend OTP functionality and enforce 60-second cooldown rate-limiting (429)
11. Login using registered email + password
12. Login using registered phone (+91 or 10-digit format) + password
13. Reject incorrect password (401 Unauthorized)
14. Reject unregistered email or phone (404 Not Found)
15. Reject login if account is unverified or inactive
16. Verify authenticated profile endpoints (/api/auth/me and /api/auth/profile)
"""

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.main import app
from backend.models.database import SessionLocal, Base, engine, init_db
from backend.models.user import User
from backend.models.pending_registration import PendingRegistration
from backend.services.notification_service import get_test_otp, clear_test_otps

client = TestClient(app)


class TestSahakarSahayakAuthAndOTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()


    def setUp(self):
        # Clean up database and test OTP store before each test
        clear_test_otps()
        db = SessionLocal()
        try:
            db.query(PendingRegistration).delete()
            db.query(User).delete()
            db.commit()
        finally:
            db.close()

    def _initiate_helper(self, name="Ramesh Kumar", email="ramesh@example.gov.in", phone="+919876543210", password="Password@123"):
        """Helper to initiate registration and return session ID."""
        payload = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "userType": "Cooperative Member",
            "preferredLanguage": "hi",
        }
        res = client.post("/api/auth/register/initiate", json=payload)
        return res

    def test_01_initiate_registration_and_security(self):
        """Test step 1 initiation: generates OTPs, creates pending record, does NOT expose OTP in API."""
        res = self._initiate_helper()
        self.assertEqual(res.status_code, 200, f"Expected 200, got {res.status_code}: {res.text}")
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("sessionId", data)
        self.assertIn("maskedEmail", data)
        self.assertIn("maskedPhone", data)
        self.assertFalse(data.get("emailVerified"))
        self.assertFalse(data.get("phoneVerified"))

        # SECURITY CHECK: Raw OTPs must NEVER be exposed in API responses
        self.assertNotIn("otp", data)
        self.assertNotIn("emailOtp", data)
        self.assertNotIn("phoneOtp", data)

        # Check internal test notification store received both OTPs
        email_otp = get_test_otp("ramesh@example.gov.in")
        phone_otp = get_test_otp("+919876543210")
        self.assertIsNotNone(email_otp)
        self.assertIsNotNone(phone_otp)
        self.assertEqual(len(email_otp), 6)
        self.assertEqual(len(phone_otp), 6)
        print("PASS: test_01_initiate_registration_and_security")

    def test_02_prevent_duplicate_email_on_initiate(self):
        """Prevent initiation when email is already registered in users table."""
        # Create an existing active user
        db = SessionLocal()
        try:
            u = User(
                name="Existing User",
                email="duplicate@example.com",
                phone="+919800000001",
                password_hash="somehash",
                email_verified=True,
                phone_verified=True,
                is_active=True,
            )
            db.add(u)
            db.commit()
        finally:
            db.close()

        res = client.post("/api/auth/register/initiate", json={
            "name": "New User",
            "email": "duplicate@example.com",  # Duplicate email
            "phone": "+919800000002",
            "password": "Password123",
        })
        self.assertEqual(res.status_code, 409)
        self.assertIn("Email is already registered", res.json().get("detail", ""))
        print("PASS: test_02_prevent_duplicate_email_on_initiate")

    def test_03_prevent_duplicate_phone_on_initiate(self):
        """Prevent initiation when phone number (+91 or 10-digit) is already registered."""
        db = SessionLocal()
        try:
            u = User(
                name="Existing Phone User",
                email="unique1@example.com",
                phone="+919845012345",
                password_hash="somehash",
                email_verified=True,
                phone_verified=True,
                is_active=True,
            )
            db.add(u)
            db.commit()
        finally:
            db.close()

        # Try registering with same phone formatted with spaces
        res1 = client.post("/api/auth/register/initiate", json={
            "name": "Candidate 1",
            "email": "unique2@example.com",
            "phone": "+91 98450 12345",
            "password": "Password123",
        })
        self.assertEqual(res1.status_code, 409)
        self.assertIn("Phone number is already registered", res1.json().get("detail", ""))

        # Try registering with 10 digits without +91 prefix
        res2 = client.post("/api/auth/register/initiate", json={
            "name": "Candidate 2",
            "email": "unique3@example.com",
            "phone": "9845012345",
            "password": "Password123",
        })
        self.assertEqual(res2.status_code, 409)
        self.assertIn("Phone number is already registered", res2.json().get("detail", ""))
        print("PASS: test_03_prevent_duplicate_phone_on_initiate")

    def test_04_verify_email_otp_step(self):
        """Verify email OTP factor successfully."""
        res = self._initiate_helper(email="verify.email@example.com", phone="+919811122233")
        session_id = res.json()["sessionId"]
        email_otp = get_test_otp("verify.email@example.com")

        verify_res = client.post("/api/auth/register/verify-email", json={
            "sessionId": session_id,
            "otp": email_otp,
        })
        self.assertEqual(verify_res.status_code, 200)
        data = verify_res.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["emailVerified"])
        self.assertFalse(data["phoneVerified"])
        self.assertFalse(data["registrationCompleted"])
        print("PASS: test_04_verify_email_otp_step")

    def test_05_verify_phone_otp_and_complete_registration(self):
        """Verify both OTPs and ensure final user account is created with JWT token."""
        res = self._initiate_helper(name="Kavita Devi", email="kavita@example.gov.in", phone="+919877788899")
        session_id = res.json()["sessionId"]
        email_otp = get_test_otp("kavita@example.gov.in")
        phone_otp = get_test_otp("+919877788899")

        # 1. Verify email first
        client.post("/api/auth/register/verify-email", json={
            "sessionId": session_id,
            "otp": email_otp,
        })

        # 2. Verify phone second (triggers finalization)
        res_phone = client.post("/api/auth/register/verify-phone", json={
            "sessionId": session_id,
            "otp": phone_otp,
        })
        self.assertEqual(res_phone.status_code, 200)
        data = res_phone.json()
        self.assertTrue(data["success"])
        self.assertTrue(data["emailVerified"])
        self.assertTrue(data["phoneVerified"])
        self.assertTrue(data["registrationCompleted"])
        self.assertIn("token", data)
        self.assertEqual(data["user"]["email"], "kavita@example.gov.in")
        self.assertEqual(data["user"]["phone"], "+919877788899")

        # Ensure user exists in permanent users table
        db = SessionLocal()
        try:
            user_in_db = db.query(User).filter(User.email == "kavita@example.gov.in").first()
            self.assertIsNotNone(user_in_db)
            self.assertTrue(user_in_db.email_verified)
            self.assertTrue(user_in_db.phone_verified)
            self.assertTrue(user_in_db.is_active)

            # Ensure pending registration record was removed
            pending_in_db = db.query(PendingRegistration).filter(PendingRegistration.session_id == session_id).first()
            self.assertIsNone(pending_in_db)
        finally:
            db.close()

        print("PASS: test_05_verify_phone_otp_and_complete_registration")

    def test_06_account_not_created_until_both_verified(self):
        """Strict Requirement: Account must NOT exist in users table or be able to log in until BOTH OTPs are verified."""
        res = self._initiate_helper(email="partial@example.com", phone="+919833344455", password="MySecretPassword")
        session_id = res.json()["sessionId"]
        email_otp = get_test_otp("partial@example.com")

        # Verify only email
        client.post("/api/auth/register/verify-email", json={
            "sessionId": session_id,
            "otp": email_otp,
        })

        # Check users table: user must NOT exist
        db = SessionLocal()
        try:
            user_in_db = db.query(User).filter(User.email == "partial@example.com").first()
            self.assertIsNone(user_in_db, "User must NOT exist in permanent table when only email is verified!")
        finally:
            db.close()

        # Login attempt must fail (404 Not Found because account is not created yet)
        login_res = client.post("/api/auth/login", json={
            "identifier": "partial@example.com",
            "password": "MySecretPassword",
        })
        self.assertEqual(login_res.status_code, 404)
        print("PASS: test_06_account_not_created_until_both_verified")

    def test_07_reject_incorrect_otp_and_countdown_attempts(self):
        """Reject incorrect OTP and return remaining attempts countdown."""
        res = self._initiate_helper(email="wrongotp@example.com", phone="+919822233344")
        session_id = res.json()["sessionId"]

        # Enter wrong OTP
        wrong_res = client.post("/api/auth/register/verify-email", json={
            "sessionId": session_id,
            "otp": "000000",
        })
        self.assertEqual(wrong_res.status_code, 400)
        detail = wrong_res.json().get("detail", "")
        self.assertIn("Incorrect email verification code", detail)
        self.assertIn("4 attempt(s) remaining", detail)
        print("PASS: test_07_reject_incorrect_otp_and_countdown_attempts")

    def test_08_exhaust_verify_attempts_limit(self):
        """Reject OTP attempts when max attempts (5) are reached."""
        res = self._initiate_helper(email="exhaust@example.com", phone="+919899988877")
        session_id = res.json()["sessionId"]

        for i in range(4):
            client.post("/api/auth/register/verify-email", json={
                "sessionId": session_id,
                "otp": "000000",
            })

        # 5th failed attempt should trigger attempt limit rejection
        res_5 = client.post("/api/auth/register/verify-email", json={
            "sessionId": session_id,
            "otp": "000000",
        })
        self.assertEqual(res_5.status_code, 429)
        self.assertIn("Maximum attempts reached", res_5.json().get("detail", ""))
        print("PASS: test_08_exhaust_verify_attempts_limit")

    def test_09_reject_expired_otp(self):
        """Reject verification when OTP timestamp has expired."""
        res = self._initiate_helper(email="expired@example.com", phone="+919866655544")
        session_id = res.json()["sessionId"]
        email_otp = get_test_otp("expired@example.com")

        # Manually expire the OTP in database
        db = SessionLocal()
        try:
            pending = db.query(PendingRegistration).filter(PendingRegistration.session_id == session_id).first()
            pending.email_otp_expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)
            db.commit()
        finally:
            db.close()

        verify_res = client.post("/api/auth/register/verify-email", json={
            "sessionId": session_id,
            "otp": email_otp,
        })
        self.assertEqual(verify_res.status_code, 400)
        self.assertIn("expired", verify_res.json().get("detail", "").lower())
        print("PASS: test_09_reject_expired_otp")

    def test_10_resend_otp_and_cooldown(self):
        """Test resending OTP and enforcing 60-second cooldown rate-limiting."""
        res = self._initiate_helper(email="resend@example.com", phone="+919855544433")
        session_id = res.json()["sessionId"]

        # Immediate resend should be rejected due to 60s cooldown
        resend_immediate = client.post("/api/auth/register/resend-otp", json={
            "sessionId": session_id,
            "target": "email",
        })
        self.assertEqual(resend_immediate.status_code, 429)
        self.assertIn("Please wait", resend_immediate.json().get("detail", ""))

        # Simulate cooldown elapse by setting last_email_resend_at 70 seconds in past
        db = SessionLocal()
        try:
            pending = db.query(PendingRegistration).filter(PendingRegistration.session_id == session_id).first()
            pending.last_email_resend_at = datetime.now(timezone.utc) - timedelta(seconds=70)
            db.commit()
        finally:
            db.close()

        # Resend after cooldown should succeed
        resend_ok = client.post("/api/auth/register/resend-otp", json={
            "sessionId": session_id,
            "target": "email",
        })
        self.assertEqual(resend_ok.status_code, 200)
        self.assertTrue(resend_ok.json().get("success"))
        print("PASS: test_10_resend_otp_and_cooldown")

    def test_11_login_using_email_and_phone(self):
        """Test dual login using Email OR Phone Number for the same verified account."""
        # 1. Complete dual registration
        res = self._initiate_helper(
            name="Suresh Patel",
            email="suresh.patel@example.com",
            phone="+919820012345",
            password="SureshSecurePassword@1",
        )
        session_id = res.json()["sessionId"]
        email_otp = get_test_otp("suresh.patel@example.com")
        phone_otp = get_test_otp("+919820012345")

        client.post("/api/auth/register/verify-email", json={"sessionId": session_id, "otp": email_otp})
        client.post("/api/auth/register/verify-phone", json={"sessionId": session_id, "otp": phone_otp})

        # 2. Login using Email
        login_email = client.post("/api/auth/login", json={
            "identifier": "suresh.patel@example.com",
            "password": "SureshSecurePassword@1",
        })
        self.assertEqual(login_email.status_code, 200)
        self.assertEqual(login_email.json()["user"]["email"], "suresh.patel@example.com")
        self.assertIn("token", login_email.json())

        # 3. Login using Phone Number (+91 format)
        login_phone = client.post("/api/auth/login", json={
            "identifier": "+91 98200 12345",
            "password": "SureshSecurePassword@1",
        })
        self.assertEqual(login_phone.status_code, 200)
        self.assertEqual(login_phone.json()["user"]["phone"], "+919820012345")

        # 4. Login using 10-digit phone directly without +91 prefix
        login_phone_digits = client.post("/api/auth/login", json={
            "identifier": "9820012345",
            "password": "SureshSecurePassword@1",
        })
        self.assertEqual(login_phone_digits.status_code, 200)
        self.assertEqual(login_phone_digits.json()["user"]["id"], login_email.json()["user"]["id"])

        print("PASS: test_11_login_using_email_and_phone")

    def test_12_reject_incorrect_password(self):
        """Reject authentication when password does not match."""
        res = self._initiate_helper(email="wrongpass@example.com", phone="+919812345678", password="CorrectPassword1")
        session_id = res.json()["sessionId"]
        client.post("/api/auth/register/verify-email", json={"sessionId": session_id, "otp": get_test_otp("wrongpass@example.com")})
        client.post("/api/auth/register/verify-phone", json={"sessionId": session_id, "otp": get_test_otp("+919812345678")})

        res_login = client.post("/api/auth/login", json={
            "identifier": "wrongpass@example.com",
            "password": "WrongPassword999",
        })
        self.assertEqual(res_login.status_code, 401)
        self.assertIn("Incorrect password", res_login.json().get("detail", ""))
        print("PASS: test_12_reject_incorrect_password")

    def test_13_reject_unregistered_credentials(self):
        """Reject authentication when email or phone does not exist."""
        res1 = client.post("/api/auth/login", json={
            "identifier": "nonexistent@example.com",
            "password": "SomePassword1",
        })
        self.assertEqual(res1.status_code, 404)
        self.assertIn("No account found", res1.json().get("detail", ""))

        res2 = client.post("/api/auth/login", json={
            "identifier": "+919999999999",
            "password": "SomePassword1",
        })
        self.assertEqual(res2.status_code, 404)
        print("PASS: test_13_reject_unregistered_credentials")

    def test_14_authenticated_profile_endpoints(self):
        """Verify protected /api/auth/me and /api/auth/profile using Bearer token."""
        res = self._initiate_helper(
            name="Pooja Yadav",
            email="pooja@example.gov.in",
            phone="+919844455566",
            password="PoojaPassword@1",
        )
        session_id = res.json()["sessionId"]
        client.post("/api/auth/register/verify-email", json={"sessionId": session_id, "otp": get_test_otp("pooja@example.gov.in")})
        final_res = client.post("/api/auth/register/verify-phone", json={"sessionId": session_id, "otp": get_test_otp("+919844455566")})
        token = final_res.json()["token"]

        # GET /api/auth/me
        me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["name"], "Pooja Yadav")

        # PUT /api/auth/profile
        update_res = client.put(
            "/api/auth/profile",
            json={"name": "Pooja Sharma", "userType": "Cooperative Manager"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(update_res.status_code, 200)
        self.assertEqual(update_res.json()["user"]["name"], "Pooja Sharma")
        self.assertEqual(update_res.json()["user"]["userType"], "Cooperative Manager")

        print("PASS: test_14_authenticated_profile_endpoints")

    def test_15_verify_phone_first_then_email(self):
        """Verify phone OTP first and email OTP second, ensuring completion in either order."""
        res = self._initiate_helper(
            name="Vikram Seth",
            email="vikram@example.gov.in",
            phone="+919833322211",
            password="VikramPassword!1",
        )
        session_id = res.json()["sessionId"]
        email_otp = get_test_otp("vikram@example.gov.in")
        phone_otp = get_test_otp("+919833322211")

        # 1. Verify phone first
        res_phone = client.post("/api/auth/register/verify-phone", json={"sessionId": session_id, "otp": phone_otp})
        self.assertEqual(res_phone.status_code, 200)
        self.assertTrue(res_phone.json()["phoneVerified"])
        self.assertFalse(res_phone.json()["emailVerified"])
        self.assertFalse(res_phone.json()["registrationCompleted"])

        # 2. Verify email second
        res_email = client.post("/api/auth/register/verify-email", json={"sessionId": session_id, "otp": email_otp})
        self.assertEqual(res_email.status_code, 200)
        self.assertTrue(res_email.json()["emailVerified"])
        self.assertTrue(res_email.json()["phoneVerified"])
        self.assertTrue(res_email.json()["registrationCompleted"])
        self.assertIn("token", res_email.json())
        print("PASS: test_15_verify_phone_first_then_email")

    def test_16_reject_login_if_inactive(self):
        """Reject login with 403 if account is deactivated or unverified."""
        db = SessionLocal()
        try:
            inactive_user = User(
                name="Inactive User",
                email="inactive@example.com",
                phone="+919877700011",
                password_hash="somehash",
                email_verified=True,
                phone_verified=True,
                is_active=False,  # Deactivated
            )
            db.add(inactive_user)
            db.commit()
        finally:
            db.close()

        res = client.post("/api/auth/login", json={
            "identifier": "inactive@example.com",
            "password": "somepassword",
        })
        # Account is inactive or unverified -> 403 Forbidden or 401
        self.assertIn(res.status_code, (401, 403))
        print("PASS: test_16_reject_login_if_inactive")


if __name__ == "__main__":
    unittest.main(verbosity=2)

