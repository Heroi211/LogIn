import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { createApp } from 'vue';
import App from './App.vue';
import './assets/styles.css';
import router from './router';

import Footer from './components/Global/Footer.vue';
import Navbar from './components/Global/Navbar.vue';

const app = createApp(App);

app.component('Footer', Footer);
app.component('Navbar', Navbar);

app.use(router).mount('#app');