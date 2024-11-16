import { createRouter, createWebHistory } from 'vue-router/auto'
import Login from '@/pages/Login.vue';
import Routines from '@/pages/Routines.vue';
import Clients from "@/pages/Clients.vue";
import Users from '@/pages/Users.vue';

const routes = [
  {
    path: '/',
    redirect: '/login' // Redireciona a raiz para /login
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, hideNavbar: true }
  },
  // {
  //   path: '/home',
  //   name: 'Home',
  //   component: HomeView,
  //   meta: { requiresAuth: true }
  // },
  // {
  //   path: '/signup',
  //   name: 'Signup',
  //   component: SignupView,
  //   meta: { requiresAuth: false, hideNavbar: true }
  // },
  // {
  //   path: '/forgotpassword',
  //   name: 'ForgotPassword',
  //   component: ForgotPasswordView,
  //   meta: { requiresAuth: false, hideNavbar: true }
  // },
  // {
  //   path: '/resetpassword',
  //   name: 'ResetPassword',
  //   component: ResetPasswordView,
  //   meta: { requiresAuth: false, hideNavbar: true }
  // },
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
