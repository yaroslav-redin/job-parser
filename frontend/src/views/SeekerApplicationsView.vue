<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Building, Clock } from 'lucide-vue-next'
import api from '../api'

const router = useRouter()
const applications = ref<any[]>([])
const isLoading = ref(true)

const fetchApplications = async () => {
  try {
    const res = await api.get('/seeker/applications')
    applications.value = res.data
  } catch (error) { console.error(error) } 
  finally { isLoading.value = false }
}

const getStatusInfo = (status: string) => {
  const map: Record<string, { label: string, class: string }> = {
    'pending': { label: 'На рассмотрении', class: 'status-pending' },
    'reviewed': { label: 'Просмотрено', class: 'status-reviewed' },
    'invited': { label: 'Приглашение', class: 'status-invited' },
    'rejected': { label: 'Отказ', class: 'status-rejected' },
  }
  return map[status] || map['pending']
}

onMounted(fetchApplications)
</script>

<template>
  <div class="page fade-in">
    <div class="container">
      <h1 class="title">Мои отклики</h1>
      
      <div class="card">
        <div v-if="isLoading" class="loader"><div class="spinner"></div></div>
        
        <div v-else-if="applications.length === 0" class="empty-state">
          <h3>Вы еще никуда не откликнулись</h3>
          <button @click="router.push('/')" class="btn-primary mt-4">Найти вакансии</button>
        </div>

        <table v-else class="custom-table">
          <thead>
            <tr>
              <th>Вакансия</th>
              <th>Дата отклика</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in applications" :key="app.id" class="clickable-row" @click="router.push(`/vacancies/${app.vacancy.id}`)">
              <td>
                <div class="vac-info">
                  <span class="vac-title">{{ app.vacancy.title }}</span>
                  <span class="vac-company"><Building :size="14"/> {{ app.vacancy.company || 'Компания не указана' }}</span>
                </div>
              </td>
              <td>
                <span class="date"><Clock :size="14"/> {{ new Date(app.created_at).toLocaleDateString() }}</span>
              </td>
              <td>
                <span class="status-badge" :class="getStatusInfo(app.status.split('.')[1] || app.status).class">
                  {{ getStatusInfo(app.status.split('.')[1] || app.status).label }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
.title { font-size: 2rem; font-weight: 800; margin-bottom: 24px; }

.card { background: var(--bg-card); border-radius: 20px; border: 1px solid var(--border-color); box-shadow: var(--shadow); overflow: hidden; }

.custom-table { width: 100%; border-collapse: collapse; }
.custom-table th { background: var(--bg-main); padding: 16px 24px; text-align: left; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; border-bottom: 1px solid var(--border-color); }
.custom-table td { padding: 16px 24px; border-bottom: 1px solid var(--border-color); }

.clickable-row { cursor: pointer; transition: 0.2s; }
.clickable-row:hover { background-color: var(--bg-main); }

.vac-info { display: flex; flex-direction: column; gap: 4px; }
.vac-title { font-weight: 700; font-size: 1.1rem; color: var(--primary); }
.vac-company { display: flex; align-items: center; gap: 6px; font-size: 0.9rem; color: var(--text-muted); }

.date { display: flex; align-items: center; gap: 6px; font-size: 0.9rem; color: var(--text-main); }

.status-badge { padding: 6px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 700; }
.status-pending { background: var(--bg-main); color: var(--text-muted); border: 1px solid var(--border-color); }
.status-reviewed { background: #eff6ff; color: #3b82f6; border: 1px solid #dbeafe; }
.status-invited { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }
.status-rejected { background: #fef2f2; color: #ef4444; border: 1px solid #fee2e2; }

.loader { padding: 50px; display: flex; justify-content: center; }
.spinner { width: 40px; height: 40px; border: 4px solid var(--border-color); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
.empty-state { text-align: center; padding: 60px; }
.mt-4 { margin-top: 16px; }
.btn-primary { background: var(--primary); color: white; padding: 10px 20px; border-radius: 10px; font-weight: 600; }

@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:translateY(0)} }
</style>