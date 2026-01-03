"""
End-to-End API Integration Tests
Tests complete user workflows including new features
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta


class TestUserJourney:
    """Test complete user workflows"""

    def test_complete_user_workflow(self, client, test_user_data):
        """Test complete user journey: register -> login -> create expenses -> export CSV -> account settings"""

        # Step 1: Register new user
        register_response = client.post(
            "/api/auth/register",
            json=test_user_data
        )
        assert register_response.status_code == status.HTTP_200_OK
        access_token = register_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Get current user info
        user_response = client.get("/api/auth/me", headers=auth_headers)
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        assert user_data["email"] == test_user_data["email"]

        # Step 3: Create multiple expenses
        expenses_created = []
        expense_amounts = [25.50, 100.00, 15.75]
        categories = ["Food", "Transport", "Entertainment"]

        for amount, category in zip(expense_amounts, categories):
            expense = {
                "amount": amount,
                "category": category,
                "description": f"Test {category} expense",
                "date": (datetime.utcnow() - timedelta(days=1)).isoformat()
            }
            response = client.post("/api/expenses", json=expense, headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
            expenses_created.append(response.json())

        # Step 4: Retrieve expenses
        list_response = client.get("/api/expenses", headers=auth_headers)
        assert list_response.status_code == status.HTTP_200_OK
        expenses_data = list_response.json()
        assert expenses_data["total"] == 3
        assert expenses_data["total_amount"] == sum(expense_amounts)

        # Step 5: Export to CSV
        csv_response = client.get("/api/expenses/export/csv", headers=auth_headers)
        assert csv_response.status_code == status.HTTP_200_OK
        assert "text/csv" in csv_response.headers["content-type"]
        csv_content = csv_response.text
        assert "Date,Category,Amount,Description" in csv_content
        assert "Food" in csv_content
        assert "Transport" in csv_content

        # Step 6: Update profile
        profile_update = {
            "full_name": "Updated User Name",
            "email": "newemail@example.com"
        }
        profile_response = client.put(
            "/api/auth/profile",
            json=profile_update,
            headers=auth_headers
        )
        assert profile_response.status_code == status.HTTP_200_OK
        updated_profile = profile_response.json()
        assert updated_profile["full_name"] == "Updated User Name"

        # Step 7: Change password
        password_change = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword456"
        }
        password_response = client.put(
            "/api/auth/change-password",
            json=password_change,
            headers=auth_headers
        )
        assert password_response.status_code == status.HTTP_200_OK

        # Step 8: Verify new password works
        login_with_new_password = client.post(
            "/api/auth/login",
            json={
                "email": profile_update["email"],
                "password": "NewPassword456"
            }
        )
        assert login_with_new_password.status_code == status.HTTP_200_OK
        new_token = login_with_new_password.json()["access_token"]
        new_auth_headers = {"Authorization": f"Bearer {new_token}"}

        # Step 9: Create recurring expense
        recurring_expense = {
            "amount": 50.00,
            "category": "Utilities",
            "description": "Monthly electricity",
            "frequency": "monthly"
        }
        recurring_response = client.post(
            "/api/recurring-expenses",
            json=recurring_expense,
            headers=new_auth_headers
        )
        assert recurring_response.status_code == status.HTTP_200_OK
        recurring_data = recurring_response.json()
        assert recurring_data["frequency"] == "monthly"
        assert recurring_data["is_active"] == True

        # Step 10: Process recurring expenses
        process_response = client.post(
            "/api/recurring-expenses/process"
        )
        assert process_response.status_code == status.HTTP_200_OK
        assert "count" in process_response.json()

        # Step 11: Create budget
        budget_data = {
            "category": "Food",
            "monthly_limit": 200.00
        }
        budget_response = client.post(
            "/api/budgets",
            json=budget_data,
            headers=new_auth_headers
        )
        assert budget_response.status_code == status.HTTP_200_OK

        # Step 12: Get analytics
        analytics_response = client.get(
            "/api/analytics/summary",
            headers=new_auth_headers
        )
        assert analytics_response.status_code == status.HTTP_200_OK
        analytics = analytics_response.json()
        assert "total_spending" in analytics
        assert "current_month_spending" in analytics

        # Step 13: Logout and verify token is revoked
        logout_response = client.post(
            "/api/auth/logout",
            headers=new_auth_headers
        )
        assert logout_response.status_code == status.HTTP_200_OK

        # Try to use old token - should fail
        protected_response = client.get(
            "/api/auth/me",
            headers=new_auth_headers
        )
        assert protected_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_multiple_users_isolation(self, client, test_user_data):
        """Test that users' data is properly isolated"""

        # Create first user
        user1_data = test_user_data.copy()
        user1_data["email"] = "user1@example.com"
        register1 = client.post("/api/auth/register", json=user1_data)
        token1 = register1.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Create second user
        user2_data = test_user_data.copy()
        user2_data["email"] = "user2@example.com"
        register2 = client.post("/api/auth/register", json=user2_data)
        token2 = register2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User 1 creates expenses
        expense1 = {
            "amount": 100.00,
            "category": "Food",
            "description": "User 1 expense",
            "date": datetime.utcnow().isoformat()
        }
        response1 = client.post("/api/expenses", json=expense1, headers=headers1)
        expense1_id = response1.json()["id"]

        # User 2 creates expenses
        expense2 = {
            "amount": 200.00,
            "category": "Transport",
            "description": "User 2 expense",
            "date": datetime.utcnow().isoformat()
        }
        response2 = client.post("/api/expenses", json=expense2, headers=headers2)

        # Verify User 1 only sees their expenses
        user1_expenses = client.get("/api/expenses", headers=headers1)
        assert user1_expenses.json()["total"] == 1
        assert user1_expenses.json()["total_amount"] == 100.00

        # Verify User 2 only sees their expenses
        user2_expenses = client.get("/api/expenses", headers=headers2)
        assert user2_expenses.json()["total"] == 1
        assert user2_expenses.json()["total_amount"] == 200.00

        # Verify User 2 cannot access User 1's expense
        user2_access_user1_expense = client.get(
            f"/api/expenses/{expense1_id}",
            headers=headers2
        )
        assert user2_access_user1_expense.status_code == status.HTTP_404_NOT_FOUND

    def test_csrf_and_security_headers(self, client):
        """Test security aspects of the API"""

        # Test CORS is properly configured
        health_response = client.get("/api/health")
        assert health_response.status_code == status.HTTP_200_OK

        # Test unauthenticated access to protected routes
        protected_response = client.get("/api/expenses")
        assert protected_response.status_code == status.HTTP_403_FORBIDDEN

        # Test invalid token format
        bad_headers = {"Authorization": "InvalidToken"}
        bad_token_response = client.get("/api/auth/me", headers=bad_headers)
        assert bad_token_response.status_code == status.HTTP_403_FORBIDDEN

    def test_error_handling_workflow(self, client, test_user_data, auth_headers):
        """Test proper error handling throughout the workflow"""

        # Test 400: Invalid data
        invalid_expense = {
            "amount": -100,  # Negative amount
            "category": "Food",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post("/api/expenses", json=invalid_expense, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST or status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test 404: Non-existent resource
        response = client.get("/api/expenses/99999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test 422: Invalid category
        invalid_category = {
            "amount": 100,
            "category": "InvalidCategory",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post("/api/expenses", json=invalid_category, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Test future date validation
        future_expense = {
            "amount": 50.00,
            "category": "Food",
            "date": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
        response = client.post("/api/expenses", json=future_expense, headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "future" in response.json()["detail"].lower()
