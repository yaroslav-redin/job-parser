import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'
import router from '../router'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<any>(null)
  const error = ref('')
  const isLoading = ref(false)

  const login = async (email: string, password: string) => {
    error.value = ''; isLoading.value = true
    try {
      const params = new URLSearchParams()
      params.append('username', email)
      params.append('password', password)
      const response = await api.post('/auth/login', params)
      token.value = response.data.access_token
      localStorage.setItem('token', token.value)
      await fetchUser()
      router.push('/')
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка авторизации'
    } finally {
      isLoading.value = false
    }
  }

  const register = async (email: string, password: string, fullName: string) => {
    error.value = ''; isLoading.value = true
    try {
      await api.post('/auth/register', { 
      email: email, 
      password: password, 
      full_name: fullName, // Проверь это имя ключа!
      role: 'seeker' 
    })
      await login(email, password)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка регистрации'
    } finally {
      isLoading.value = false
    }
  }

  const fetchUser = async () => {
    if (!token.value) return
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
    } catch (err) { logout() }
  }

  const updateProfile = async (data: { full_name: string, resume_text: string, company_name: string }) => {
    isLoading.value = true
    try {
      const response = await api.put('/users/me', data)
      user.value = response.data
    } finally { isLoading.value = false }
  }

  const uploadAvatar = async (file: File) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const response = await api.post('/users/me/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      user.value = response.data
    } finally { isLoading.value = false }
  }

  const logout = () => {
    token.value = ''; user.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, user, error, isLoading, login, register, fetchUser, updateProfile, uploadAvatar, logout }
})