import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { startSession, getNextQuestion, submitAnswer } from '../services/api'

function Quiz() {
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showAbility, setShowAbility] = useState(false)

  // Start new session on mount
  useEffect(() => {
    const initializeSession = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await startSession()
        setSession(data)
        setCurrentQuestion(data.next_question)
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to start session')
      } finally {
        setLoading(false)
      }
    }
    initializeSession()
  }, [])

  const handleAnswerSelect = (index) => {
    setSelectedAnswer(index)
  }

  const handleSubmitAnswer = async () => {
    if (selectedAnswer === null || !session || !currentQuestion) return

    setLoading(true)
    setError(null)

    try {
      const data = await submitAnswer(
        session.session_id,
        currentQuestion.id,
        selectedAnswer
      )

      // Update session with new ability
      setSession(prev => ({
        ...prev,
        current_ability: data.current_ability
      }))

      if (data.next_question) {
        setCurrentQuestion(data.next_question)
        setSelectedAnswer(null)
      } else {
        // Session complete, navigate to results
        navigate('/result', { state: { sessionId: session.session_id } })
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit answer')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !session) {
    return (
      <div className="container">
        <div className="card">
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <div className="card">
          <h3 style={{ color: 'red' }}>Error</h3>
          <p>{error}</p>
          <button className="btn" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!session || !currentQuestion) {
    return null
  }

  const progress = ((session.questions_asked || 0) + 1) / 10 * 100

  return (
    <div className="container">
      <div className="card">
        <div style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span>Question {Math.min((session.questions_asked || 0) + 1, 10)}/10</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div style={{ height: '8px', backgroundColor: '#e0e0e0', borderRadius: '4px' }}>
            <div
              style={{
                width: `${progress}%`,
                height: '100%',
                backgroundColor: '#007bff',
                borderRadius: '4px',
                transition: 'width 0.3s'
              }}
            />
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
          <span style={{ backgroundColor: '#e3f2fd', padding: '4px 8px', borderRadius: '4px' }}>
            {currentQuestion.topic}
          </span>
          <span style={{ backgroundColor: '#fff3e0', padding: '4px 8px', borderRadius: '4px' }}>
            Difficulty: {currentQuestion.difficulty.toFixed(2)}
          </span>
        </div>

        <h2 style={{ marginBottom: '24px' }}>{currentQuestion.text}</h2>

        <div style={{ marginBottom: '24px' }}>
          {currentQuestion.options.map((option, index) => (
            <div
              key={index}
              style={{
                padding: '12px',
                marginBottom: '8px',
                border: selectedAnswer === index ? '2px solid #007bff' : '1px solid #ddd',
                borderRadius: '6px',
                cursor: 'pointer',
                backgroundColor: selectedAnswer === index ? '#e3f2fd' : 'white'
              }}
              onClick={() => handleAnswerSelect(index)}
            >
              <label style={{ cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="answer"
                  value={index}
                  checked={selectedAnswer === index}
                  onChange={() => handleAnswerSelect(index)}
                  style={{ marginRight: '8px' }}
                />
                {option}
              </label>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <button
            className="btn"
            onClick={handleSubmitAnswer}
            disabled={selectedAnswer === null || loading}
          >
            Submit Answer
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => setShowAbility(!showAbility)}
          >
            {showAbility ? 'Hide' : 'Show'} Ability
          </button>
        </div>

        {showAbility && (
          <div style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '6px' }}>
            <strong>Current Ability:</strong> {session.current_ability?.toFixed(3) || 'N/A'}
          </div>
        )}
      </div>
    </div>
  )
}

export default Quiz
