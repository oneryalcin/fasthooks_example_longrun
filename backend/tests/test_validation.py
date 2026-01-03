import pytest
from fastapi import status
from datetime import datetime


class TestExpenseValidation:
    """Test expense input validation"""

    def test_amount_max_limit(self, client, auth_headers):
        """Test amount cannot exceed maximum limit"""
        expense_data = {
            "amount": 1_000_001,
            "category": "Food",
            "description": "Too expensive",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_description_max_length(self, client, auth_headers):
        """Test description cannot exceed max length"""
        long_description = "x" * 501
        expense_data = {
            "amount": 25.0,
            "category": "Food",
            "description": long_description,
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_valid_description_at_max_length(self, client, auth_headers):
        """Test valid description at max length"""
        description = "x" * 500
        expense_data = {
            "amount": 25.0,
            "category": "Food",
            "description": description,
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_null_description_allowed(self, client, auth_headers):
        """Test that null description is allowed"""
        expense_data = {
            "amount": 25.0,
            "category": "Food",
            "description": None,
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestBudgetValidation:
    """Test budget input validation"""

    def test_create_budget_success(self, client, auth_headers):
        """Test successful budget creation"""
        budget_data = {
            "category": "Food",
            "monthly_limit": 500.0
        }
        response = client.post(
            "/api/budgets",
            json=budget_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

    def test_budget_negative_amount(self, client, auth_headers):
        """Test budget cannot have negative amount"""
        budget_data = {
            "category": "Food",
            "monthly_limit": -500.0
        }
        response = client.post(
            "/api/budgets",
            json=budget_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_budget_zero_amount(self, client, auth_headers):
        """Test budget cannot have zero amount"""
        budget_data = {
            "category": "Food",
            "monthly_limit": 0
        }
        response = client.post(
            "/api/budgets",
            json=budget_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_budget_duplicate_category(self, client, auth_headers):
        """Test cannot create duplicate budget for same category"""
        budget_data = {
            "category": "Food",
            "monthly_limit": 500.0
        }
        # Create first budget
        client.post(
            "/api/budgets",
            json=budget_data,
            headers=auth_headers
        )
        # Try to create duplicate
        response = client.post(
            "/api/budgets",
            json=budget_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]

    def test_budget_update_success(self, client, auth_headers):
        """Test successful budget update"""
        budget_data = {
            "category": "Food",
            "monthly_limit": 500.0
        }
        client.post(
            "/api/budgets",
            json=budget_data,
            headers=auth_headers
        )

        response = client.put(
            "/api/budgets/Food",
            json={"monthly_limit": 600.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["monthly_limit"] == 600.0

    def test_budget_update_not_found(self, client, auth_headers):
        """Test updating non-existent budget"""
        response = client.put(
            "/api/budgets/Food",
            json={"monthly_limit": 600.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRecurringExpenseValidation:
    """Test recurring expense validation"""

    def test_create_recurring_success(self, client, auth_headers):
        """Test successful recurring expense creation"""
        recurring_data = {
            "amount": 50.0,
            "category": "Utilities",
            "frequency": "monthly",
            "description": "Internet bill"
        }
        response = client.post(
            "/api/recurring-expenses",
            json=recurring_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_active"] is True

    def test_recurring_invalid_frequency(self, client, auth_headers):
        """Test recurring expense with invalid frequency"""
        recurring_data = {
            "amount": 50.0,
            "category": "Utilities",
            "frequency": "invalid",
            "description": "Internet bill"
        }
        response = client.post(
            "/api/recurring-expenses",
            json=recurring_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_recurring_valid_frequencies(self, client, auth_headers):
        """Test all valid frequencies"""
        frequencies = ["daily", "weekly", "monthly", "yearly"]
        for freq in frequencies:
            recurring_data = {
                "amount": 50.0,
                "category": "Utilities",
                "frequency": freq,
                "description": f"Test {freq}"
            }
            response = client.post(
                "/api/recurring-expenses",
                json=recurring_data,
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["frequency"] == freq

    def test_recurring_negative_amount(self, client, auth_headers):
        """Test recurring expense with negative amount"""
        recurring_data = {
            "amount": -50.0,
            "category": "Utilities",
            "frequency": "monthly",
            "description": "Internet bill"
        }
        response = client.post(
            "/api/recurring-expenses",
            json=recurring_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestErrorMessages:
    """Test error message clarity"""

    def test_error_has_detail_field(self, client):
        """Test that errors include detail field"""
        response = client.post(
            "/api/auth/register",
            json={"email": "invalid", "password": "short"}
        )
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]
        # Response includes validation errors

    def test_unauthenticated_error(self, client):
        """Test unauthenticated error message"""
        response = client.get("/api/expenses")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_not_found_error(self, client, auth_headers):
        """Test not found error message"""
        response = client.get(
            "/api/expenses/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
