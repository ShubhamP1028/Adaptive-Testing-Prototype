# Adaptive Diagnostic Engine

A GRE-style adaptive testing system that delivers personalized assessments and study recommendations. The system dynamically adjusts question difficulty based on user performance using IRT-inspired algorithms, and generates personalized study plans using OpenAI after 10 questions.

## Features

- **Adaptive Testing**: Questions adjust difficulty based on your answers using Item Response Theory (IRT)
- **Ability Estimation**: Real-time tracking of your skill level (0.0 to 1.0 scale)
- **Personalized Study Plans**: AI-generated 3-step study recommendations after 10 questions
- **Comprehensive Analytics**: Topic breakdown and accuracy tracking
- **Production-Ready**: Dockerized, monitored with Prometheus/Grafana, rate-limited, and secured

## Tech Stack

- **Backend**: Flask (Python 3.11)
- **Database**: MongoDB (Docker-based)
- **Frontend**: React + Vite
- **AI**: OpenAI API (gpt-4)
- **Monitoring**: Prometheus + Grafana
- **Containerization**: Docker + Docker Compose

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Frontend  │────▶│   Backend    │────▶│   MongoDB    │
│  (React)    │     │   (Flask)    │     │   (Docker)   │
└─────────────┘     └──────────────┘     └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   OpenAI     │
                  │   (API)      │
                  └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │  Prometheus  │
                  │   (Metrics)  │
                  └──────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository

2. Create `.env` file in the root directory:
```bash
cp .env.example .env
```

3. Update `.env` with your OpenAI API key:
```bash
OPENAI_API_KEY=your-openai-api-key-here
API_KEY=your-api-key-here
```

4. Start all services:
```bash
docker-compose up -d
```

5. Seed questions into the database:
```bash
docker-compose exec backend python seed_questions.py
```

6. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

## API Endpoints

### POST /api/start-session
Start a new assessment session.

```json
Request:
{
  "user_id": "optional-user-id"
}

Response:
{
  "session_id": "uuid",
  "next_question": {
    "id": "uuid",
    "text": "Question text",
    "options": ["A", "B", "C", "D"],
    "difficulty": 0.5,
    "topic": "Algebra",
    "tags": ["quadratic"]
  }
}
```

### GET /api/next-question
Get the next question for a session.

Query params: `session_id`

### POST /api/submit-answer
Submit an answer to a question.

```json
Request:
{
  "session_id": "uuid",
  "question_id": "uuid",
  "answer_index": 0
}
```

### GET /api/result
Get session results and study plan.

Query params: `session_id`

### GET /api/metrics
Get Prometheus metrics (requires API key).

## Development

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m flask run
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

```bash
cd backend
pytest tests/
```

## Project Structure

```
adaptive-test-engine/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── routes/
│   │   │   ├── session_routes.py
│   │   │   ├── question_routes.py
│   │   │   └── meta_routes.py
│   │   ├── services/
│   │   │   ├── adaptive_engine.py
│   │   │   ├── irt_model.py
│   │   │   └── ai_service.py
│   │   ├── models/
│   │   │   ├── question_model.py
│   │   │   └── session_model.py
│   │   ├── security/
│   │   │   ├── auth.py
│   │   │   └── rate_limiter.py
│   │   └── monitoring/
│   │       └── metrics.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Quiz.jsx
│   │   │   └── Result.jsx
│   │   └── services/
│   │       └── api.js
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── prometheus/
│   └── prometheus.yml
├── seed_questions.py
├── .env.example
└── README.md
```

## License

MIT
