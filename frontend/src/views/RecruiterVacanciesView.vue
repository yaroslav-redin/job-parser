<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Edit2, Trash2, X, Eye, FileText } from 'lucide-vue-next'
import api from '../api'

const router = useRouter()
const vacancies = ref<any[]>([])
const total = ref(0)
const isLoading = ref(true)

const currentPage = ref(1)
const itemsPerPage = 6
const totalPages = computed(() => Math.ceil(total.value / itemsPerPage))

// Работа с модалкой
const showModal = ref(false)
const isEditMode = ref(false)
const selectedVacId = ref<number | null>(null)
const form = ref({ title: '', description: '', is_published: true })

const fetchVacancies = async () => {
  isLoading.value = true
  try {
    const skip = (currentPage.value - 1) * itemsPerPage
    const res = await api.get(`/recruiter/vacancies?skip=${skip}&limit=${itemsPerPage}`)
    vacancies.value = res.data.vacancies
    total.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const setPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchVacancies()
}

// Открытие для создания
const openCreateModal = () => {
  isEditMode.value = false
  selectedVacId.value = null
  form.value = { title: '', description: '', is_published: true }
  showModal.value = true
}

// Открытие для редактирования
const openEditModal = (vac: any) => {
  isEditMode.value = true
  selectedVacId.value = vac.id
  form.value = { 
    title: vac.title, 
    description: vac.description, 
    is_published: vac.is_published 
  }
  showModal.value = true
}

const handleSubmit = async () => {
  try {
    if (isEditMode.value && selectedVacId.value) {
      await api.put(`/recruiter/vacancies/${selectedVacId.value}`, form.value)
    } else {
      await api.post('/recruiter/vacancies', form.value)
    }
    showModal.value = false
    fetchVacancies()
  } catch (error) {
    alert('Ошибка при сохранении')
  }
}

const deleteVacancy = async (id: number) => {
  if (confirm('Удалить вакансию?')) {
    try {
      await api.delete(`/recruiter/vacancies/${id}`)
      fetchVacancies()
    } catch (error) { alert('Ошибка удаления') }
  }
}

onMounted(fetchVacancies)
</script>

<template>
  <div class="recruiter-page fade-in">
    <div class="container">
      
      <div class="page-header">
        <div>
          <h1 class="title">Мои вакансии</h1>
          <p class="subtitle">Управление публикациями компании</p>
        </div>
        <button @click="openCreateModal" class="btn-create">
          <Plus :size="20" /> Создать вакансию
        </button>
      </div>

      <div class="card table-card">
        <div v-if="isLoading" class="loader-container"><div class="spinner"></div></div>
        
        <div v-else-if="vacancies.length === 0" class="empty-state">
          <FileText :size="48" class="empty-icon" />
          <h3>У вас пока нет вакансий</h3>
          <p>Создайте первую вакансию, чтобы начать поиск кандидатов.</p>
        </div>

        <div v-else class="table-wrapper">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Должность</th>
                <th>Статус</th>
                <th>Отклики</th>
                <th class="text-right">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="vac in vacancies" :key="vac.id">
                <td>
                  <p class="vac-title">{{ vac.title }}</p>
                  <p class="vac-date">Создано: {{ new Date(vac.created_at).toLocaleDateString() }}</p>
                </td>
                <td>
                  <span class="status-badge" :class="vac.is_published ? 'active' : 'draft'">
                    {{ vac.is_published ? 'Опубликована' : 'Черновик' }}
                  </span>
                </td>
                <td>
                  <div class="applicants-count" 
                       :class="{ 'has-apps': vac.applications_count > 0 }"
                       @click="vac.applications_count > 0 ? router.push(`/recruiter/vacancies/${vac.id}/applications`) : null"
                       :style="vac.applications_count > 0 ? 'cursor: pointer;' : ''"
                       title="Смотреть кандидатов">
                      {{ vac.applications_count }} кандидатов
                  </div>
                </td>
                <td>
                  <div class="actions-cell">
                    <button @click="router.push(`/vacancies/${vac.id}`)" class="btn-action view" title="Смотреть">
                        <Eye :size="18" />
                    </button>
                    <button @click="openEditModal(vac)" class="btn-action edit-small" title="Редактировать">
                        <Edit2 :size="18" />
                    </button>
                    <button @click="deleteVacancy(vac.id)" class="btn-action delete" title="Удалить">
                        <Trash2 :size="18" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Пагинация -->
          <div class="pagination" v-if="totalPages > 1">
            <button @click="setPage(currentPage - 1)" :disabled="currentPage===1">Назад</button>
            <span>{{ currentPage }} / {{ totalPages }}</span>
            <button @click="setPage(currentPage + 1)" :disabled="currentPage===totalPages">Вперед</button>
          </div>
        </div>
      </div>
    </div>

    <!-- МОДАЛКА (Единая для Создания и Редактирования) -->
    <div v-if="showModal" class="modal-overlay" @click="showModal = false">
      <div class="modal-window scale-in" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditMode ? 'Редактировать вакансию' : 'Новая вакансия' }}</h3>
          <button @click="showModal = false" class="close-btn"><X :size="20"/></button>
        </div>
        <form @submit.prevent="handleSubmit">
          <div class="modal-body">
            <div class="input-group">
              <label>Должность</label>
              <input v-model="form.title" type="text" required placeholder="Например: Frontend Developer" />
            </div>
            <div class="input-group">
              <label>Описание и требования</label>
              <textarea v-model="form.description" required rows="8" placeholder="Опишите задачи, стек и условия..."></textarea>
            </div>
            <div class="checkbox-group">
              <input type="checkbox" id="pub_rec" v-model="form.is_published" />
              <label for="pub_rec">Опубликовать</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showModal = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-confirm">{{ isEditMode ? 'Сохранить' : 'Создать' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Добавляем стиль для новой кнопки редактирования в таблице */
.edit-small { color: var(--primary); background: #f5f3ff; margin-right: 5px; }
.edit-small:hover { background: var(--primary); color: white; }

/* Все остальные стили такие же, как были в твоем файле */
.recruiter-page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; }
.title { font-size: 2.2rem; font-weight: 800; }
.subtitle { color: var(--text-muted); font-size: 1.1rem; }
.btn-create { display: flex; align-items: center; gap: 8px; background: var(--primary); color: white; padding: 12px 24px; border-radius: 12px; font-weight: 700; transition: 0.2s; }
.card { background: var(--bg-card); border-radius: 20px; border: 1px solid var(--border-color); box-shadow: var(--shadow); overflow: hidden; }
.custom-table { width: 100%; border-collapse: collapse; }
.custom-table th { background: var(--bg-main); padding: 16px 24px; text-align: left; color: var(--text-muted); border-bottom: 1px solid var(--border-color); }
.custom-table td { padding: 16px 24px; border-bottom: 1px solid var(--border-color); }
.actions-cell { display: flex; gap: 8px; justify-content: flex-end; }
.btn-action { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; transition: 0.2s; }
.view { 
  color: var(--primary); 
  background: var(--bg-main); /* Было жестко светло-фиолетовым */
  border: 1px solid var(--border-color);
} 
.view:hover { background: var(--primary); color: white; }

.edit-small { 
  color: var(--primary); 
  background: var(--bg-main); 
  border: 1px solid var(--border-color);
  margin-right: 5px; 
}
.edit-small:hover { background: var(--primary); color: white; }

.delete { 
  color: #ef4444; 
  background: var(--bg-main); 
  border: 1px solid var(--border-color);
} 
.delete:hover { background: #ef4444; color: white; }

.applicants-count { 
  font-weight: 600; 
  color: var(--text-muted); 
  background: var(--bg-main); 
  padding: 6px 12px; 
  border-radius: 10px; 
  display: inline-block; 
  font-size: 0.85rem;
  border: 1px solid var(--border-color);
}
.applicants-count.has-apps {
  color: var(--primary);
  background: rgba(139, 92, 246, 0.1);
  border-color: var(--primary);
}
.delete { color: #ef4444; background: #fef2f2; } .delete:hover { background: #ef4444; color: white; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 2000; backdrop-filter: blur(4px); }
.modal-window { background: var(--bg-card); width: 90%; max-width: 600px; border-radius: 20px; border: 1px solid var(--border-color); overflow: hidden; }
.modal-header { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); }
.modal-body { padding: 24px; display: flex; flex-direction: column; gap: 16px; }
.input-group { display: flex; flex-direction: column; gap: 8px; }
.input-group input, .input-group textarea { padding: 12px; border: 1px solid var(--border-color); border-radius: 10px; background: var(--bg-main); color: var(--text-main); font-family: inherit; }
.modal-footer { padding: 20px 24px; background: var(--bg-main); display: flex; justify-content: flex-end; gap: 12px; }
.btn-confirm { background: var(--primary); color: white; padding: 10px 24px; border-radius: 10px; font-weight: 600; }
.view { 
  color: var(--primary); 
  background: var(--bg-main); /* Используем переменную вместо белого */
  border: 1px solid var(--border-color);
}
.edit-small { 
  color: var(--primary); 
  background: var(--bg-main); 
  border: 1px solid var(--border-color);
}
.delete { 
  color: #ef4444; 
  background: var(--bg-main); 
  border: 1px solid var(--border-color);
}
</style>