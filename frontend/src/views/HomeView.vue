<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from 'lucide-vue-next'

const router = useRouter()
const searchQuery = ref('')

// Перенаправляем на страницу всех вакансий с параметром поиска
const handleSearch = () => {
  router.push({ path: '/vacancies', query: { search: searchQuery.value } })
}
</script>

<template>
  <div class="home-container">
    <section class="hero">
      <div class="hero-overlay"></div> 
      <div class="hero-content">
        <h1 class="hero-title">Найдите работу своей <span class="highlight">мечты</span></h1>
        <p class="hero-subtitle">Умная рекомендательная система на основе машинного обучения подберет вакансии специально для вас.</p>
        <div class="search-box">
          <input v-model="searchQuery" type="text" placeholder="Профессия, навыки или компания..." @keyup.enter="handleSearch" />
          <button @click="handleSearch" class="search-btn" title="Найти">
            <Search :size="24" stroke-width="2.5" />
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.fade-in { animation: fadeInUp 0.8s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.home-container { min-height: calc(100vh - 64px); display: flex; flex-direction: column; }
.hero { flex-grow: 1; display: flex; align-items: center; justify-content: center; position: relative; background-image: url('../assets/bg.jpg'); background-size: cover; background-position: center; padding: 20px; text-align: center; }
.hero-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: var(--bg-main); opacity: 0.8; }
.hero-content { position: relative; z-index: 1; width: 100%; max-width: 800px; }
.hero-title { font-size: 3.5rem; font-weight: 800; margin-bottom: 20px; line-height: 1.2; }
.highlight { color: var(--primary); }
.hero-subtitle { font-size: 1.25rem; color: var(--text-muted); margin-bottom: 40px; font-weight: 500; }

.search-box { display: flex; gap: 5px; background-color: var(--bg-card); padding: 10px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.15); border: 1px solid var(--border-color); }
.search-box input { flex-grow: 1; border: none; background: transparent; padding: 15px 25px; font-size: 1.1rem; color: var(--text-main); outline: none; }
.search-btn { display: flex; align-items: center; justify-content: center; background-color: var(--primary); color: white; width: 65px; height: 55px; border-radius: 15px; transition: 0.2s; }
.search-btn:hover { background-color: var(--primary-hover); transform: scale(1.05); }

@media (max-width: 768px) { .hero-title { font-size: 2.5rem; } }
</style>