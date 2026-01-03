from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from collections import defaultdict

from app.database import get_db
from app.models import Expense
from app.schemas import AnalyticsSummary, CategorySummary, MonthlySummary, CategoryEnum
from app.security import get_current_user

router = APIRouter()

@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    user_id: int = Depends(get_current_user),
    months: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get analytics summary including spending by category and monthly trends"""
    now = datetime.utcnow()
    start_date = now - timedelta(days=30 * months)

    # Get all expenses for the period
    expenses = db.query(Expense).filter(
        and_(Expense.owner_id == user_id, Expense.date >= start_date)
    ).all()

    # Calculate total spending
    total_spending = sum(exp.amount for exp in expenses)

    # Calculate current month spending
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_expenses = [exp for exp in expenses if exp.date >= month_start]
    current_month_spending = sum(exp.amount for exp in current_month_expenses)

    # Breakdown by category
    category_spending = defaultdict(lambda: {"total": 0, "count": 0})
    for exp in expenses:
        category_spending[exp.category]["total"] += exp.amount
        category_spending[exp.category]["count"] += 1

    by_category = []
    for category in CategoryEnum:
        if category in category_spending:
            total = category_spending[category]["total"]
            percentage = (total / total_spending * 100) if total_spending > 0 else 0
            by_category.append(CategorySummary(
                category=category,
                total=round(total, 2),
                percentage=round(percentage, 2),
                count=category_spending[category]["count"]
            ))

    # Monthly trends
    monthly_trends = []
    for i in range(months):
        month_num = months - i
        month_start = now - timedelta(days=30 * month_num)
        month_end = month_start + timedelta(days=30)

        month_expenses = [
            exp for exp in expenses
            if month_start <= exp.date < month_end
        ]

        month_total = sum(exp.amount for exp in month_expenses)
        month_str = month_start.strftime("%Y-%m")

        # Category breakdown for this month
        month_category = defaultdict(lambda: {"total": 0, "count": 0})
        for exp in month_expenses:
            month_category[exp.category]["total"] += exp.amount
            month_category[exp.category]["count"] += 1

        month_by_category = []
        for category in CategoryEnum:
            if category in month_category:
                cat_total = month_category[category]["total"]
                cat_percentage = (cat_total / month_total * 100) if month_total > 0 else 0
                month_by_category.append(CategorySummary(
                    category=category,
                    total=round(cat_total, 2),
                    percentage=round(cat_percentage, 2),
                    count=month_category[category]["count"]
                ))

        monthly_trends.append(MonthlySummary(
            month=month_str,
            total=round(month_total, 2),
            by_category=month_by_category
        ))

    return AnalyticsSummary(
        total_spending=round(total_spending, 2),
        current_month_spending=round(current_month_spending, 2),
        by_category=by_category,
        monthly_trends=monthly_trends
    )

@router.get("/by-category")
async def get_by_category(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category"""
    expenses = db.query(Expense).filter(Expense.owner_id == user_id).all()

    category_spending = defaultdict(lambda: {"total": 0, "count": 0})
    for exp in expenses:
        category_spending[exp.category]["total"] += exp.amount
        category_spending[exp.category]["count"] += 1

    total_spending = sum(exp.amount for exp in expenses)

    result = []
    for category in CategoryEnum:
        if category in category_spending:
            total = category_spending[category]["total"]
            percentage = (total / total_spending * 100) if total_spending > 0 else 0
            result.append({
                "category": category.value,
                "total": round(total, 2),
                "percentage": round(percentage, 2),
                "count": category_spending[category]["count"]
            })

    return {"by_category": result, "total": round(total_spending, 2)}

@router.get("/by-month")
async def get_by_month(
    user_id: int = Depends(get_current_user),
    months: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get monthly spending trends"""
    now = datetime.utcnow()
    start_date = now - timedelta(days=30 * months)

    expenses = db.query(Expense).filter(
        and_(Expense.owner_id == user_id, Expense.date >= start_date)
    ).all()

    monthly_data = defaultdict(float)
    for exp in expenses:
        month_str = exp.date.strftime("%Y-%m")
        monthly_data[month_str] += exp.amount

    result = []
    for i in range(months):
        month_num = months - i
        month_start = now - timedelta(days=30 * month_num)
        month_str = month_start.strftime("%Y-%m")
        result.append({
            "month": month_str,
            "total": round(monthly_data.get(month_str, 0), 2)
        })

    return {"monthly_trends": result}
