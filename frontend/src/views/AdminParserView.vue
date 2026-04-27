<script setup lang="ts">
import { ref } from 'vue'
import { DownloadCloud, Settings, Database } from 'lucide-vue-next'
import api from '../api'

const parseQuery = ref('Python')
const parsePages = ref(1)
const isParsing = ref(false)

const startParser = async () => {
  isParsing.value = true
  try {
    const res = await api.post(`/admin/parse/hh?query=${parseQuery.value}&pages=${parsePages.value}`)
    alert(res.data.message)
  } catch (error) {
    alert('Ошибка запуска парсера')
  } finally {
    isParsing.value = false
  }
}
</script>

<template>
  <div class="admin-page fade-in">
    <div class="container">
      
      <div class="admin-header">
        <div class="header-text">
          <h1 class="title">Сбор данных</h1>
          <p class="subtitle">Управление парсерами и интеграциями</p>
        </div>
      </div>

      <!-- Блок парсера HH.ru -->
      <div class="card parse-card mb-4">
        <div class="parse-header">
          <div class="header-icon hh-icon">
            <DownloadCloud :size="24" />
          </div>
          <div>
            <h3>Парсер HeadHunter (HH.ru)</h3>
            <p>Запуск автоматического сбора вакансий через открытое API.</p>
          </div>
        </div>
        
        <div class="parse-controls">
          <div class="input-group">
            <label>Поисковый запрос</label>
            <input v-model="parseQuery" type="text" placeholder="Например: Frontend Developer" />
          </div>
          <div class="input-group">
            <label>Количество страниц (1 стр = 20 вакансий)</label>
            <input v-model="parsePages" type="number" min="1" max="100" />
          </div>
          <button @click="startParser" class="btn-parse" :disabled="isParsing">
            <Settings v-if="isParsing" class="spin-icon" :size="20"/> 
            <Database v-else :size="20"/> 
            {{ isParsing ? 'Сбор запущен...' : 'Старт парсинга' }}
          </button>
        </div>
      </div>

      <!-- В будущем сюда можно добавить парсер Авито -->

    </div>
  </div>
</template>

<style scoped>
.admin-page { padding: 40px 0; min-height: 100vh; }
.container { max-width: 1100px; margin: 0 auto; padding: 0 20px; }

.admin-header { margin-bottom: 32px; display: flex; justify-content: space-between; align-items: flex-end; }
.title { font-size: 2.2rem; font-weight: 800; margin-bottom: 4px; color: var(--text-main); }
.subtitle { color: var(--text-muted); font-size: 1.1rem; }

.card {
  background-color: var(--bg-card);
  border-radius: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow);
  overflow: hidden;
}

.parse-card { padding: 30px; }
.parse-header { display: flex; align-items: center; gap: 20px; margin-bottom: 30px; }
.parse-header h3 { font-size: 1.5rem; font-weight: 800; color: var(--text-main); }
.parse-header p { color: var(--text-muted); font-size: 1rem; margin-top: 5px; }

.header-icon { padding: 15px; border-radius: 16px; display: flex; align-items: center; justify-content: center; }
.hh-icon { background: rgba(220, 38, 38, 0.1); color: #dc2626; } /* Красный цвет для HH */

.parse-controls { display: flex; align-items: flex-end; gap: 20px; flex-wrap: wrap; background: var(--bg-main); padding: 25px; border-radius: 16px; border: 1px solid var(--border-color); }
.parse-controls .input-group { flex: 1; min-width: 250px; }
.parse-controls label { font-size: 0.85rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; margin-bottom: 10px; display: block;}
.parse-controls input { width: 100%; padding: 14px 18px; border: 1px solid var(--border-color); border-radius: 12px; background: var(--bg-card); color: var(--text-main); outline: none; font-size: 1rem; transition: 0.2s;}
.parse-controls input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1); }

.btn-parse { display: flex; align-items: center; gap: 10px; background: var(--primary); color: white; padding: 14px 30px; border-radius: 12px; font-weight: 700; font-size: 1.05rem; transition: 0.2s; white-space: nowrap; border: none; cursor: pointer; }
.btn-parse:hover:not(:disabled) { background: var(--primary-hover); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3); }
.btn-parse:disabled { opacity: 0.7; cursor: wait; }

.spin-icon { animation: spin 2s linear infinite; }

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeIn 0.4s ease-out; }
</style>