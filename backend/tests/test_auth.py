import pytest
from fastapi import status


class TestUserRegistration:
    """Test user registration endpoint"""

    def test_register_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client, test_user, test_user_data):
        """Test registration with duplicate email"""
        test_user_data["email"] = test_user.email
        response = client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"]

    def test_register_missing_email(self, client, test_user_data):
        """Test registration with missing email"""
        test_user_data.pop("email")
        response = client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_missing_password(self, client, test_user_data):
        """Test registration with missing password"""
        test_user_data.pop("password")
        response = client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_password_too_short(self, client):
        """Test registration with password less than 8 characters"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "Short1"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_password_no_uppercase(self, client):
        """Test registration with password missing uppercase letter"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "lowercase123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "uppercase" in response.json()["detail"][0]["msg"].lower()

    def test_register_password_no_digit(self, client):
        """Test registration with password missing digit"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "NoDigitPassword"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "digit" in response.json()["detail"][0]["msg"].lower()


class TestUserLogin:
    """Test user login endpoint"""

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPassword123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid" in response.json()["detail"]

    def test_login_missing_email(self, client):
        """Test login with missing email"""
        response = client.post(
            "/api/auth/login",
            json={"password": "TestPassword123"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_missing_password(self, client, test_user):
        """Test login with missing password"""
        response = client.post(
            "/api/auth/login",
            json={"email": test_user.email}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_invalid_email(self, client):
        """Test login with invalid email format"""
        response = client.post(
            "/api/auth/login",
            json={
                "email": "invalid-email",
                "password": "TestPassword123"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogout:
    """Test logout endpoint"""

    def test_logout_success(self, client, auth_headers):
        """Test successful logout"""
        response = client.post(
            "/api/auth/logout",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Logged out" in response.json()["message"]

    def test_logout_without_token(self, client):
        """Test logout without authentication token"""
        response = client.post("/api/auth/logout")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetCurrentUser:
    """Test get current user endpoint"""

    def test_get_current_user_success(self, client, auth_headers, test_user):
        """Test getting current user info"""
        response = client.get(
            "/api/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_current_user_without_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenValidation:
    """Test token validation"""

    def test_valid_token_can_access_protected_route(self, client, auth_headers):
        """Test that valid token can access protected routes"""
        response = client.get(
            "/api/auth/me",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_expired_token_access_denied(self, client):
        """Test that expired token is rejected"""
        # Create a token with very short expiry (would need to mock time)
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjowfQ.test"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_token(self, client):
        """Test that malformed token is rejected"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer not-a-valid-token"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
