<script setup lang="ts">
import { useAuthStore } from './stores/auth'
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { Briefcase, Sun, Moon, LogOut, User, ChevronDown, Shield, FileText, Heart, Database} from 'lucide-vue-next'

const authStore = useAuthStore()
const isDark = ref(false)
const isMenuOpen = ref(false) // Состояние выпадающего меню

// Логика переключения темы
const toggleTheme = () => {
  isDark.value = !isDark.value
  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    html.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// Переключение меню
const toggleMenu = (event: Event) => {
  event.stopPropagation()
  isMenuOpen.value = !isMenuOpen.value
}

// Закрытие меню при клике в любое другое место
const closeMenu = () => {
  isMenuOpen.value = false
}

const getAvatarUrl = (path: string) => `http://localhost:8000${path}`

onMounted(() => {
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
  authStore.fetchUser()
  window.addEventListener('click', closeMenu)
})

onUnmounted(() => {
  window.removeEventListener('click', closeMenu)
})
</script>

<template>
  <div class="app-wrapper">
    <header class="header">
      <div class="container header-content">
        
        <RouterLink to="/" class="logo-container">
          <div class="logo-icon">
            <Briefcase :size="20" stroke-width="2.5" />
          </div>
          <span class="logo-text">JobParser</span>
        </RouterLink>

        <div class="nav-links">
          <RouterLink to="/" class="nav-link">Главная</RouterLink>
          <RouterLink to="/vacancies" class="nav-link">Все вакансии</RouterLink>
          <RouterLink v-if="authStore.user?.role === 'seeker'" to="/recommendations" class="nav-link highlight-link">Рекомендации</RouterLink>
          
          <button @click="toggleTheme" class="icon-btn theme-btn" title="Переключить тему">
            <Sun v-if="isDark" :size="22" />
            <Moon v-else :size="22" />
          </button>

          <RouterLink v-if="!authStore.user" to="/login" class="btn-primary">
            Войти
          </RouterLink>

          <!-- Выпадающее меню пользователя -->
          <div v-else class="user-dropdown-container">
            <button @click="toggleMenu" class="avatar-trigger">
              <div class="avatar-circle">
                <img v-if="authStore.user.avatar" :src="getAvatarUrl(authStore.user.avatar)" class="avatar-img" />
                <!-- Инициалы, если нет аватарки -->
                <span v-else class="avatar-initials">
                  {{ (authStore.user.full_name || authStore.user.email).charAt(0).toUpperCase() }}
                </span>
              </div>
              <ChevronDown :size="16" :class="{ 'rotate': isMenuOpen }" class="chevron" />
            </button>

            <!-- Само выпадающее меню -->
            <transition name="slide-fade">
              <div v-if="isMenuOpen" class="dropdown-menu" @click.stop>
                <div class="dropdown-header">
                  <p class="user-fio">{{ authStore.user.full_name || 'Пользователь' }}</p>
                  <p class="user-email">{{ authStore.user.email }}</p>
                </div>
                
                <hr class="divider" />
                
                <RouterLink to="/profile" class="dropdown-item" @click="closeMenu">
                  <User :size="18" />
                  <span>Профиль</span>
                </RouterLink>

                <RouterLink v-if="authStore.user?.role === 'recruiter'" to="/recruiter/vacancies" class="dropdown-item" @click="closeMenu">
                  <Briefcase :size="18" />
                  <span>Мои вакансии</span>
                </RouterLink>

                <RouterLink v-if="authStore.user?.role === 'seeker'" to="/seeker/applications" class="dropdown-item" @click="closeMenu">
                  <FileText :size="18" />
                  <span>Мои отклики</span>
                </RouterLink>

                <RouterLink v-if="authStore.user?.role === 'seeker'" to="/seeker/favorites" class="dropdown-item" @click="closeMenu">
                  <Heart :size="18" />
                  <span>Избранное</span>
                </RouterLink>

                <RouterLink v-if="authStore.user?.role === 'admin'" to="/admin/users" class="dropdown-item" @click="closeMenu">
                  <Shield :size="18" />
                  <span>Пользователи</span>
                </RouterLink>

                <RouterLink v-if="authStore.user?.role === 'admin'" to="/admin/parser" class="dropdown-item" @click="closeMenu">
                  <Database :size="18" />
                  <span>Сбор данных</span>
                </RouterLink>
                
                <button @click="authStore.logout" class="dropdown-item logout-item">
                  <LogOut :size="18" />
                  <span>Выйти</span>
                </button>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </header>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-wrapper { display: flex; flex-direction: column; min-height: 100vh; }

.header {
  background-color: var(--bg-header);
  box-shadow: var(--shadow);
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: background-color var(--transition);
}

.container { max-width: 1200px; margin: 0 auto; padding: 0 20px; height: 100%; }
.header-content { display: flex; align-items: center; justify-content: space-between; height: 100%; }

.logo-container { display: flex; align-items: center; gap: 10px; transition: transform 0.2s; }
.logo-container:hover { transform: scale(1.05); }

.logo-icon {
  width: 36px; height: 36px;
  background-color: var(--primary);
  color: white;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}

.logo-text { font-size: 1.3rem; font-weight: 800; color: var(--primary); }

.nav-links { display: flex; align-items: center; gap: 20px; }
.nav-link { font-weight: 500; transition: color 0.2s; }
.nav-link:hover { color: var(--primary); }

/* Аватарка и выпадашка */
.user-dropdown-container { position: relative; }

.avatar-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px;
  border-radius: 30px;
  transition: background-color 0.2s;
  border: 1px solid transparent;
}
.avatar-trigger:hover { background-color: var(--border-color); }

.avatar-circle {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background-color: var(--primary);
  color: white;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--primary);
  font-weight: 700; /* Жирный шрифт для буквы */
  font-size: 1.1rem;
}

.avatar-initials {
  line-height: 1;
  user-select: none;
}

.avatar-img { width: 100%; height: 100%; object-fit: cover; }

.chevron { transition: transform 0.3s; color: var(--text-muted); }
.rotate { transform: rotate(180deg); }

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 240px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  padding: 8px;
  z-index: 1001;
}

.dropdown-header { padding: 12px 16px; }
.user-fio { font-weight: 700; font-size: 0.95rem; margin-bottom: 2px; }
.user-email { font-size: 0.8rem; color: var(--text-muted); }

.divider { border: 0; border-top: 1px solid var(--border-color); margin: 8px 0; }

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px; /* Расстояние между иконкой и текстом */
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-main);
  transition: all 0.2s;
  width: 100%;
}

.dropdown-item svg {
  flex-shrink: 0; /* Иконка не должна сжиматься */
  color: var(--text-muted);
}
.dropdown-item:hover { background-color: var(--bg-main); color: var(--primary); }
.logout-item { color: #ef4444; }
.logout-item:hover { background-color: #fef2f2; color: #ef4444; }
.dropdown-item:hover svg {
  color: var(--primary);
}
/* Анимация меню */
.slide-fade-enter-active { transition: all 0.2s ease-out; }
.slide-fade-leave-active { transition: all 0.15s ease-in; }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }

.icon-btn { padding: 8px; border-radius: 50%; transition: all 0.2s; color: var(--text-muted); }
.icon-btn:hover { background-color: var(--border-color); color: var(--text-main); }

.btn-primary {
  background-color: var(--primary); color: white;
  padding: 8px 20px; border-radius: 8px; font-weight: 600;
  transition: all 0.2s;
}
.btn-primary:hover { background-color: var(--primary-hover); transform: translateY(-2px); }

.main-content { flex-grow: 1; }
</style>