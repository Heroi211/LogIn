import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.css';
import { createApp } from 'vue';
import App from './App.vue';
import './assets/styles.css';
import router from './router';

createApp(App).use(router).mount('#app');