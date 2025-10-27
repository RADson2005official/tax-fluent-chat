import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { TooltipProvider } from 'radix-vue';
import App from './App.vue';
import router from './router';
import './index.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.component('TooltipProvider', TooltipProvider);
app.mount('#root');

