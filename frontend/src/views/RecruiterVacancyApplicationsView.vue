<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, User, FileText, X } from 'lucide-vue-next'
import api from '../api'

const route = useRoute()
const router = useRouter()

const applications = ref<any[]>([])
const isLoading = ref(true)

// Модалка резюме
const showResumeModal = ref(false)
const selectedApplicant = ref<any>(null)

const fetchApplications = async () => {
  try {
    const res = await api.get(`/recruiter/vacancies/${route.params.id}/applications`)
    applications.value = res.data
  } catch (error) { router.push('/recruiter/vacancies') } 
  finally { isLoading.value = false }
}

const updateStatus = async (appId: number, event: Event) => {
  const target = event.target as HTMLSelectElement
  const newStatus = target.value
  try {
    await api.put(`/recruiter/applications/${appId}/status?status=${newStatus}`)
    // Статус обновлен в БД
  } catch (error) {
    alert('Ошибка при обновлении статуса')
  }
}

const openResume = (applicant: any) => {
  selectedApplicant.value = applicant
  showResumeModal.value = true
}

const getAvatarUrl = (path: string) => `http://localhost:8000${path}`

onMounted(fetchApplications)
</script>

<template>
  <div class="page fade-in">
    <div class="container">
      
      <button @click="router.back()" class="back-link">
        <ArrowLeft :size="18" /> Вернуться к вакансиям
      </button>

      <h1 class="title">Отклики кандидатов</h1>

      <div class="card">
        <div v-if="isLoading" class="loader"><div class="spinner"></div></div>
        
        <div v-else-if="applications.length === 0" class="empty-state">
          <h3>На эту вакансию пока нет откликов.</h3>
        </div>

        <table v-else class="custom-table">
          <thead>
            <tr>
              <th>Кандидат</th>
              <th>Дата отклика</th>
              <th>Резюме</th>
              <th>Статус (выбор)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applications" :key="app.id">
              <td>
                <div class="user-cell">
                  <div class="avatar-circle">
                    <img v-if="app.applicant.avatar" :src="getAvatarUrl(app.applicant.avatar)" />
                    <span v-else>{{ (app.applicant.full_name || app.applicant.email).charAt(0).toUpperCase() }}</span>
                  </div>
                  <div>
                    <p class="name">{{ app.applicant.full_name || 'Имя не указано' }}</p>
                    <p class="email">{{ app.applicant.email }}</p>
                  </div>
                </div>
              </td>
              <td>{{ new Date(app.created_at).toLocaleDateString() }}</td>
              <td>
                <button @click="openResume(app.applicant)" class="btn-resume">
                  <FileText :size="16" /> Читать
                </button>
              </td>
              <td>
                <!-- Селект для изменения статуса -->
                <select :value="app.status.split('.')[1] || app.status" @change="updateStatus(app.id, $event)" class="status-select">
                  <option value="pending">На рассмотрении</option>
                  <option value="reviewed">Просмотрено</option>
                  <option value="invited">Приглашение</option>
                  <option value="rejected">Отказ</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Модалка чтения резюме -->
    <div v-if="showResumeModal" class="modal-overlay" @click="showResumeModal = false">
      <div class="modal-window scale-in" @click.stop>
        <div class="modal-header">
          <h3>Резюме: {{ selectedApplicant.full_name || selectedApplicant.email }}</h3>
          <button @click="showResumeModal = false" class="close-btn"><X :size="20"/></button>
        </div>
        <div class="modal-body">
          <div class="resume-text">
            {{ selectedApplicant.resume_text || 'Кандидат не заполнил резюме в профиле.' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

.back-link { display: flex; align-items: center; gap: 8px; color: var(--text-muted); margin-bottom: 20px; font-weight: 600; background: none; border: none; cursor: pointer; }
.back-link:hover { color: var(--primary); }

.title { font-size: 2.2rem; font-weight: 800; margin-bottom: 24px; }
.card { background: var(--bg-card); border-radius: 20px; border: 1px solid var(--border-color); box-shadow: var(--shadow); overflow: hidden; }

.custom-table { width: 100%; border-collapse: collapse; }
.custom-table th { background: var(--bg-main); padding: 16px 24px; text-align: left; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; border-bottom: 1px solid var(--border-color); }
.custom-table td { padding: 16px 24px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }

.user-cell { display: flex; align-items: center; gap: 12px; }
.avatar-circle { width: 40px; height: 40px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; overflow: hidden; }
.avatar-circle img { width: 100%; height: 100%; object-fit: cover; }
.name { font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.email { font-size: 0.85rem; color: var(--text-muted); }

.btn-resume { display: flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 10px; background: var(--bg-main); color: var(--primary); border: 1px solid var(--primary); font-weight: 600; transition: 0.2s; cursor: pointer;}
.btn-resume:hover { background: var(--primary); color: white; }

.status-select { padding: 8px 12px; border-radius: 8px; border: 1px solid var(--border-color); background: var(--bg-main); color: var(--text-main); font-weight: 600; outline: none; cursor: pointer; }
.status-select:focus { border-color: var(--primary); }

.loader { padding: 50px; display: flex; justify-content: center; }
.spinner { width: 40px; height: 40px; border: 4px solid var(--border-color); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
.empty-state { text-align: center; padding: 60px; }

/* Модалка */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 2000; backdrop-filter: blur(4px); }
.modal-window { background: var(--bg-card); width: 90%; max-width: 600px; border-radius: 20px; border: 1px solid var(--border-color); overflow: hidden; }
.modal-header { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); }
.modal-header h3 { font-weight: 700; }
.close-btn { background: none; border: none; cursor: pointer; color: var(--text-muted); }
.modal-body { padding: 24px; max-height: 60vh; overflow-y: auto; }
.resume-text { line-height: 1.6; white-space: pre-wrap; font-size: 1.05rem; }

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
.scale-in { animation: scaleIn 0.3s ease-out; }
@keyframes fadeIn { from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:translateY(0)} }
@keyframes scaleIn { from{transform:scale(0.95);opacity:0} to{transform:scale(1);opacity:1} }
</style>