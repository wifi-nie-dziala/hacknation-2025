# Contributing to HackNation 2025

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

### Getting Started

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hacknation-2025.git
   cd hacknation-2025
   ```

2. Start the development environment:
   ```bash
   docker-compose up -d
   ```

## Project Structure

```
hacknation-2025/
├── frontend/        # React.js application
├── backend/         # Flask API
├── database/        # PostgreSQL with pgvector
└── docker-compose.yml
```

## Development Workflow

### Frontend Development

For faster iteration, you can run the frontend locally:

```bash
cd frontend
npm install
npm run dev
```

The dev server supports hot module replacement and runs on http://localhost:5173

### Backend Development

For local backend development:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Make sure the database is running:
```bash
docker-compose up database
```

### Database Changes

Database schema changes should be made in `database/init.sql`. To apply changes:

```bash
# Stop and remove the database container
docker-compose down database
docker volume rm hacknation-postgres-data

# Restart to recreate with new schema
docker-compose up database
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### JavaScript (Frontend)
- Use modern ES6+ syntax
- Follow React best practices
- Use functional components with hooks
- Keep components small and reusable

### General
- Write clear commit messages
- Keep commits atomic and focused
- Add comments for complex logic

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Test your changes:
   ```bash
   # Test the full stack
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Update documentation if needed
- Keep PRs focused on a single feature or fix

## Adding New Features

### Adding a New API Endpoint

1. Add the endpoint to `backend/app.py`
2. Update API documentation in `README.md`
3. Add corresponding frontend functionality if needed

Example:
```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    """Description of what this endpoint does."""
    data = request.json
    # Your logic here
    return jsonify({'result': 'success'}), 200
```

### Adding a New Frontend Component

1. Create component in `frontend/src/components/`
2. Import and use in `App.jsx`
3. Add necessary styles

Example:
```jsx
// src/components/MyComponent.jsx
export function MyComponent({ data }) {
  return (
    <div className="my-component">
      {/* Your component JSX */}
    </div>
  );
}
```

## Docker Best Practices

- Keep Dockerfiles minimal
- Use multi-stage builds for smaller images
- Don't commit sensitive data
- Use `.dockerignore` to exclude unnecessary files

## Reporting Issues

When reporting issues, please include:

- Description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Docker/system information
- Relevant logs

## Questions?

Feel free to:
- Open an issue for questions
- Check existing issues and PRs
- Reach out to maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn

Thank you for contributing! 🚀
