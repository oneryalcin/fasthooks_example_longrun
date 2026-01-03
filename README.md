# Expense Tracker

> **This application was autonomously built by Claude Code using [fasthooks](https://github.com/oneryalcin/fasthooks) `LongRunningStrategy`.**
>
> The LongRunningStrategy implements Anthropic's [two-agent pattern for long-running autonomous agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):
> - **Initializer Agent** (Session 1): Creates `feature_list.json` with 24 detailed features, sets up project structure
> - **Coding Agent** (Sessions 2+): Implements features one at a time, tests thoroughly, commits progress
>
> See `claude-progress.txt` for the full development history across multiple sessions.
>
> **Reproduce this yourself**: Check [`.claude-setup/`](.claude-setup/) for the hooks configuration and Docker setup used to build this app.
>
> Learn more: [fasthooks LongRunningStrategy docs](https://github.com/oneryalcin/fasthooks/blob/main/docs/strategies/long-running.md)

---

A full-stack expense tracking application built with FastAPI (backend) and React (frontend). Track your spending, visualize trends, set budgets, and manage recurring expenses.

## Features

- **User Authentication**: Secure JWT-based authentication with user registration and login
- **Expense Management**: Create, read, update, and delete expenses with categories and descriptions
- **Categories**: Organize expenses by predefined categories (Food, Transport, Entertainment, Utilities, Health, Shopping, Other)
- **Budget Alerts**: Set monthly budgets per category and receive alerts when exceeded
- **Recurring Expenses**: Set up expenses that repeat automatically (daily, weekly, monthly, yearly)
- **Charts & Analytics**: Visualize spending trends with pie charts (by category) and line/bar charts (over time)
- **CSV Export**: Export all expenses to CSV format for further analysis
- **Receipt Upload**: Attach receipt images to expenses for documentation
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Input Validation**: Comprehensive validation on both frontend and backend
- **Error Handling**: Detailed error messages and proper HTTP status codes

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens)
- **Validation**: Pydantic
- **Testing**: pytest
- **Image Storage**: Local filesystem or cloud storage

### Frontend
- **Framework**: React 18
- **State Management**: React Hooks / Context API
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Styling**: CSS Modules / Tailwind CSS
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development without Docker)
- Python 3.11+ (for local backend development)

### Quick Start (Docker)

```bash
git clone https://github.com/oneryalcin/fasthooks_example_longrun.git
cd fasthooks_example_longrun
docker compose up -d
```

Open in browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

Register a new account and start tracking!

### Manual Setup (Development)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on: http://localhost:8000

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:3000

## Project Structure

```
expense-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication logic
│   │   ├── routers/
│   │   │   ├── expenses.py       # Expense CRUD endpoints
│   │   │   ├── auth.py           # Authentication endpoints
│   │   │   ├── categories.py     # Category endpoints
│   │   │   ├── budgets.py        # Budget endpoints
│   │   │   ├── recurring.py      # Recurring expense endpoints
│   │   │   └── analytics.py      # Analytics/charts endpoints
│   │   └── dependencies.py       # Shared dependencies
│   ├── tests/
│   │   ├── test_auth.py          # Authentication tests
│   │   ├── test_expenses.py      # Expense CRUD tests
│   │   ├── test_validation.py    # Validation tests
│   │   └── test_integration.py   # Integration tests
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile               # Backend container
│   └── .env.example             # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API service layer
│   │   ├── hooks/               # Custom React hooks
│   │   ├── context/             # Context providers
│   │   ├── App.jsx              # Main app component
│   │   └── main.jsx             # Entry point
│   ├── public/                  # Static assets
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── Dockerfile               # Frontend container
│   └── .env.example             # Environment variables
├── docker-compose.yml           # Docker Compose configuration
├── init.sh                      # Setup script
├── feature_list.json            # Feature specifications and tests
└── README.md                    # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

### Expenses
- `GET /api/expenses` - Get all expenses (with filtering)
- `POST /api/expenses` - Create new expense
- `GET /api/expenses/{id}` - Get expense details
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense
- `GET /api/expenses/export/csv` - Export to CSV
- `POST /api/expenses/{id}/receipt` - Upload receipt image

### Categories
- `GET /api/categories` - Get available categories

### Budgets
- `GET /api/budgets` - Get all budgets
- `POST /api/budgets` - Create budget
- `PUT /api/budgets/{category}` - Update budget
- `DELETE /api/budgets/{category}` - Delete budget

### Recurring Expenses
- `GET /api/recurring-expenses` - Get all recurring expenses
- `POST /api/recurring-expenses` - Create recurring expense
- `PUT /api/recurring-expenses/{id}` - Update recurring expense
- `DELETE /api/recurring-expenses/{id}` - Delete recurring expense

### Analytics
- `GET /api/analytics/summary` - Get spending summary
- `GET /api/analytics/by-category` - Get breakdown by category
- `GET /api/analytics/by-month` - Get monthly trends

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage report
```

Target: >80% code coverage

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## Deployment

The application is containerized and ready for deployment:

```bash
# Using Docker Compose
docker-compose up -d

# Using Docker directly
docker build -t expense-tracker-backend ./backend
docker build -t expense-tracker-frontend ./frontend
docker run -p 8000:8000 expense-tracker-backend
docker run -p 3000:3000 expense-tracker-frontend
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./expense_tracker.db
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPLOAD_FOLDER=./uploads
ALLOWED_UPLOAD_EXTENSIONS=jpg,jpeg,png,gif
MAX_UPLOAD_SIZE=5242880
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api
```

## Development Workflow

1. Create a feature branch: `git checkout -b feature/feature-name`
2. Make your changes and test thoroughly
3. Commit with clear messages: `git commit -m "Add: description of changes"`
4. Push to repository: `git push origin feature/feature-name`
5. Create a pull request for review

## Troubleshooting

### Backend won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Ensure Python dependencies are installed: `pip install -r requirements.txt`
- Check database connection in `.env`

### Frontend won't start
- Ensure Node.js 18+ is installed: `node --version`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check if port 3000 is in use: `lsof -i :3000`

### Docker issues
- Rebuild images: `docker-compose build --no-cache`
- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`

## Contributing

1. Ensure tests pass before committing
2. Follow the existing code style and structure
3. Add tests for new features
4. Update documentation as needed
5. Keep commits focused and meaningful

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

Built with ❤️ for better expense tracking.
