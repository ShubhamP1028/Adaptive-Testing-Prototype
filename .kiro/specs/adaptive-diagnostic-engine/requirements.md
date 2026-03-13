# Requirements Document: Adaptive Diagnostic Engine

## Introduction

The Adaptive Diagnostic Engine is a GRE-style adaptive testing system that delivers personalized assessments and study recommendations. The system dynamically adjusts question difficulty based on user performance using IRT-inspired algorithms, and generates personalized study plans using OpenAI after 10 questions. This document specifies the functional requirements derived from the approved design.

## Glossary

- **System**: The Adaptive Diagnostic Engine application (Flask backend + React frontend)
- **Backend**: Flask REST API server handling requests and business logic
- **Frontend**: React single-page application providing user interface
- **Adaptive_Engine**: Component responsible for question selection and ability estimation
- **OpenAI_Service**: Component that generates personalized study plans via OpenAI API
- **MongoDB_Repository**: Data layer managing questions and user sessions in Docker-based MongoDB
- **Metrics_Collector**: Component tracking application metrics for Prometheus
- **UserSession**: Data structure tracking user progress through assessment
- **Question**: Data structure representing a test question with difficulty and metadata
- **API_Key**: Authentication credential for accessing the system
- **Study_Plan**: Personalized 3-step learning recommendation generated after 10 questions
- **Ability_Score**: Numerical estimate (0.0 to 1.0) of user's current skill level

## Requirements

### Requirement 1: Session Management

**User Story:** As a user, I want to start a new assessment session, so that I can begin taking the adaptive test.

#### Acceptance Criteria

1. WHEN a POST request is sent to /start-session with a valid X-API-KEY header, THE Backend SHALL create a new UserSession with ability score initialized to 0.5
2. WHEN a new UserSession is created, THE Backend SHALL assign a unique session_id and return it in the response
3. WHEN a new UserSession is created, THE Backend SHALL initialize question_history as an empty list
4. WHEN a new UserSession is created, THE Backend SHALL set correct_count and incorrect_count to 0
5. WHEN a new UserSession is created, THE Backend SHALL record the start_time as the current timestamp

### Requirement 2: Authentication and Authorization

**User Story:** As a system administrator, I want to control access to the API, so that only authorized clients can use the system.

#### Acceptance Criteria

1. WHEN a request is received without an X-API-KEY header, THE Backend SHALL return HTTP 401 with error message "Invalid API key"
2. WHEN a request is received with an invalid X-API-KEY, THE Backend SHALL return HTTP 401 with error message "Invalid API key"
3. WHEN a request is received with a valid X-API-KEY, THE Backend SHALL process the request normally
4. THE Backend SHALL store API keys as bcrypt hashes in the database
5. WHEN an API key is marked as inactive, THE Backend SHALL reject requests using that key

### Requirement 3: Rate Limiting

**User Story:** As a system administrator, I want to limit request rates per API key, so that the system is protected from abuse and DoS attacks.

#### Acceptance Criteria

1. WHEN an API key exceeds the configured request limit per minute, THE Backend SHALL return HTTP 429 with error message "Rate limit exceeded"
2. WHEN an API key is within the rate limit, THE Backend SHALL process requests normally
3. THE Backend SHALL apply rate limiting using a sliding window algorithm
4. THE Backend SHALL track rate limits independently for each API key

### Requirement 4: Question Selection

**User Story:** As a user, I want to receive questions appropriate to my skill level, so that the assessment accurately measures my ability.

#### Acceptance Criteria

1. WHEN a GET request is sent to /next-question with a valid session_id, THE Adaptive_Engine SHALL calculate target difficulty based on current ability score
2. WHEN selecting a question, THE Adaptive_Engine SHALL query questions with difficulty within ±0.15 of target difficulty
3. WHEN fewer than 3 questions are available in the initial range, THE Adaptive_Engine SHALL expand the difficulty range to ±0.3
4. WHEN selecting a question, THE Adaptive_Engine SHALL exclude all questions already asked in the current session
5. WHEN multiple suitable questions are available, THE Adaptive_Engine SHALL select one randomly from the pool
6. WHEN no questions match the difficulty criteria, THE Adaptive_Engine SHALL select any unasked question as fallback
7. WHEN all questions have been asked, THE Backend SHALL return HTTP 404 with error message "No more questions available"

### Requirement 5: Answer Submission and Ability Update

**User Story:** As a user, I want my answers to be evaluated and my ability score updated, so that subsequent questions match my skill level.

#### Acceptance Criteria

1. WHEN a POST request is sent to /submit-answer with session_id, question_id, and answer_index, THE Backend SHALL validate that the question_id exists in the session's question_history
2. WHEN an answer is submitted, THE Backend SHALL compare answer_index to the question's correct_answer to determine correctness
3. WHEN an answer is submitted, THE Adaptive_Engine SHALL update the ability score using the logistic model formula: adjustment = learning_rate * (1.0 - probability) for correct answers
4. WHEN an answer is submitted, THE Adaptive_Engine SHALL update the ability score using the logistic model formula: adjustment = -learning_rate * probability for incorrect answers
5. WHEN the ability score is updated, THE Adaptive_Engine SHALL clamp the result to the range [0.0, 1.0]
6. WHEN a correct answer is submitted, THE Backend SHALL increment correct_count
7. WHEN an incorrect answer is submitted, THE Backend SHALL increment incorrect_count
8. WHEN an answer is submitted, THE Backend SHALL increment questions_asked
9. WHEN an invalid answer_index is provided, THE Backend SHALL return HTTP 400 with error message "Invalid answer index"

### Requirement 6: Study Plan Generation

**User Story:** As a user, I want to receive a personalized study plan after completing 10 questions, so that I know how to improve my skills.

#### Acceptance Criteria

1. WHEN a UserSession reaches 10 questions_asked, THE OpenAI_Service SHALL generate a study plan using the OpenAI API
2. WHEN generating a study plan, THE OpenAI_Service SHALL format performance data including topics missed, max difficulty reached, and accuracy percentage
3. WHEN generating a study plan, THE OpenAI_Service SHALL use model "gpt-4" with temperature 0.7 and max_tokens 1000
4. WHEN the OpenAI API returns a response, THE OpenAI_Service SHALL parse it into a StudyPlan structure with 3 steps
5. WHEN the OpenAI API call fails, THE Backend SHALL return HTTP 503 with error message "Study plan generation failed"
6. WHEN a study plan is generated, THE Backend SHALL store it in the UserSession document

### Requirement 7: Result Retrieval

**User Story:** As a user, I want to view my final results and study plan, so that I can understand my performance and next steps.

#### Acceptance Criteria

1. WHEN a GET request is sent to /result with a valid session_id, THE Backend SHALL return the UserSession's current_ability score
2. WHEN a GET request is sent to /result and questions_asked >= 10, THE Backend SHALL include the study_plan in the response
3. WHEN a GET request is sent to /result and questions_asked < 10, THE Backend SHALL return null for study_plan
4. WHEN a GET request is sent to /result with an invalid session_id, THE Backend SHALL return HTTP 404 with error message "Session not found"
5. WHEN a result is retrieved for the first time, THE Backend SHALL set the end_time to the current timestamp

### Requirement 8: Data Persistence

**User Story:** As a system, I need to persist questions and user sessions, so that data survives application restarts.

#### Acceptance Criteria

1. THE MongoDB_Repository SHALL store questions in a Questions collection with fields: id, text, options, correct_answer, difficulty, topic, tags, created_at
2. THE MongoDB_Repository SHALL store user sessions in a UserSessions collection with fields: session_id, user_id, start_time, current_ability, question_history, correct_count, incorrect_count, questions_asked, study_plan, end_time
3. WHEN a question is stored, THE MongoDB_Repository SHALL validate that difficulty is between 0.1 and 1.0
4. WHEN a question is stored, THE MongoDB_Repository SHALL validate that correct_answer is a valid index for the options array
5. WHEN a UserSession is stored, THE MongoDB_Repository SHALL validate that current_ability is between 0.0 and 1.0
6. THE MongoDB_Repository SHALL run in a Docker container using the mongo:6 image
7. THE MongoDB_Repository SHALL persist data to a Docker volume named mongo-data
8. THE MongoDB_Repository SHALL be accessible via connection URI mongodb://mongo:27017/adaptive_test

### Requirement 9: Question Database Seeding

**User Story:** As a system administrator, I want to populate the question database, so that the system has questions available for assessments.

#### Acceptance Criteria

1. THE MongoDB_Repository SHALL provide a seed_questions method that accepts a list of Question objects
2. WHEN seed_questions is called, THE MongoDB_Repository SHALL insert all questions into the Questions collection
3. WHEN seed_questions is called, THE MongoDB_Repository SHALL return the count of questions inserted
4. WHEN seed_questions is called with duplicate question IDs, THE MongoDB_Repository SHALL skip duplicates and continue

### Requirement 10: Metrics Collection

**User Story:** As a system administrator, I want to monitor application performance and usage, so that I can identify issues and optimize the system.

#### Acceptance Criteria

1. WHEN a request is processed, THE Metrics_Collector SHALL record the request duration in seconds tagged by endpoint
2. WHEN a question is answered, THE Metrics_Collector SHALL record whether the answer was correct and the question difficulty
3. WHEN the OpenAI API is called, THE Metrics_Collector SHALL record the call duration and success status
4. WHEN a GET request is sent to /metrics, THE Backend SHALL return metrics in Prometheus format
5. THE Metrics_Collector SHALL expose metrics: request_duration_seconds, questions_answered_total, questions_correct_total, openai_api_calls_total, openai_api_duration_seconds

### Requirement 11: Data Validation

**User Story:** As a system, I need to validate all data inputs, so that data integrity is maintained.

#### Acceptance Criteria

1. WHEN a Question is created, THE System SHALL validate that difficulty is between 0.1 and 1.0
2. WHEN a Question is created, THE System SHALL validate that correct_answer is a valid index for the options array
3. WHEN a Question is created, THE System SHALL validate that topic and text are non-empty strings
4. WHEN a Question is created, THE System SHALL validate that options contains at least 2 items
5. WHEN a UserSession is updated, THE System SHALL validate that current_ability is between 0.0 and 1.0
6. WHEN a UserSession is updated, THE System SHALL validate that correct_count + incorrect_count equals questions_asked
7. WHEN a UserSession is updated, THE System SHALL validate that questions_asked equals the length of question_history

### Requirement 12: Session State Consistency

**User Story:** As a system, I need to maintain consistent session state, so that assessments are accurate and reliable.

#### Acceptance Criteria

1. THE System SHALL ensure that for all UserSessions, correct_count + incorrect_count equals questions_asked
2. THE System SHALL ensure that for all UserSessions, current_ability remains between 0.0 and 1.0 after every update
3. THE System SHALL ensure that for all UserSessions, question_history contains no duplicate question_ids
4. THE System SHALL ensure that for all UserSessions, questions_asked equals the length of question_history
5. WHEN questions_asked is less than 10, THE System SHALL ensure study_plan is null
6. WHEN questions_asked is 10 or greater, THE System SHALL ensure study_plan is non-null

### Requirement 13: Error Handling

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can understand and resolve issues.

#### Acceptance Criteria

1. WHEN an invalid API key is provided, THE Backend SHALL return HTTP 401 with JSON body containing error message
2. WHEN rate limit is exceeded, THE Backend SHALL return HTTP 429 with JSON body containing error message
3. WHEN a session is not found, THE Backend SHALL return HTTP 404 with JSON body containing error message
4. WHEN no questions are available, THE Backend SHALL return HTTP 404 with JSON body containing error message
5. WHEN the OpenAI API fails, THE Backend SHALL return HTTP 503 with JSON body containing error message
6. WHEN an invalid answer index is provided, THE Backend SHALL return HTTP 400 with JSON body containing error message
7. WHEN any error occurs, THE Backend SHALL log the error with timestamp and context

### Requirement 14: Performance Requirements

**User Story:** As a user, I want fast response times, so that the assessment experience is smooth and responsive.

#### Acceptance Criteria

1. THE Backend SHALL respond to /start-session requests in less than 100ms (excluding network latency)
2. THE Backend SHALL respond to /next-question requests in less than 50ms (excluding network latency)
3. THE Backend SHALL respond to /submit-answer requests in less than 100ms (excluding network latency and OpenAI calls)
4. THE Backend SHALL respond to /result requests in less than 200ms (excluding network latency and OpenAI calls)
5. THE Backend SHALL respond to /metrics requests in less than 50ms (excluding network latency)

### Requirement 15: Database Indexing

**User Story:** As a system, I need efficient database queries, so that response times remain fast as data grows.

#### Acceptance Criteria

1. THE MongoDB_Repository SHALL create an index on the session_id field in the UserSessions collection
2. THE MongoDB_Repository SHALL create an index on the difficulty field in the Questions collection
3. THE MongoDB_Repository SHALL create an index on the question_id field in the Questions collection
4. THE MongoDB_Repository SHALL use connection pooling for concurrent session access

### Requirement 16: Docker Deployment

**User Story:** As a system administrator, I want to deploy the system using Docker, so that deployment is consistent and reproducible.

#### Acceptance Criteria

1. THE System SHALL provide a docker-compose.yml file that defines all services
2. THE System SHALL run MongoDB in a Docker container using the mongo:6 image
3. THE System SHALL run Prometheus in a Docker container using the prom/prometheus image
4. THE System SHALL run Grafana in a Docker container using the grafana/grafana image
5. THE System SHALL configure MongoDB with port mapping 27017:27017
6. THE System SHALL configure MongoDB with volume mount mongo-data:/data/db
7. THE System SHALL configure MongoDB with restart policy unless-stopped
8. WHEN docker-compose up is executed, THE System SHALL start all services in the correct dependency order

### Requirement 17: Configuration Management

**User Story:** As a system administrator, I want to configure the system via environment variables, so that I can deploy to different environments without code changes.

#### Acceptance Criteria

1. THE Backend SHALL read MONGODB_URI from environment variables
2. THE Backend SHALL read OPENAI_API_KEY from environment variables
3. THE Backend SHALL read API_KEYS from environment variables
4. THE System SHALL provide a .env.example file with all required configuration variables
5. WHEN a required environment variable is missing, THE Backend SHALL log an error and fail to start
