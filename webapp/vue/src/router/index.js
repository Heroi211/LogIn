import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue'; // Caminho relativo correto

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView
  },
  // Outras rotas
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

export default router;