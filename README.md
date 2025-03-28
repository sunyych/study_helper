# Learning Platform

A comprehensive educational platform designed to help users of all ages learn Chinese, math, English, and other subjects. The platform leverages a local large language model (e.g., Llama) for conversational interactions and tutorials, and includes video-based learning, quizzes, progress tracking, and time management features.

## Features

- **User Authentication**: Simple password-based login system managed by an admin
- **Course Structure**: Courses categorized by subjects with multiple units and video lessons
- **Learning Interface**: Video player, note-taking with Markdown support, and auto-generated quizzes
- **Progress Tracking**: Track learning goals, progress, and time spent on learning activities
- **Admin Interface**: Manage course content, users, and trigger video processing
- **LLM Integration**: Context-aware interactions, personalized quizzes, and study recommendations

## Technology Stack

- **Frontend**: React with Bootstrap for responsive UI
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **Deployment**: Docker for containerized deployment
- **Video Integration**: YouTube, Khan Academy, and local video support
- **Local AI Model**: Llama for conversational and quiz generation

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sunyych/learning-platform.git
   cd learning-platform
   ```

2. Start the application using Docker Compose:

   ```bash
   docker compose down
   docker compose build --no-cache
   docker compose up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Default Admin Credentials

- Email: admin@example.com
- Password: admin123

### default test user

- email: test@example.com
- password: password123

## Project Structure

- `backend/`: FastAPI backend application
  - `app/`: Main application code
    - `api/`: API endpoints
    - `core/`: Core functionality (config, security, etc.)
    - `models/`: Database models
    - `schemas/`: Pydantic schemas for API validation
    - `services/`: Business logic services
- `frontend/`: React frontend application
  - `src/`: Source code
    - `components/`: Reusable UI components
    - `pages/`: Page components
    - `services/`: API service clients
- `uploads/`: Directory for uploaded videos
- `docker-compose.yml`: Docker Compose configuration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Local Backend Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip and virtualenv

### Setup Steps

1. **Create and activate virtual environment:**

   ```bash
   python -m venv .env
   source .env/bin/activate  # On Windows: .env\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**

   ```bash
   # Start PostgreSQL service
   # Linux: sudo service postgresql start
   # macOS: brew services start postgresql
   # Windows: Start in Services panel
   
   # Create database
   psql -U postgres -c "CREATE DATABASE study_helper;"
   ```

4. **Configure environment variables:**

   ```bash
   # Create .env file in backend directory
   cp .env.example .env
   
   # Edit .env file with your database connection:
   # DATABASE_URL=postgresql://postgres:password@localhost:5432/study_helper
   # SECRET_KEY=your_secret_key
   ```

5. **Run database migrations:**

   ```bash
   cd backend
   alembic upgrade head
   ```

6. **Start the backend server:**

   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API documentation:**
   - Open http://localhost:8000/docs in your browser

### Troubleshooting

1. **Model Import Errors:**
   - Check that all model names match in imports and definitions
   - Ensure circular imports are resolved

2. **Database Connection Issues:**
   - Verify PostgreSQL is running: `pg_isready`
   - Check credentials in DATABASE_URL

3. **Alembic Migration Issues:**
   - Run with verbose output: `alembic upgrade head --verbose`
   - If tables exist, try: `alembic stamp head` to mark current as up-to-date

4. **bcrypt/passlib Issues:**
   - Ensure bcrypt version is 3.2.2: `pip install bcrypt==3.2.2`

### Local Development Setup

1. Clone the repository and set up environment:

```bash
git clone https://github.com/yourusername/study_helper.git
cd study_helper
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate
```

2. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Start PostgreSQL in Docker:

```bash
# Start only the database container
docker-compose up -d db

# Wait a few seconds for the database to be ready
sleep 5
```

4. Configure environment variables:

```bash
# Create .env file in backend directory
cp .env.example .env

# Edit .env file with your database connection:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app
```

5. Run database migrations:

```bash
cd backend
alembic upgrade head
```

6. Start the backend server:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

7. In a new terminal, install and start the frontend:

```bash
cd frontend
npm install
npm start
```

### Common Issues

1. Database Connection:
   - Ensure PostgreSQL container is running: `docker ps`
   - Check database logs: `docker-compose logs db`
   - Verify database exists: `docker exec -it study_helper-db-1 psql -U postgres -l`

2. Port Conflicts:
   - Check if ports 8000 (backend) and 3000 (frontend) are available
   - To kill processes using these ports:

     ```bash
     # On Linux/macOS:
     lsof -i :8000 | grep LISTEN
     kill -9 <PID>
     ```

3. Dependencies:
   - If you encounter module not found errors:

     ```bash
     pip install -r requirements.txt --no-cache-dir
     ```

   - For frontend dependency issues:

     ```bash
     rm -rf node_modules package-lock.json
     npm install
     ```
