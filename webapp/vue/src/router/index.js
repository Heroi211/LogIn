import Clients from "@/pages/Clients.vue";
import ForgotPassword from '@/pages/ForgotPassword.vue';
import Home from '@/pages/Home.vue';
import Login from '@/pages/Login.vue';
import ResetPassword from '@/pages/ResetPassword.vue';
import Routines from '@/pages/Routines.vue';
import Signup from '@/pages/Signup.vue';
import Users from '@/pages/Users.vue';

import { createRouter, createWebHistory } from 'vue-router/auto';

const routes = [
  {
    path: '/',
    redirect: '/home' // Redireciona a raiz para /home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, hideNavbar: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/signup',
    name: 'Signup',
    component: Signup,
    meta: { requiresAuth: false, hideNavbar: true }
  },
  {
    path: '/forgotpassword',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { requiresAuth: false, hideNavbar: true }
  },
  {
    path: '/resetpassword',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: { requiresAuth: false, hideNavbar: true }
  },
  {
    path: '/routines',
    name: 'Routines',
    component: Routines,
    meta: { requiresAuth: true, hideNavbar: false }
  },
  {
    path: '/users',
    name: 'Users',
    component: Users,
    meta: { requiresAuth: true, hideNavbar: false }
  },
  {
    path: '/clients',
    name: 'Clients',
    component: Clients,
    meta: { requiresAuth: true, hideNavbar: false }
  },
  // Outras rotas
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token');
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router
