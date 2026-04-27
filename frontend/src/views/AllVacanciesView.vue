<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search, Building, Heart, Eye, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref((route.query.search as string) || '')
const sortOrder = ref('desc') // desc - новые, asc - старые
const vacancies = ref<any[]>([])
const total = ref(0)
const isLoading = ref(true)

// Пагинация
const currentPage = ref(1)
const itemsPerPage = 10
const totalPages = computed(() => Math.ceil(total.value / itemsPerPage))

const formatDate = (dateString: string) => {
  if (!dateString) return 'Неизвестно'
  const d = new Date(dateString)
  return isNaN(d.getTime()) ? 'Неизвестно' : d.toLocaleDateString('ru-RU')
}

const fetchVacancies = async () => {
  isLoading.value = true
  try {
    const skip = (currentPage.value - 1) * itemsPerPage
    const res = await api.get('/vacancies', {
      params: { search: searchQuery.value, skip, limit: itemsPerPage }
    })
    
    // Сортировка (пока фронтенд-сортировка, позже можно вынести на бэк)
    let sorted = res.data.vacancies
    if (sortOrder.value === 'asc') {
      sorted = sorted.reverse()
    }
    
    vacancies.value = sorted
    total.value = res.data.total
  } catch (error) { console.error(error) } 
  finally { isLoading.value = false }
}

const handleSearch = () => {
  currentPage.value = 1
  // Обновляем URL, чтобы поиск сохранялся в истории
  router.replace({ query: { ...route.query, search: searchQuery.value } })
  fetchVacancies()
}

// Следим за изменением сортировки
watch(sortOrder, fetchVacancies)

const toggleLike = async (job: any) => {
  if (!authStore.user || authStore.user.role !== 'seeker') return alert('Только соискатели могут добавлять в избранное.')
  try {
    const res = await api.post(`/vacancies/${job.id}/like`)
    job.is_liked = (res.data.status === 'liked')
  } catch (e) { console.error(e) }
}

const setPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
  fetchVacancies()
}

onMounted(fetchVacancies)

const getSourceLabel = (s: string) => ({'internal': 'На сайте', 'hh': 'HH.ru', 'avito': 'Авито', 'rabota': 'Работа.ру'})[s] || s
const truncate = (t: string, len: number) => t?.length <= len ? t : t?.substring(0, len) + '...'
</script>

<template>
  <div class="page fade-in">
    <div class="container">
      
      <!-- Панель управления (Поиск и Сортировка) -->
      <div class="controls-panel card">
        <div class="search-input-wrapper">
          <Search :size="20" class="search-icon" />
          <input v-model="searchQuery" type="text" placeholder="Поиск вакансий..." @keyup.enter="handleSearch" />
          <button @click="handleSearch" class="btn-search">Найти</button>
        </div>
        <div class="sort-wrapper">
          <label>Сортировать:</label>
          <select v-model="sortOrder" class="sort-select">
            <option value="desc">Сначала новые</option>
            <option value="asc">Сначала старые</option>
          </select>
        </div>
      </div>

      <div class="results-info">Найдено вакансий: <b>{{ total }}</b></div>

      <div v-if="isLoading" class="loader-container"><div class="spinner"></div></div>
      <div v-else-if="vacancies.length === 0" class="empty-state">По вашему запросу ничего не найдено.</div>

      <!-- ВЕРТИКАЛЬНЫЙ СПИСОК -->
      <div v-else class="vacancy-list">
        <div v-for="job in vacancies" :key="job.id" class="vacancy-card wide-card">
          
          <div class="card-main-content">
            <div class="card-header">
              <h3 class="job-title" @click="router.push(`/vacancies/${job.id}`)">
                {{ job.title }}
                <span v-if="job.is_viewed" class="viewed-badge"><Eye :size="14"/> Просмотрено</span>
              </h3>
              <span class="source-tag" :class="job.source">{{ getSourceLabel(job.source) }}</span>
            </div>
            
            <div class="company-info">
              <Building :size="16" /> <span class="company-name">{{ job.company || 'Компания не указана' }}</span>
            </div>
            <p class="job-description">{{ truncate(job.description, 200) }}</p>
          </div>

          <div class="card-sidebar">
            <button v-if="authStore.user?.role === 'seeker'" @click.stop="toggleLike(job)" class="like-btn" :class="{'liked': job.is_liked}">
              <Heart :size="28" :fill="job.is_liked ? 'currentColor' : 'none'" />
            </button>
            <div class="date-info">
              <span class="date">{{ formatDate(job.created_at) }}</span>
            </div>
            <button @click="router.push(`/vacancies/${job.id}`)" class="details-btn">Подробнее</button>
          </div>

        </div>
      </div>

      <!-- ПАГИНАЦИЯ -->
      <div class="pagination" v-if="totalPages > 1">
        <button @click="setPage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn"><ChevronLeft :size="20" /></button>
        <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="setPage(currentPage + 1)" :disabled="currentPage === totalPages" class="page-btn"><ChevronRight :size="20" /></button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }

/* Панель управления */
.controls-panel { display: flex; justify-content: space-between; align-items: center; padding: 20px; margin-bottom: 20px; flex-wrap: wrap; gap: 20px; }
.card { background: var(--bg-card); border-radius: 16px; border: 1px solid var(--border-color); box-shadow: var(--shadow); }
.search-input-wrapper { display: flex; align-items: center; background: var(--bg-main); border: 1px solid var(--border-color); border-radius: 12px; padding: 5px; flex-grow: 1; max-width: 600px; }
.search-icon { margin: 0 15px; color: var(--text-muted); }
.search-input-wrapper input { flex-grow: 1; border: none; background: transparent; padding: 10px; color: var(--text-main); outline: none; font-size: 1rem; }
.btn-search { background: var(--primary); color: white; padding: 10px 24px; border-radius: 10px; font-weight: 700; transition: 0.2s; }
.btn-search:hover { background: var(--primary-hover); }

.sort-wrapper { display: flex; align-items: center; gap: 10px; font-weight: 600; }
.sort-select { padding: 10px 16px; border-radius: 10px; border: 1px solid var(--border-color); background: var(--bg-main); color: var(--text-main); outline: none; }

.results-info { margin-bottom: 20px; color: var(--text-muted); font-size: 1.1rem; }

/* Вертикальный список */
.vacancy-list { display: flex; flex-direction: column; gap: 20px; }
.wide-card { display: flex; justify-content: space-between; padding: 30px; transition: 0.2s; }
.wide-card:hover { transform: translateY(-3px); border-color: var(--primary); }

.card-main-content { flex-grow: 1; padding-right: 30px; }
.card-header { display: flex; align-items: center; gap: 15px; margin-bottom: 12px; }
.job-title { font-size: 1.4rem; font-weight: 800; color: var(--primary); cursor: pointer; transition: 0.2s; display: flex; align-items: center; gap: 10px;}
.job-title:hover { text-decoration: underline; }
.viewed-badge { display: inline-flex; align-items: center; gap: 4px; font-size: 0.75rem; background: var(--bg-main); color: var(--text-muted); padding: 4px 8px; border-radius: 8px; font-weight: 600; border: 1px solid var(--border-color); text-decoration: none; }

.company-info { display: flex; align-items: center; gap: 8px; color: var(--text-main); font-weight: 600; margin-bottom: 15px; }
.job-description { color: var(--text-muted); line-height: 1.6; }

.source-tag { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; padding: 4px 10px; border-radius: 8px; }
.source-tag.internal { background: #e0e7ff; color: #4338ca; }
.source-tag.hh { background: #fee2e2; color: #dc2626; }

/* Боковая часть карточки (Сайдбар) */
.card-sidebar { width: 180px; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end; border-left: 1px solid var(--border-color); padding-left: 30px; }
.like-btn { color: var(--border-color); transition: 0.2s; padding: 4px; }
.like-btn:hover { color: #ec4899; transform: scale(1.1); }
.like-btn.liked { color: #ec4899; }

.date-info { text-align: right; margin-bottom: 15px; color: var(--text-muted); font-size: 0.9rem; }
.details-btn { width: 100%; padding: 12px; border-radius: 10px; background: var(--bg-main); color: var(--primary); font-weight: 700; border: 1px solid var(--primary); transition: 0.2s; }
.details-btn:hover { background: var(--primary); color: white; }

/* Пагинация */
.pagination { margin-top: 40px; display: flex; justify-content: center; align-items: center; gap: 20px; }
.page-btn { padding: 10px; border-radius: 12px; background: var(--bg-card); border: 1px solid var(--border-color); transition: 0.2s; display: flex; }
.page-btn:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-weight: 700; color: var(--text-muted); }

.loader-container { display: flex; justify-content: center; padding: 80px; }
.spinner { width: 40px; height: 40px; border: 4px solid var(--border-color); border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:translateY(0)} }

@media (max-width: 768px) {
  .wide-card { flex-direction: column; }
  .card-main-content { padding-right: 0; margin-bottom: 20px; }
  .card-sidebar { width: 100%; border-left: none; border-top: 1px solid var(--border-color); padding-left: 0; padding-top: 20px; flex-direction: row; align-items: center; }
}
</style>