# Contributing to EnerScopeAI

Thank you for your interest in contributing to EnerScopeAI! This document provides guidelines for contributing to the project.

## Getting Started

### Local Development Setup

#### Prerequisites
- Python 3.11+ 
- Node.js 18+
- Git

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/EnerScopeAI.git
cd EnerScopeAI
```

#### 2. Backend Setup
```bash
cd backend

# Create Python virtual environment
python -m venv venv

# Activate venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start dev server (runs on http://localhost:5173)
npm run dev
```

#### 4. Environment Configuration
```bash
# Copy the example file
cp .env.example .env

# Update .env with your values:
# - GEMINI_API_KEY from https://aistudio.google.com/app/apikey
# - JWT_SECRET_KEY (any random string for development)
```

#### 5. Start Backend Server
```bash
cd backend

# Activate venv if not already active
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux

# Run backend (port 8000)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Verify Setup
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Development Workflow

### Branch Naming
- `feature/` — New features
- `fix/` — Bug fixes
- `refactor/` — Code improvements
- `docs/` — Documentation updates
- `test/` — Tests

### Commit Messages
Follow conventional commits:
```
feat: add new feature description
fix: resolve specific bug
refactor: improve code structure
docs: update documentation
test: add/update tests
```

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 100 characters
- Run: `black backend/ --line-length 100`

#### JavaScript/React (Frontend)
- Use ESLint configuration in project
- Use Prettier for formatting
- Use meaningful variable/function names
- Comment complex logic

### Testing

#### Backend
```bash
cd backend
pytest tests/
```

#### Frontend
```bash
cd frontend
npm run test
```

---

## Submitting Changes

### Pull Request Process

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** with clear commit messages

3. **Test locally** to ensure nothing breaks
   ```bash
   # Backend: Verify API endpoints work
   # Frontend: Check UI renders correctly
   # Test: Run unit tests if applicable
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference to any related issues
   - Screenshots if UI changes

### Pull Request Guidelines
- One feature per PR (keep them focused)
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass
- Request review from maintainers

---

## Project Structure

```
EnerScopeAI/
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── models.py        # Pydantic models
│   ├── database.py      # Database layer
│   ├── requirements.txt  # Python dependencies
│   └── ...              # Service modules
├── frontend/            # React Vite frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── services/
│   │   ├── pages/
│   │   ├── components/
│   │   └── styles/
│   ├── package.json
│   └── vite.config.js
├── .env.example        # Environment template
└── README.md          # Project documentation
```

---

## Key Technologies

- **Backend**: FastAPI, Python 3.11+, SQLAlchemy, Psycopg
- **Frontend**: React 19, Vite, Tailwind CSS, Axios
- **Database**: PostgreSQL (optional for local dev)
- **API**: RESTful, OpenAPI/Swagger

---

## Issues & Bug Reports

### Reporting Bugs
Please create an issue with:
- Clear title
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Environment info (OS, Python version, Node version, etc.)
- Screenshots/logs if applicable

### Feature Requests
- Describe the feature
- Explain the use case
- Provide examples if possible
- Link to related issues

---

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn
- Report inappropriate behavior

---

## Questions?

- Check existing issues/discussions
- Ask in pull request comments
- Create a discussion topic

---

## License

Contributing means you agree your code is licensed under the project's license (MIT).

Thank you for contributing to EnerScopeAI! 🚀
