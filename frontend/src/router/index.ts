import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import AdminUsersView from '../views/AdminUsersView.vue'
import RecruiterVacanciesView from '../views/RecruiterVacanciesView.vue'
import VacancyDetailView from '../views/VacancyDetailView.vue'
import SeekerApplicationsView from '../views/SeekerApplicationsView.vue'
import SeekerFavoritesView from '../views/SeekerFavoritesView.vue'
import RecruiterVacancyApplicationsView from '../views/RecruiterVacancyApplicationsView.vue'
import AllVacanciesView from '../views/AllVacanciesView.vue'
import RecommendationsView from '../views/RecommendationsView.vue'
import AdminParserView from '../views/AdminParserView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/profile', name: 'profile', component: ProfileView },
    { path: '/admin/users', name: 'admin-users', component: AdminUsersView },
    { path: '/recruiter/vacancies', name: 'recruiter-vacancies', component: RecruiterVacanciesView },
    { path: '/vacancies/:id', name: 'vacancy-detail', component: VacancyDetailView },
    { path: '/seeker/applications', name: 'seeker-applications', component: SeekerApplicationsView },
    { path: '/seeker/favorites', name: 'seeker-favorites', component: SeekerFavoritesView },
    { path: '/recruiter/vacancies/:id/applications', name: 'vacancy-applications', component: RecruiterVacancyApplicationsView },
    { path: '/vacancies', name: 'all-vacancies', component: AllVacanciesView },
    { path: '/recommendations', name: 'recommendations', component: RecommendationsView },
    {path: '/admin/parser', name: 'admin-parser', component: AdminParserView },
  ]
})

export default router