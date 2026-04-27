<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { User, Mail, Shield, Briefcase, Camera } from 'lucide-vue-next'

const authStore = useAuthStore()

const form = ref({
  full_name: '',
  resume_text: '',
  company_name: ''
})

const initForm = () => {
  if (authStore.user) {
    form.value.full_name = authStore.user.full_name || ''
    form.value.resume_text = authStore.user.resume_text || ''
    form.value.company_name = authStore.user.company_name || ''
  }
}

onMounted(initForm)
watch(() => authStore.user, initForm)

const saveProfile = async () => {
  await authStore.updateProfile(form.value)
  alert('Профиль успешно сохранен!')
}

const onFileChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    await authStore.uploadAvatar(target.files[0])
  }
}

const getAvatarUrl = (url: string) => `http://localhost:8000${url}`

// Функция для красивого отображения роли
const getRoleLabel = (role: string) => {
  if (role === 'admin') return 'Администратор'
  if (role === 'recruiter') return 'Рекрутер'
  return 'Соискатель'
}
</script>

<template>
  <div class="profile-page fade-in">
    <div class="container">
      <div class="unified-profile-card">
        
        <!-- Левая часть: Информация и Аватар -->
        <div class="profile-left">
          <div class="avatar-section">
            <div class="avatar-wrapper">
              <img v-if="authStore.user?.avatar" :src="getAvatarUrl(authStore.user.avatar)" class="avatar-img" />
              <div v-else class="avatar-placeholder">
                {{ (authStore.user?.full_name || authStore.user?.email || '?').charAt(0).toUpperCase() }}
              </div>
              <label class="avatar-upload-overlay" title="Сменить фото">
                <Camera :size="24" />
                <input type="file" accept="image/*" @change="onFileChange" hidden />
              </label>
            </div>
            
            <h2 class="user-name">{{ authStore.user?.full_name || 'Без имени' }}</h2>
            <div class="role-badge" :class="authStore.user?.role">
              <Shield v-if="authStore.user?.role === 'admin'" :size="14" />
              <Briefcase v-else-if="authStore.user?.role === 'recruiter'" :size="14" />
              <User v-else :size="14" />
              {{ getRoleLabel(authStore.user?.role) }}
            </div>
          </div>

          <div class="user-info-list">
            <div class="info-item">
              <Mail :size="18" class="info-icon" />
              <span>{{ authStore.user?.email }}</span>
            </div>
          </div>
        </div>

        <!-- Правая часть: Форма редактирования -->
        <div class="profile-right">
          <h1 class="form-title">Настройки профиля</h1>
          
          <form @submit.prevent="saveProfile" class="profile-form">
            <div class="input-group">
              <label>Полное имя (ФИО)</label>
              <input v-model="form.full_name" type="text" placeholder="Введите ваше имя" />
            </div>

            <!-- ПОЛЕ ДЛЯ РЕКРУТЕРА -->
            <div v-if="authStore.user?.role === 'recruiter'" class="input-group">
              <label>Название компании</label>
              <input v-model="form.company_name" type="text" placeholder="" />
            </div>

            <!-- ПОЛЕ ДЛЯ СОИСКАТЕЛЯ -->
            <div v-if="authStore.user?.role === 'seeker'" class="input-group">
              <label>Резюме / О себе</label>
              <textarea 
                v-model="form.resume_text" 
                rows="8" 
                placeholder="Расскажите о своих навыках..."
              ></textarea>
            </div>

            <div class="form-actions">
              <button type="submit" class="save-btn" :disabled="authStore.isLoading">
                <span v-if="authStore.isLoading" class="spinner"></span>
                <span v-else>Сохранить изменения</span>
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeIn 0.5s ease-out; }

.profile-page {
  padding-top: 40px; /* Отступ от хедера */
  padding-bottom: 60px;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Единая карточка */
.unified-profile-card {
  display: grid;
  grid-template-columns: 320px 1fr;
  background-color: var(--bg-card);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border-color);
}

/* Левая часть */
.profile-left {
  background-color: var(--bg-card);
  padding: 40px 30px;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-section {
  text-align: center;
  margin-bottom: 30px;
  width: 100%;
}

.avatar-wrapper {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 20px;
  border-radius: 50%;
  border: 4px solid var(--primary);
  box-shadow: 0 8px 16px rgba(139, 92, 246, 0.2);
  overflow: hidden;
}

.avatar-img, .avatar-placeholder {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary);
  color: white;
  font-size: 4.5rem;
  font-weight: 800;
}

.avatar-upload-overlay {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background-color: rgba(0,0,0,0.5);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  cursor: pointer;
  transition: opacity 0.3s;
}

.avatar-wrapper:hover .avatar-upload-overlay {
  opacity: 1;
}

.user-name {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 10px;
  color: var(--text-main);
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Стили для ролей */
.role-badge.admin { background-color: #ef4444; color: white; }
.role-badge.recruiter { background-color: var(--primary); color: white; }
.role-badge.seeker { background-color: var(--border-color); color: var(--text-muted); }

.user-info-list {
  width: 100%;
  border-top: 1px solid var(--border-color);
  padding-top: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 0.95rem;
  padding: 8px 0;
}

/* Правая часть */
.profile-right {
  padding: 50px;
}

.form-title {
  font-size: 1.8rem;
  font-weight: 800;
  margin-bottom: 30px;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.input-group input, .input-group textarea {
  padding: 14px 18px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-main);
  color: var(--text-main);
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.2s;
  outline: none;
}

.input-group input:focus, .input-group textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.1);
  background-color: var(--bg-card);
}

.form-actions {
  padding-top: 10px;
}

.save-btn {
  background-color: var(--primary);
  color: white;
  padding: 16px 32px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.save-btn:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.save-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 20px; height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Адаптивность */
@media (max-width: 900px) {
  .unified-profile-card { grid-template-columns: 1fr; }
  .profile-left { border-right: none; border-bottom: 1px solid var(--border-color); }
}
</style>