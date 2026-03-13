# Implementation Tasks: Adaptive Diagnostic Engine

## Phase 1: Backend Foundation

- [x] 1.1 Create project structure and initialize backend
  - Create backend directory structure (app/, app/__init__.py, app/config.py, app/main.py)
  - Create requirements.txt with Flask, PyMongo, prometheus_client, python-dotenv, Flask-Limiter
  - Initialize Flask app factory pattern
  - Configure environment variables via .env.example

- [x] 1.2 Set up MongoDB connection
  - Create app/db.py with MongoDB connection logic
  - Implement connection pooling
  - Add health check endpoint
  - Create database initialization script

- [x] 1.3 Implement API key authentication
  - Create app/security/auth.py with API key validation
  - Store API keys as bcrypt hashes in MongoDB
  - Implement X-API-KEY header validation middleware
  - Add authentication decorator for routes

- [x] 1.4 Implement rate limiting
  - Create app/security/rate_limiter.py using Flask-Limiter
  - Configure rate limit per API key (100 requests/minute)
  - Add rate limit exceeded error handling
  - Test rate limiting behavior

## Phase 2: Data Layer

- [x] 2.1 Create Question model
  - Create app/models/question_model.py
  - Define Question data structure with validation
  - Implement validation rules (difficulty 0.1-1.0, valid options)
  - Add MongoDB document schema

- [x] 2.2 Create UserSession model
  - Create app/models/session_model.py
  - Define UserSession data structure
  - Implement validation rules (ability bounds, consistency checks)
  - Add MongoDB document schema

- [x] 2.3 Implement MongoDB repository
  - Create app/services/mongodb_repository.py
  - Implement CRUD operations for questions
  - Implement session management operations
  - Add question seeding functionality
  - Create database indexes

## Phase 3: Adaptive Engine

- [x] 3.1 Implement IRT-based ability update
  - Create app/services/irt_model.py
  - Implement logistic model: P(correct) = 1 / (1 + exp(-(ability - difficulty)))
  - Implement ability update: θ_new = θ_old + α * (score - P)
  - Add ability clamping to [0.0, 1.0]
  - Write unit tests for edge cases

- [x] 3.2 Implement adaptive question selection
  - Create app/services/adaptive_engine.py
  - Implement question selection based on difficulty range (±0.15)
  - Implement fallback to expanded range (±0.3)
  - Implement random selection from available pool
  - Track question history to avoid duplicates

- [x] 3.3 Implement answer submission logic
  - Create answer validation logic
  - Implement ability score update after each answer
  - Update session statistics (correct_count, incorrect_count, questions_asked)
  - Add session history tracking

## Phase 4: API Endpoints

- [x] 4.1 Implement /start-session endpoint
  - Create app/routes/session_routes.py
  - POST /start-session with API key validation
  - Create new UserSession with ability = 0.5
  - Return session_id and initial question

- [x] 4.2 Implement /next-question endpoint
  - GET /next-question with session_id validation
  - Use adaptive engine to select next question
  - Return question details with difficulty and topic

- [x] 4.3 Implement /submit-answer endpoint
  - POST /submit-answer with answer validation
  - Validate answer_index against question options
  - Update ability score and session state
  - Return correctness and next question

- [x] 4.4 Implement /result endpoint
  - GET /result with session_id validation
  - Return final ability score
  - Include study_plan if questions_asked >= 10
  - Set end_time on first result retrieval

- [x] 4.5 Implement /metrics endpoint
  - GET /metrics for Prometheus scraping
  - Expose request_duration_seconds histogram
  - Expose questions_answered_total counter
  - Expose openai_api_calls_total counter

## Phase 5: OpenAI Integration

- [x] 5.1 Implement OpenAI service
  - Create app/services/ai_service.py
  - Configure OpenAI API client
  - Implement study plan generation prompt
  - Parse and validate OpenAI response
  - Add error handling for API failures

- [x] 5.2 Implement study plan generation trigger
  - Detect when questions_asked reaches 10
  - Format performance data for OpenAI prompt
  - Call OpenAI API asynchronously
  - Store generated study plan in UserSession

## Phase 6: Monitoring

- [x] 6.1 Implement metrics collection
  - Create app/monitoring/metrics.py
  - Track request durations per endpoint
  - Track question response accuracy
  - Track OpenAI API call performance
  - Expose metrics in Prometheus format

- [x] 6.2 Add structured logging
  - Implement JSON structured logging
  - Log all API requests with request_id
  - Log session events (start, end, ability updates)
  - Log OpenAI API calls with duration

## Phase 7: Frontend

- [x] 7.1 Set up React project
  - Initialize Vite + React project
  - Configure React Router
  - Set up Axios for API calls
  - Create basic project structure

- [x] 7.2 Create Home page
  - Add introduction text
  - Add "Start Test" button
  - Link to API service module

- [x] 7.3 Create Quiz page
  - Display progress bar (Question X/10)
  - Show question text and options
  - Add topic badge and difficulty indicator
  - Implement answer selection with radio buttons
  - Add Submit button (disabled until answer selected)
  - Show estimated ability toggle

- [x] 7.4 Create Result page
  - Display final ability score (0.0-1.0)
  - Show accuracy percentage
  - Display breakdown by topic (bar chart)
  - Show generated study plan
  - Add "Retake" and "Share" buttons

- [x] 7.5 Create API service module
  - Create src/services/api.js
  - Implement all API endpoint calls
  - Handle authentication headers
  - Add error handling and loading states
  - Implement request retry logic

## Phase 8: Docker & Deployment

- [x] 8.1 Create Dockerfile for backend
  - Use Python 3.11 slim image
  - Install dependencies from requirements.txt
  - Expose port 5000
  - Configure gunicorn for production

- [x] 8.2 Create Dockerfile for frontend
  - Use Node 20 for build
  - Build static assets
  - Serve via nginx or Vite dev server

- [x] 8.3 Create docker-compose.yml
  - Define mongodb service (mongo:6)
  - Define backend service
  - Define frontend service
  - Define prometheus service
  - Define grafana service
  - Configure volumes and dependencies
  - Set environment variables

- [x] 8.4 Create prometheus.yml
  - Configure scrape for backend:5000
  - Set metrics_path to /metrics
  - Add job_name: adaptive-backend

- [x] 8.5 Create seed_questions.py
  - Create 20+ GRE-style questions
  - Include variety of topics (Algebra, Vocabulary, etc.)
  - Assign difficulty scores 0.1-1.0
  - Include tags for each question
  - Run script to seed database

## Phase 9: Testing

- [x] 9.1 Write unit tests for adaptive engine
  - Test ability update with various inputs
  - Test question selection logic
  - Test edge cases (all correct, all wrong)

- [x] 9.2 Write unit tests for IRT model
  - Test logistic probability calculation
  - Test ability bounds preservation
  - Test learning rate impact

- [x] 9.3 Write integration tests
  - Test complete session flow
  - Test API endpoints with authentication
  - Test database operations
  - Test OpenAI integration (mocked)

- [x] 9.4 Write property-based tests
  - Test ability score bounds
  - Test accuracy count consistency
  - Test no duplicate questions
  - Test difficulty adjustment direction

## Phase 10: Documentation

- [x] 10.1 Update README.md
  - Project overview
  - Tech stack
  - Installation instructions
  - Docker deployment guide
  - API documentation
  - Development setup

- [x] 10.2 Create .env.example
  - List all required environment variables
  - Provide example values
  - Document each variable's purpose

- [x] 10.3 Add code comments
  - Document all public functions
  - Add inline comments for complex logic
  - Document configuration options
