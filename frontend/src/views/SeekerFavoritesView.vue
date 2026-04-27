<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Building, Heart, Eye, Briefcase, ArrowLeft } from 'lucide-vue-next'
import api from '../api'

const router = useRouter()
const vacancies = ref<any[]>([])
const isLoading = ref(true)

// Загрузка избранных вакансий
const fetchFavorites = async () => {
  isLoading.value = true
  try {
    const res = await api.get('/seeker/favorites')
    vacancies.value = res.data
  } catch (error) {
    console.error("Ошибка при загрузке избранного:", error)
  } finally {
    isLoading.value = false
  }
}

// Удаление из избранного (тоггл лайка)
const toggleLike = async (job: any) => {
  try {
    await api.post(`/vacancies/${job.id}/like`)
    // Убираем вакансию из списка на экране без перезагрузки всей страницы
    vacancies.value = vacancies.value.filter(v => v.id !== job.id)
  } catch (e) {
    console.error(e)
  }
}

onMounted(fetchFavorites)

// Обрезка текста для карточки
const truncate = (text: string, length: number) => {
  if (!text) return ''
  return text.length <= length ? text : text.substring(0, length) + '...'
}
</script>

<template>
  <div class="favorites-page fade-in">
    <div class="container">
      
      <!-- Хедер страницы -->
      <div class="page-header">
        <button @click="router.push('/')" class="back-btn">
          <ArrowLeft :size="18" /> На главную
        </button>
        <h1 class="title">Избранные вакансии</h1>
        <p class="subtitle">Здесь хранятся вакансии, которые вы отметили сердечком</p>
      </div>

      <!-- Состояние загрузки -->
      <div v-if="isLoading" class="loader-container">
        <div class="spinner"></div>
      </div>

      <!-- Если избранного нет -->
      <div v-else-if="vacancies.length === 0" class="empty-state">
        <div class="empty-icon-circle">
          <Heart :size="48" />
        </div>
        <h3>Список пуст</h3>
        <p>Вы еще не добавили ни одной вакансии в избранное.</p>
        <button @click="router.push('/')" class="btn-primary-outline">Посмотреть все вакансии</button>
      </div>

      <!-- Сетка вакансий -->
      <div v-else class="vacancy-grid">
        <div v-for="job in vacancies" :key="job.id" class="vacancy-card">
          <div class="card-header">
            <h3 class="job-title">
              {{ job.title }}
              <span v-if="job.is_viewed" class="viewed-badge">
                <Eye :size="14" /> Просмотрено
              </span>
            </h3>
            
            <div class="header-actions">
              <span class="source-tag" :class="job.source">{{ job.source }}</span>
              <!-- Кнопка Лайка (всегда розовая на этой странице) -->
              <button @click="toggleLike(job)" class="like-btn liked">
                <Heart :size="22" fill="currentColor" />
              </button>
            </div>
          </div>
          
          <div class="company-info">
            <Building :size="16" />
            <p class="company-name">{{ job.company || 'Компания не указана' }}</p>
          </div>

          <p class="job-description">
            {{ truncate(job.description, 120) }}
          </p>
          
          <div class="card-footer">
            <button @click="router.push(`/vacancies/${job.id}`)" class="details-btn">
              Подробнее
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.favorites-page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

.page-header { margin-bottom: 40px; }
.back-btn { display: flex; align-items: center; gap: 8px; background: none; color: var(--text-muted); font-weight: 600; margin-bottom: 15px; transition: 0.2s; }
.back-btn:hover { color: var(--primary); }

.title { font-size: 2.2rem; font-weight: 800; color: var(--text-main); margin-bottom: 5px; }
.subtitle { color: var(--text-muted); font-size: 1.1rem; }

/* Сетка и карточки (аналогично HomeView) */
.vacancy-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 25px; }

.vacancy-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 28px;
  border-radius: 20px;
  box-shadow: var(--shadow);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}
.vacancy-card:hover { transform: translateY(-8px); border-color: var(--primary); }

.card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; }
.job-title { font-size: 1.25rem; font-weight: 800; color: var(--text-main); flex: 1; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }

.viewed-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.75rem; background: var(--bg-main); color: var(--text-muted); padding: 4px 8px; border-radius: 8px; font-weight: 600; border: 1px solid var(--border-color); }

.header-actions { display: flex; align-items: center; gap: 12px; }
.like-btn { color: var(--text-muted); transition: 0.2s; padding: 4px; background: none; }
.like-btn.liked { color: #ec4899; }
.like-btn:hover { transform: scale(1.1); }

.source-tag { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; padding: 4px 10px; border-radius: 8px; }
.source-tag.internal { background: #e0e7ff; color: #4338ca; }
.source-tag.hh { background: #fee2e2; color: #dc2626; }

.company-info { display: flex; align-items: center; gap: 8px; color: var(--text-muted); margin-bottom: 15px; }
.company-name { font-weight: 600; font-size: 0.95rem; }

.job-description { font-size: 0.95rem; line-height: 1.6; color: var(--text-muted); margin-bottom: 25px; flex-grow: 1; }

.card-footer { display: flex; justify-content: space-between; align-items: center; padding-top: 20px; border-top: 1px solid var(--border-color); }
.date { font-size: 0.8rem; color: var(--text-muted); font-style: italic; }

.details-btn {
  padding: 10px 20px; border-radius: 10px; background-color: var(--primary);
  color: white; font-weight: 700; font-size: 0.9rem; transition: 0.2s;
}

/* Пустое состояние */
.empty-state { text-align: center; padding: 80px 20px; color: var(--text-muted); }
.empty-icon-circle { 
    width: 100px; height: 100px; background: var(--bg-main); 
    border-radius: 50%; display: flex; align-items: center; 
    justify-content: center; margin: 0 auto 20px; color: var(--border-color);
}
.btn-primary-outline { 
    margin-top: 20px; background: none; border: 2px solid var(--primary); 
    color: var(--primary); padding: 12px 24px; border-radius: 12px; 
    font-weight: 700; transition: 0.2s; 
}
.btn-primary-outline:hover { background: var(--primary); color: white; }

/* Загрузка */
.loader-container { display: flex; justify-content: center; padding: 100px; }
.spinner { width: 45px; height: 45px; border: 4px solid var(--border-color); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:translateY(0)} }
.fade-in { animation: fadeIn 0.5s ease-out; }

@media (max-width: 768px) { .vacancy-grid { grid-template-columns: 1fr; } }
</style>