import axios from 'axios'

// Создаем экземпляр axios с базовым URL нашего FastAPI
const api = axios.create({
  baseURL: 'http://localhost:8000',
})

// Перехватчик: перед каждым запросом проверяем, есть ли токен, и добавляем его
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api