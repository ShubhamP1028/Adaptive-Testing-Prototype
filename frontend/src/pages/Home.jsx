import { useNavigate } from 'react-router-dom'
import '../index.css'

function Home() {
  const navigate = useNavigate()

  const handleStartTest = () => {
    navigate('/quiz')
  }

  return (
    <div className="container">
      <div className="card">
        <h1>Adaptive Diagnostic Engine</h1>
        <p>
          A GRE-style adaptive testing system that delivers personalized assessments
          and study recommendations based on your performance.
        </p>
        <p>
          The system starts with baseline difficulty questions and dynamically adjusts
          difficulty based on your answers. After 10 questions, you'll receive a
          personalized 3-step study plan tailored to your specific weaknesses.
        </p>
        <div style={{ marginTop: '32px' }}>
          <button className="btn" onClick={handleStartTest}>
            Start Test
          </button>
        </div>
      </div>

      <div className="card">
        <h2>How It Works</h2>
        <ol>
          <li>Start with a baseline question (difficulty 0.5)</li>
          <li>Answer questions - correct answers lead to harder questions</li>
          <li>Incorrect answers lead to easier questions</li>
          <li>After 10 questions, get a personalized study plan</li>
        </ol>
      </div>

      <div className="card">
        <h2>Technical Details</h2>
        <ul>
          <li>IRT (Item Response Theory) based adaptive algorithm</li>
          <li>OpenAI-powered study plan generation</li>
          <li>Real-time ability score estimation</li>
          <li>Prometheus + Grafana monitoring</li>
        </ul>
      </div>
    </div>
  )
}

export default Home
