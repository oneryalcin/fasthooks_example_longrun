import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import Expense


class TestCreateExpense:
    """Test expense creation"""

    def test_create_expense_success(self, client, auth_headers):
        """Test successful expense creation"""
        expense_data = {
            "amount": 25.50,
            "category": "Food",
            "description": "Lunch",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 25.50
        assert data["category"] == "Food"
        assert data["description"] == "Lunch"

    def test_create_expense_without_auth(self, client):
        """Test expense creation without authentication"""
        expense_data = {
            "amount": 25.50,
            "category": "Food",
            "description": "Lunch",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_expense_negative_amount(self, client, auth_headers):
        """Test expense creation with negative amount"""
        expense_data = {
            "amount": -25.50,
            "category": "Food",
            "description": "Lunch",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_expense_zero_amount(self, client, auth_headers):
        """Test expense creation with zero amount"""
        expense_data = {
            "amount": 0,
            "category": "Food",
            "description": "Lunch",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_expense_invalid_category(self, client, auth_headers):
        """Test expense creation with invalid category"""
        expense_data = {
            "amount": 25.50,
            "category": "InvalidCategory",
            "description": "Lunch",
            "date": datetime.utcnow().isoformat()
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_expense_future_date(self, client, auth_headers):
        """Test expense creation with future date"""
        future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
        expense_data = {
            "amount": 25.50,
            "category": "Food",
            "description": "Lunch",
            "date": future_date
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "future" in response.json()["detail"].lower()

    def test_create_expense_missing_required_fields(self, client, auth_headers):
        """Test expense creation with missing required fields"""
        expense_data = {
            "amount": 25.50,
            "category": "Food"
        }
        response = client.post(
            "/api/expenses",
            json=expense_data,
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_expense_with_all_categories(self, client, auth_headers):
        """Test expense creation with each category"""
        categories = ["Food", "Transport", "Entertainment", "Utilities", "Health", "Shopping", "Other"]
        for category in categories:
            expense_data = {
                "amount": 25.50,
                "category": category,
                "description": f"Test {category}",
                "date": datetime.utcnow().isoformat()
            }
            response = client.post(
                "/api/expenses",
                json=expense_data,
                headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["category"] == category


class TestGetExpenses:
    """Test getting expenses"""

    def test_get_expenses_empty(self, client, auth_headers):
        """Test getting expenses when none exist"""
        response = client.get(
            "/api/expenses",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["total_amount"] == 0
        assert len(data["items"]) == 0

    def test_get_expenses_with_data(self, client, auth_headers, db, test_user):
        """Test getting expenses with data"""
        # Create expenses
        for i in range(3):
            expense_data = {
                "amount": 10.0 + i,
                "category": "Food",
                "description": f"Expense {i}",
                "date": datetime.utcnow().isoformat()
            }
            client.post(
                "/api/expenses",
                json=expense_data,
                headers=auth_headers
            )

        response = client.get(
            "/api/expenses",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert data["total_amount"] == pytest.approx(33.0, 0.01)

    def test_get_expenses_filter_by_category(self, client, auth_headers):
        """Test filtering expenses by category"""
        # Create expenses
        client.post(
            "/api/expenses",
            json={
                "amount": 25.0,
                "category": "Food",
                "description": "Lunch",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )
        client.post(
            "/api/expenses",
            json={
                "amount": 50.0,
                "category": "Transport",
                "description": "Taxi",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )

        response = client.get(
            "/api/expenses",
            params={"category": "Food"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "Food"

    def test_get_expenses_filter_by_date_range(self, client, auth_headers):
        """Test filtering expenses by date range"""
        now = datetime.utcnow()
        old_date = (now - timedelta(days=30)).isoformat()
        recent_date = now.isoformat()

        # Create old expense
        client.post(
            "/api/expenses",
            json={
                "amount": 25.0,
                "category": "Food",
                "description": "Old",
                "date": old_date
            },
            headers=auth_headers
        )

        # Create recent expense
        client.post(
            "/api/expenses",
            json={
                "amount": 50.0,
                "category": "Transport",
                "description": "Recent",
                "date": recent_date
            },
            headers=auth_headers
        )

        # Filter recent only
        response = client.get(
            "/api/expenses",
            params={"start_date": (now - timedelta(days=7)).isoformat()},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1

    def test_get_expenses_without_auth(self, client):
        """Test getting expenses without authentication"""
        response = client.get("/api/expenses")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetExpense:
    """Test getting single expense"""

    def test_get_expense_success(self, client, auth_headers):
        """Test successful expense retrieval"""
        # Create expense
        create_response = client.post(
            "/api/expenses",
            json={
                "amount": 25.0,
                "category": "Food",
                "description": "Lunch",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Get expense
        response = client.get(
            f"/api/expenses/{expense_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == expense_id

    def test_get_expense_not_found(self, client, auth_headers):
        """Test getting non-existent expense"""
        response = client.get(
            "/api/expenses/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateExpense:
    """Test updating expenses"""

    def test_update_expense_success(self, client, auth_headers):
        """Test successful expense update"""
        # Create expense
        create_response = client.post(
            "/api/expenses",
            json={
                "amount": 25.0,
                "category": "Food",
                "description": "Lunch",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Update expense
        response = client.put(
            f"/api/expenses/{expense_id}",
            json={
                "amount": 35.0,
                "description": "Expensive lunch"
            },
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["amount"] == 35.0
        assert data["description"] == "Expensive lunch"

    def test_update_expense_category(self, client, auth_headers):
        """Test updating expense category"""
        # Create expense
        create_response = client.post(
            "/api/expenses",
            json={
                "amount": 25.0,
                "category": "Food",
                "description": "Lunch",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Update category
        response = client.put(
            f"/api/expenses/{expense_id}",
            json={"category": "Transport"},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["category"] == "Transport"

    def test_update_expense_not_found(self, client, auth_headers):
        """Test updating non-existent expense"""
        response = client.put(
            "/api/expenses/99999",
            json={"amount": 35.0},
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteExpense:
    """Test deleting expenses"""

    def test_delete_expense_success(self, client, auth_headers):
        """Test successful expense deletion"""
        # Create expense
        create_response = client.post(
            "/api/expenses",
            json={
                "amount": 25.0,
                "category": "Food",
                "description": "Lunch",
                "date": datetime.utcnow().isoformat()
            },
            headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Delete expense
        response = client.delete(
            f"/api/expenses/{expense_id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify deletion
        get_response = client.get(
            f"/api/expenses/{expense_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_not_found(self, client, auth_headers):
        """Test deleting non-existent expense"""
        response = client.delete(
            "/api/expenses/99999",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_expense_without_auth(self, client):
        """Test deleting expense without authentication"""
        response = client.delete("/api/expenses/1")
        assert response.status_code == status.HTTP_403_FORBIDDEN
