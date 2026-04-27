import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router' // Мы создавали этот файл в папке router ранее
import './assets/main.css'

const app = createApp(App)

app.use(createPinia()) // Подключаем хранилище
app.use(router)      // Подключаем роутер

app.mount('#app')