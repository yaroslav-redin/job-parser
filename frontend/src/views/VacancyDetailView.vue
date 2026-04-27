<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Building, MapPin, ArrowLeft, Send, Edit3, X, CheckCircle, Heart } from 'lucide-vue-next'
import api from '../api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const vacancy = ref<any>(null)
const isLoading = ref(true)

// Состояние для редактирования
const showEditModal = ref(false)
const editForm = ref({ title: '', description: '', is_published: true })

const toggleLike = async () => {
  if (authStore.user?.role !== 'seeker') return;
  try {
    const res = await api.post(`/vacancies/${vacancy.value.id}/like`);
    vacancy.value.is_liked = res.data.status === 'liked';
  } catch (e) {}
}

const fetchVacancy = async () => {
  try {
    const res = await api.get(`/vacancies/${route.params.id}`)
    vacancy.value = res.data

    // ОТПРАВЛЯЕМ СОБЫТИЕ ПРОСМОТРА ДЛЯ ML
    if (authStore.user?.role === 'seeker') {
      api.post(`/vacancies/${vacancy.value.id}/view`).catch(()=>{})
    }
  } catch (e) {
    router.push('/')
  } finally { isLoading.value = false }
}
const apply = async () => {
  try {
    await api.post(`/vacancies/${vacancy.value.id}/apply`)
    vacancy.value.is_applied = True // Обновляем состояние сразу после отклика
    alert('Отклик успешно отправлен!')
  } catch (e: any) {
    alert(e.response?.data?.detail || 'Ошибка при отклике')
  }
}

const openEditModal = () => {
  editForm.value = {
    title: vacancy.value.title,
    description: vacancy.value.description,
    is_published: vacancy.value.is_published
  }
  showEditModal.value = true
}

const saveChanges = async () => {
  try {
    const res = await api.put(`/recruiter/vacancies/${vacancy.value.id}`, editForm.value)
    vacancy.value = res.data
    showEditModal.value = false
    alert('Вакансия обновлена')
  } catch (e) {
    alert('Ошибка при сохранении')
  }
}

onMounted(fetchVacancy)
</script>

<template>
  <div class="vacancy-detail-page fade-in">
    <div class="container" v-if="vacancy">
      
      <button @click="router.back()" class="back-link">
        <ArrowLeft :size="18" /> Назад к списку
      </button>

      <div class="vacancy-card-large">
        <div class="card-header">
          <div class="title-section">
            <h1 class="vac-title">{{ vacancy.title }}</h1>
            <div class="meta-info">
              <span class="meta-item"><Building :size="18"/> {{ vacancy.company }}</span>
              <span class="meta-item"><MapPin :size="18"/> {{ vacancy.source === 'internal' ? 'На сайте' : 'Внешний источник' }}</span>
            </div>
          </div>
        </div>

        <hr class="divider" />

        <div class="card-body">
          <h3 class="section-title">Описание вакансии</h3>
          <div class="description-text">{{ vacancy.description }}</div>
        </div>

        <div class="card-footer-actions">
          <hr class="divider" />
          
          <div class="actions-row">
            <div class="author-status">
              <p v-if="authStore.user?.id === vacancy.author_id" class="admin-hint">Это ваша публикация</p>
            </div>

            <div class="buttons-group">
                <button v-if="authStore.user?.role === 'seeker'" 
                        @click="toggleLike" 
                        class="btn-favorite" 
                        :class="{'liked': vacancy.is_liked}">
                    <Heart :size="20" :fill="vacancy.is_liked ? 'currentColor' : 'none'" /> 
                    {{ vacancy.is_liked ? 'В избранном' : 'В избранное' }}
                </button>
              <!-- Для соискателя (Откликнуться) -->
              <button v-if="authStore.user?.role === 'seeker'" 
                      @click="apply" 
                      class="btn-apply" 
                      :class="{ 'applied': vacancy.is_applied }"
                      :disabled="vacancy.is_applied">
                <template v-if="vacancy.is_applied">
                  <CheckCircle :size="18" /> Вы откликнулись
                </template>
                <template v-else>
                  <Send :size="18" /> Откликнуться
                </template>
              </button>

              <!-- Для автора-рекрутера (Редактировать) -->
              <button v-if="authStore.user?.id === vacancy.author_id" 
                      @click="openEditModal" 
                      class="btn-edit">
                <Edit3 :size="18" /> Редактировать
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- МОДАЛКА -->
    <div v-if="showEditModal" class="modal-overlay" @click="showEditModal = false">
      <div class="modal-window scale-in" @click.stop>
        <div class="modal-header">
          <h3>Редактирование</h3>
          <button @click="showEditModal = false" class="close-btn"><X :size="20"/></button>
        </div>
        <form @submit.prevent="saveChanges">
          <div class="modal-body">
            <div class="input-group">
              <label>Должность</label>
              <input v-model="editForm.title" type="text" required />
            </div>
            <div class="input-group">
              <label>Описание</label>
              <textarea v-model="editForm.description" required rows="10"></textarea>
            </div>
            <div class="checkbox-group">
              <input type="checkbox" id="edit_pub" v-model="editForm.is_published" />
              <label for="edit_pub">Опубликована</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" @click="showEditModal = false" class="btn-cancel">Отмена</button>
            <button type="submit" class="btn-confirm">Сохранить</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.vacancy-detail-page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 900px; margin: 0 auto; padding: 0 20px; }

.back-link { display: flex; align-items: center; gap: 8px; color: var(--text-muted); margin-bottom: 24px; font-weight: 600; }
.back-link:hover { color: var(--primary); }

.vacancy-card-large { 
  background: var(--bg-card); 
  border-radius: 24px; padding: 40px; 
  border: 1px solid var(--border-color); 
  box-shadow: var(--shadow);
  color: var(--text-main);
}

.vac-title { font-size: 2.8rem; font-weight: 800; margin-bottom: 15px; }
.meta-info { display: flex; gap: 24px; color: var(--text-muted); }
.meta-item { display: flex; align-items: center; gap: 8px; font-weight: 500; font-size: 1.1rem; }

.divider { border: 0; border-top: 1px solid var(--border-color); margin: 30px 0; }

.card-body .section-title { margin-bottom: 20px; font-size: 1.5rem; font-weight: 700; }
.description-text { line-height: 1.8; white-space: pre-wrap; font-size: 1.1rem; }

.card-footer-actions { margin-top: 40px; }
.actions-row { display: flex; justify-content: space-between; align-items: center; }
.buttons-group { display: flex; gap: 16px; }

.btn-apply { 
  background: var(--primary); color: white; padding: 14px 35px; border-radius: 14px; 
  font-weight: 700; display: flex; align-items: center; gap: 10px; transition: 0.3s;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}
.btn-apply:hover:not(:disabled) { background: var(--primary-hover); transform: translateY(-3px); }

/* Стиль для кнопки "Вы откликнулись" */
.btn-apply.applied {
  background: #10b981; /* Зеленый */
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
  cursor: default;
}

.btn-edit { 
  background: var(--bg-main); color: var(--primary); border: 2px solid var(--primary); 
  padding: 12px 28px; border-radius: 12px; font-weight: 700; display: flex; align-items: center; gap: 10px; transition: 0.2s;
}
.btn-edit:hover { background: var(--primary); color: white; }

/* Модалка (темная тема) */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-window { background: var(--bg-card); width: 90%; max-width: 700px; border-radius: 24px; border: 1px solid var(--border-color); color: var(--text-main); }
.modal-header { padding: 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; }
.modal-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.input-group label { font-weight: 700; font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; }
.input-group input, .input-group textarea { padding: 14px; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-main); color: var(--text-main); font-family: inherit; outline: none; }
.modal-footer { padding: 20px 24px; background: var(--bg-main); display: flex; justify-content: flex-end; gap: 15px; }

.btn-confirm { background: var(--primary); color: white; padding: 12px 30px; border-radius: 12px; font-weight: 700; }

.fade-in { animation: fadeIn 0.4s ease-out; }
@keyframes fadeIn { from{opacity:0; transform: translateY(10px);} to{opacity:1; transform: translateY(0);} }
.btn-favorite { background: var(--bg-main); color: var(--text-muted); border: 1px solid var(--border-color); padding: 12px 24px; border-radius: 12px; font-weight: 700; display: flex; align-items: center; gap: 10px; transition: 0.2s; }
.btn-favorite:hover { border-color: #ec4899; color: #ec4899; }
.btn-favorite.liked { color: #ec4899; border-color: #ec4899; background: #fdf2f8; }
</style>