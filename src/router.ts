import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import Index from './pages/Index.vue';
import LandingPage from './pages/LandingPage.vue';
import NewFiling from './pages/NewFiling.vue';
import Filings from './pages/Filings.vue';
import Chat from './pages/Chat.vue';
import Documents from './pages/Documents.vue';
import Login from './pages/Login.vue';
import NotFound from './pages/NotFound.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'LandingPage',
      component: LandingPage,
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('./pages/Register.vue'),
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: Index,
      meta: { requiresAuth: true },
    },
    {
      path: '/filing/new',
      name: 'NewFiling',
      component: NewFiling,
      meta: { requiresAuth: true },
    },
    {
      path: '/filings',
      name: 'Filings',
      component: Filings,
      meta: { requiresAuth: true },
    },
    {
      path: '/chat',
      name: 'Chat',
      component: Chat,
      meta: { requiresAuth: true },
    },
    {
      path: '/documents',
      name: 'Documents',
      component: () => import('./pages/Documents.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/reports',
      name: 'Reports',
      component: () => import('./pages/Reports.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'Settings',
      component: () => import('./pages/Settings.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/help',
      name: 'Help',
      component: () => import('./pages/Help.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/contact',
      name: 'Contact',
      component: () => import('./pages/Contact.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/filing/grid',
      name: 'FilingGrid',
      component: () => import('./pages/FilingGrid.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/filing/wizard',
      name: 'WizardFiling',
      component: () => import('./pages/WizardFiling.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFound,
    },
  ],
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard');
  } else {
    next();
  }
});

export default router;
