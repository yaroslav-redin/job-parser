<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const isLogin = ref(true)
const fullName = ref('') 

const submit = async () => {
  if (isLogin.value) {
    await authStore.login(email.value, password.value)
  } else {
    await authStore.register(email.value, password.value, fullName.value)
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card fade-in">
      
      <h2 class="title">{{ isLogin ? 'С возвращением!' : 'Создать аккаунт' }}</h2>
      <p class="subtitle">
        {{ isLogin ? 'Войдите, чтобы находить лучшие вакансии' : 'Присоединяйтесь к нашей платформе' }}
      </p>
      <div v-if="authStore.error" class="error-msg">
        {{ authStore.error }}
      </div>

      <form @submit.prevent="submit" class="auth-form">
        <div v-if="!isLogin" class="input-group">
          <label>ФИО</label>
          <input v-model="fullName" type="text" placeholder="Иванов Иван Иванович" required />
        </div>

        <div class="input-group">
          <label>Email</label>
          <input v-model="email" type="email" placeholder="you@example.com" required />
        </div>

        <div class="input-group">
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••••" required />
        </div>

        <button type="submit" class="submit-btn" :disabled="authStore.isLoading">
          <span v-if="authStore.isLoading" class="spinner"></span>
          <span v-else>{{ isLogin ? 'Войти' : 'Зарегистрироваться' }}</span>
        </button>
      </form>

      <div class="toggle-mode">
        <span>{{ isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}</span>
        <button type="button" @click="isLogin = !isLogin" class="toggle-btn">
          {{ isLogin ? 'Зарегистрируйтесь' : 'Войти' }}
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Анимация появления */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.error-msg {
  background-color: #fee2e2;
  color: #dc2626;
  padding: 10px;
  border-radius: 8px;
  text-align: center;
  font-size: 0.9rem;
  margin-bottom: 20px;
  border: 1px solid #f87171;
}

.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 104px); /* Высота экрана минус хедер и отступы */
}

.auth-card {
  background-color: var(--bg-card);
  padding: 40px;
  border-radius: 16px;
  box-shadow: var(--shadow);
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--border-color);
}

.title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: var(--text-muted);
  margin-bottom: 30px;
  font-size: 0.9rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 0.9rem;
  font-weight: 500;
}

.input-group input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-main);
  color: var(--text-main);
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

.input-group input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
}

.submit-btn {
  background-color: var(--primary);
  color: white;
  padding: 14px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  margin-top: 10px;
  transition: background-color 0.2s, transform 0.2s;
}

.submit-btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
}

.toggle-mode {
  margin-top: 24px;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-muted);
}

.toggle-btn {
  color: var(--primary);
  font-weight: 600;
  margin-left: 6px;
  transition: color 0.2s;
}

.toggle-btn:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.slide-down {
  animation: slideDown 0.3s ease-out;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); height: 0; }
  to { opacity: 1; transform: translateY(0); height: auto; }
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Крутилка загрузки */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>