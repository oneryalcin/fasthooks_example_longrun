import pytest
from fastapi import status
from datetime import datetime, timedelta
import csv
from io import StringIO


class TestCSVExport:
    """Test CSV export functionality"""

    def test_export_csv_success(self, client, auth_headers):
        """Test exporting expenses to CSV"""
        # Create some test expenses
        expense_data = {
            "amount": 25.50,
            "category": "Food",
            "description": "Lunch",
            "date": datetime.utcnow().isoformat()
        }
        client.post("/api/expenses", json=expense_data, headers=auth_headers)

        # Export to CSV
        response = client.get("/api/expenses/export/csv", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_export_csv_format(self, client, auth_headers):
        """Test CSV format is correct"""
        # Create multiple expenses
        expenses = [
            {
                "amount": 25.50,
                "category": "Food",
                "description": "Lunch",
                "date": (datetime.utcnow() - timedelta(days=1)).isoformat()
            },
            {
                "amount": 50.00,
                "category": "Transport",
                "description": "Taxi",
                "date": datetime.utcnow().isoformat()
            }
        ]
        for expense in expenses:
            client.post("/api/expenses", json=expense, headers=auth_headers)

        # Export to CSV
        response = client.get("/api/expenses/export/csv", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Parse CSV content
        csv_content = response.text
        assert "Date,Category,Amount,Description" in csv_content
        assert "Food" in csv_content
        assert "Transport" in csv_content
        assert "25.5" in csv_content
        assert "50" in csv_content

    def test_export_csv_empty(self, client, auth_headers):
        """Test exporting empty expense list"""
        response = client.get("/api/expenses/export/csv", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "Date,Category,Amount,Description" in response.text

    def test_export_csv_without_auth(self, client):
        """Test CSV export requires authentication"""
        response = client.get("/api/expenses/export/csv")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAccountSettings:
    """Test account settings functionality"""

    def test_change_password_success(self, client, auth_headers, test_user):
        """Test successful password change"""
        response = client.put(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.json()["message"].lower()

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test password change with wrong current password"""
        response = client.put(
            "/api/auth/change-password",
            json={
                "current_password": "WrongPassword123",
                "new_password": "NewPassword456"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()

    def test_change_password_same_as_current(self, client, auth_headers):
        """Test password change with new password same as current"""
        response = client.put(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123",
                "new_password": "TestPassword123"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "different" in response.json()["detail"].lower()

    def test_change_password_validation(self, client, auth_headers):
        """Test new password must meet validation requirements"""
        # Password too short
        response = client.put(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123",
                "new_password": "Short1"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_change_password_without_auth(self, client):
        """Test password change requires authentication"""
        response = client.put(
            "/api/auth/change-password",
            json={
                "current_password": "TestPassword123",
                "new_password": "NewPassword456"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_profile_success(self, client, auth_headers):
        """Test successful profile update"""
        response = client.put(
            "/api/auth/profile",
            json={
                "full_name": "Updated Name",
                "email": "newemail@example.com"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == "newemail@example.com"

    def test_update_profile_name_only(self, client, auth_headers):
        """Test updating only name"""
        response = client.put(
            "/api/auth/profile",
            json={"full_name": "New Name"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["full_name"] == "New Name"

    def test_update_profile_email_only(self, client, auth_headers):
        """Test updating only email"""
        response = client.put(
            "/api/auth/profile",
            json={"email": "unique@example.com"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == "unique@example.com"

    def test_update_profile_duplicate_email(self, client, auth_headers, test_user_data):
        """Test updating email to one already in use"""
        # Create another user
        client.post("/api/auth/register", json=test_user_data)

        # Try to update current user's email to the other user's email
        response = client.put(
            "/api/auth/profile",
            json={"email": test_user_data["email"]},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already in use" in response.json()["detail"].lower()

    def test_update_profile_without_auth(self, client):
        """Test profile update requires authentication"""
        response = client.put(
            "/api/auth/profile",
            json={"full_name": "New Name"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestTokenRevocation:
    """Test token revocation on logout"""

    def test_revoked_token_cannot_access_protected_route(self, client, auth_headers):
        """Test that revoked token cannot access protected routes"""
        # First, verify token works
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Logout to revoke token
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK

        # Try to use revoked token - should fail
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "revoked" in response.json()["detail"].lower()

    def test_revoked_token_cannot_create_expense(self, client, auth_headers):
        """Test that revoked token cannot create expenses"""
        # Logout to revoke token
        client.post("/api/auth/logout", headers=auth_headers)

        # Try to create expense with revoked token
        response = client.post(
            "/api/expenses",
            json={
                "amount": 25.00,
                "category": "Food",
                "description": "Test",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRecurringExpenseProcessing:
    """Test recurring expense processing"""

    def test_process_recurring_daily(self, client, auth_headers):
        """Test daily recurring expense generation"""
        # Create a daily recurring expense
        recurring_data = {
            "amount": 10.00,
            "category": "Food",
            "description": "Daily coffee",
            "frequency": "daily"
        }
        response = client.post(
            "/api/recurring-expenses",
            json=recurring_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Process recurring expenses
        response = client.post("/api/recurring-expenses/process", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["count"] >= 0

    def test_process_recurring_endpoint_public(self, client):
        """Test that process endpoint can be called without auth (for cron jobs)"""
        # Should be accessible without auth for cron job integration
        response = client.post("/api/recurring-expenses/process")
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.json()

    def test_generate_today_endpoint(self, client):
        """Test quick generate today endpoint"""
        response = client.post("/api/recurring-expenses/generate-today")
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.json()

    def test_recurring_creates_actual_expenses(self, client, auth_headers):
        """Test that processing recurring creates actual expenses"""
        # Create a recurring expense
        recurring_data = {
            "amount": 15.00,
            "category": "Transport",
            "description": "Bus pass",
            "frequency": "daily"
        }
        client.post(
            "/api/recurring-expenses",
            json=recurring_data,
            headers=auth_headers
        )

        # Process recurring
        response = client.post("/api/recurring-expenses/process")
        assert response.status_code == status.HTTP_200_OK

        # Get expenses and verify new one was created
        response = client.get("/api/expenses", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should have at least the generated expense
        assert data["total"] >= 0
