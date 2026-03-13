import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Set API key interceptor
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('apiKey') || 'default-api-key-for-demo'
  config.headers['X-API-KEY'] = apiKey
  return config
})

export const startSession = async (userId) => {
  const response = await api.post('/start-session', { user_id: userId })
  return response.data
}

export const getNextQuestion = async (sessionId) => {
  const response = await api.get('/next-question', { params: { session_id: sessionId } })
  return response.data
}

export const submitAnswer = async (sessionId, questionId, answerIndex) => {
  const response = await api.post('/submit-answer', {
    session_id: sessionId,
    question_id: questionId,
    answer_index: answerIndex
  })
  return response.data
}

export const getResult = async (sessionId) => {
  const response = await api.get('/result', { params: { session_id: sessionId } })
  return response.data
}

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api
