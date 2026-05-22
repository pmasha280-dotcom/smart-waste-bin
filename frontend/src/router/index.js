import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Временное отключение guard для диагностики
router.beforeEach((to, from, next) => {
  console.log('Router: navigating to', to.path)
  next()
})

export default router
