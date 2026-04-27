<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Shield, User, Briefcase, Trash2, Edit2, X, AlertTriangle, ChevronLeft, ChevronRight, Search } from 'lucide-vue-next'
import api from '../api'

const users = ref<any[]>([])
const totalUsers = ref(0)
const isLoading = ref(true)
const currentPage = ref(1)
const itemsPerPage = 8
const totalPages = computed(() => Math.ceil(totalUsers.value / itemsPerPage))

const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedUser = ref<any>(null)
const newRole = ref('')

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const skip = (currentPage.value - 1) * itemsPerPage
    const response = await api.get(`/admin/users?skip=${skip}&limit=${itemsPerPage}`)
    users.value = response.data.users
    totalUsers.value = response.data.total
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const setPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchUsers()
}

const openEditModal = (user: any) => {
  selectedUser.value = user
  newRole.value = user.role
  showEditModal.value = true
}

const openDeleteModal = (user: any) => {
  selectedUser.value = user
  showDeleteModal.value = true
}

const closeModals = () => {
  showEditModal.value = false
  showDeleteModal.value = false
  selectedUser.value = null
}

const confirmChangeRole = async () => {
  try {
    await api.put(`/admin/users/${selectedUser.value.id}/role?role=${newRole.value}`)
    closeModals()
    fetchUsers()
  } catch (error) { alert('Ошибка') }
}

const confirmDelete = async () => {
  try {
    await api.delete(`/admin/users/${selectedUser.value.id}`)
    closeModals()
    fetchUsers()
  } catch (error: any) { alert(error.response?.data?.detail) }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="admin-page fade-in">
    <div class="container">
      
      <div class="admin-header">
        <div class="header-text">
          <h1 class="title">Управление пользователями</h1>
          <p class="subtitle">Всего в системе: <span>{{ totalUsers }}</span></p>
        </div>
      </div>

      <div class="card table-card">
        <div v-if="isLoading" class="loader-container">
          <div class="spinner"></div>
        </div>

        <div v-else class="table-wrapper">
          <table class="custom-table">
            <thead>
              <tr>
                <th>Пользователь</th>
                <th>Роль</th>
                <th class="text-right">Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>
                  <div class="user-info-cell">
                    <div class="mini-avatar">
                      {{ (user.full_name || user.email).charAt(0).toUpperCase() }}
                    </div>
                    <div class="details">
                      <p class="name">{{ user.full_name || 'Без имени' }}</p>
                      <p class="email">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="role-badge" :class="user.role">
                    <Shield v-if="user.role === 'admin'" :size="12" />
                    <Briefcase v-else-if="user.role === 'recruiter'" :size="12" />
                    <User v-else :size="12" />
                    <span>{{ user.role }}</span>
                  </div>
                </td>
                <td>
                  <div class="actions-cell">
                    <button @click="openEditModal(user)" class="btn-action edit" title="Изменить роль">
                      <Edit2 :size="18" />
                    </button>
                    <button @click="openDeleteModal(user)" class="btn-action delete" title="Удалить пользователя">
                      <Trash2 :size="18" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- ПАГИНАЦИЯ -->
          <div class="pagination-container" v-if="totalPages > 1">
            <button @click="setPage(currentPage - 1)" :disabled="currentPage === 1" class="p-btn">
              <ChevronLeft :size="20" />
            </button>
            <div class="p-info">Страница {{ currentPage }} из {{ totalPages }}</div>
            <button @click="setPage(currentPage + 1)" :disabled="currentPage === totalPages" class="p-btn">
              <ChevronRight :size="20" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- МОДАЛКА: РОЛЬ -->
    <div v-if="showEditModal" class="modal-overlay" @click="closeModals">
      <div class="modal-window scale-in" @click.stop>
        <div class="modal-header">
          <h3>Изменить роль</h3>
          <button @click="closeModals" class="close-icon"><X :size="20"/></button>
        </div>
        <div class="modal-body">
          <p class="modal-text">Выберите новую роль для <b>{{ selectedUser?.email }}</b>:</p>
          <select v-model="newRole" class="styled-select">
            <option value="seeker">Соискатель (Seeker)</option>
            <option value="recruiter">Рекрутер (Recruiter)</option>
            <option value="admin">Администратор (Admin)</option>
          </select>
        </div>
        <div class="modal-footer">
          <button @click="closeModals" class="btn-cancel">Отмена</button>
          <button @click="confirmChangeRole" class="btn-confirm">Сохранить</button>
        </div>
      </div>
    </div>

    <!-- МОДАЛКА: УДАЛЕНИЕ -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeModals">
      <div class="modal-window scale-in" @click.stop>
        <div class="modal-header danger-head">
          <AlertTriangle :size="24" />
          <h3>Удаление пользователя</h3>
        </div>
        <div class="modal-body">
          <p>Вы уверены, что хотите удалить <b>{{ selectedUser?.email }}</b>?</p>
          <p class="warn">Это действие удалит все данные, связанные с этим аккаунтом.</p>
        </div>
        <div class="modal-footer">
          <button @click="closeModals" class="btn-cancel">Отмена</button>
          <button @click="confirmDelete" class="btn-danger-action">Удалить навсегда</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

.admin-header { margin-bottom: 32px; display: flex; justify-content: space-between; align-items: flex-end; }
.title { font-size: 2.2rem; font-weight: 800; margin-bottom: 4px; }
.subtitle { color: var(--text-muted); font-size: 1.1rem; }
.subtitle span { color: var(--primary); font-weight: 700; }

.card {
  background-color: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  overflow: hidden;
}

/* Таблица */
.table-wrapper { overflow-x: auto; }
.custom-table { width: 100%; border-collapse: collapse; min-width: 600px; }
.custom-table th {
  background-color: var(--bg-main);
  padding: 16px 24px;
  text-align: left;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
}
.custom-table td { padding: 16px 24px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
.custom-table tr:last-child td { border-bottom: none; }
.custom-table tr:hover td { background-color: var(--bg-main); }

.user-info-cell { display: flex; align-items: center; gap: 16px; }
.mini-avatar {
  width: 42px; height: 42px; border-radius: 12px;
  background-color: var(--primary); color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 1.1rem; flex-shrink: 0;
}
.details .name { font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.details .email { font-size: 0.85rem; color: var(--text-muted); }

.role-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: 30px;
  font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
}
.role-badge.admin { background-color: #fef2f2; color: #ef4444; border: 1px solid #fee2e2; }
.role-badge.recruiter { background-color: #f5f3ff; color: var(--primary); border: 1px solid #ede9fe; }
.role-badge.seeker { background-color: var(--bg-main); color: var(--text-muted); border: 1px solid var(--border-color); }

.actions-cell { display: flex; gap: 10px; justify-content: flex-end; }
.btn-action {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.edit { color: var(--primary); background: #f5f3ff; }
.edit:hover { background: var(--primary); color: white; }
.delete { color: #ef4444; background: #fef2f2; }
.delete:hover { background: #ef4444; color: white; }

/* Пагинация */
.pagination-container {
  display: flex; align-items: center; justify-content: center;
  gap: 25px; padding: 25px; background: var(--bg-main);
}
.p-btn {
  width: 40px; height: 40px; border-radius: 10px;
  background: var(--bg-card); border: 1px solid var(--border-color);
  display: flex; align-items: center; justify-content: center;
  transition: 0.2s;
}
.p-btn:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); }
.p-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.p-info { font-weight: 700; color: var(--text-muted); font-size: 0.95rem; }

/* Модалки */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); backdrop-filter: blur(5px);
  display: flex; align-items: center; justify-content: center; z-index: 2000;
}
.modal-window {
  background: var(--bg-card); width: 90%; max-width: 460px;
  border-radius: 24px; box-shadow: 0 25px 50px rgba(0,0,0,0.4);
  overflow: hidden; border: 1px solid var(--border-color);
}
.modal-header {
  padding: 24px; display: flex; justify-content: space-between; align-items: center;
  border-bottom: 1px solid var(--border-color);
}
.danger-head { background: #fff1f2; color: #e11d48; border-bottom: none; }
.modal-body { padding: 30px 24px; }
.styled-select {
  width: 100%; padding: 14px; border-radius: 12px; margin-top: 15px;
  background: var(--bg-main); border: 1px solid var(--border-color);
  color: var(--text-main); font-size: 1rem; outline: none;
}
.warn { color: #e11d48; font-size: 0.85rem; margin-top: 10px; font-weight: 600; }
.modal-footer { padding: 20px 24px; background: var(--bg-main); display: flex; justify-content: flex-end; gap: 15px; }

.btn-cancel { font-weight: 700; color: var(--text-muted); }
.btn-confirm { background: var(--primary); color: white; padding: 12px 24px; border-radius: 12px; font-weight: 700; }
.btn-danger-action { background: #e11d48; color: white; padding: 12px 24px; border-radius: 12px; font-weight: 700; }

.spinner {
  width: 40px; height: 40px; border: 4px solid var(--border-color);
  border-top-color: var(--primary); border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.scale-in { animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
@keyframes scaleIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>