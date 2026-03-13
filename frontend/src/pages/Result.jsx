import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { getResult } from '../services/api'

function Result() {
  const location = useLocation()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchResult = async () => {
      const sessionId = location.state?.sessionId || new URLSearchParams(window.location.search).get('session_id')
      
      if (!sessionId) {
        setError('No session ID provided')
        setLoading(false)
        return
      }

      try {
        const data = await getResult(sessionId)
        setResult(data)
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to fetch results')
      } finally {
        setLoading(false)
      }
    }
    fetchResult()
  }, [location.state])

  const handleRetake = () => {
    navigate('/quiz')
  }

  const handleShare = () => {
    const shareData = {
      title: 'Adaptive Test Results',
      text: `I scored ${result?.accuracy * 100 || 0}% on the Adaptive Diagnostic Engine!`,
      url: window.location.href
    }
    
    if (navigator.share) {
      navigator.share(shareData).catch(console.error)
    } else {
      navigator.clipboard.writeText(`${shareData.text} ${window.location.href}`)
      alert('Results copied to clipboard!')
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <p>Loading results...</p>
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
          <button className="btn" onClick={() => navigate('/')}>
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  if (!result) {
    return null
  }

  const accuracy = result.accuracy * 100

  return (
    <div className="container">
      <div className="card">
        <h1>Test Results</h1>
        <p>Here's your performance summary and personalized study plan.</p>
      </div>

      <div className="card">
        <h2>Performance Summary</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
          <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#e3f2fd', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#007bff' }}>
              {result.current_ability?.toFixed(2) || 'N/A'}
            </div>
            <div style={{ color: '#666' }}>Ability Score</div>
          </div>
          <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#e8f5e9', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4caf50' }}>
              {accuracy.toFixed(0)}%
            </div>
            <div style={{ color: '#666' }}>Accuracy</div>
          </div>
          <div style={{ textAlign: 'center', padding: '16px', backgroundColor: '#fff3e0', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff9800' }}>
              {result.questions_asked || 0}
            </div>
            <div style={{ color: '#666' }}>Questions</div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          <div>
            <div style={{ color: '#4caf50' }}>
              <strong>Correct:</strong> {result.correct_count || 0}
            </div>
            <div style={{ color: '#f44336' }}>
              <strong>Incorrect:</strong> {result.incorrect_count || 0}
            </div>
          </div>
        </div>
      </div>

      {result.topic_stats && (
        <div className="card">
          <h2>Topic Breakdown</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(result.topic_stats).map(([topic, stats]) => (
              <div key={topic}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span>{topic}</span>
                  <span>{Math.round((stats.correct / stats.total) * 100)}% ({stats.correct}/{stats.total})</span>
                </div>
                <div style={{ height: '8px', backgroundColor: '#e0e0e0', borderRadius: '4px' }}>
                  <div
                    style={{
                      width: `${(stats.correct / stats.total) * 100}%`,
                      height: '100%',
                      backgroundColor: '#007bff',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.study_plan && (
        <div className="card">
          <h2>Personalized Study Plan</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {result.study_plan.steps?.map((step, index) => (
              <div key={index} style={{ padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '8px' }}>
                <h3 style={{ marginBottom: '8px' }}>{index + 1}. {step.title}</h3>
                <p style={{ marginBottom: '8px', color: '#666' }}>{step.description}</p>
                {step.action_items && (
                  <ul style={{ paddingLeft: '20px' }}>
                    {step.action_items.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card" style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
        <button className="btn" onClick={handleRetake}>
          Retake Test
        </button>
        <button className="btn btn-secondary" onClick={handleShare}>
          Share Results
        </button>
      </div>
    </div>
  )
}

export default Result
