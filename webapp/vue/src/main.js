import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'devextreme/dist/css/dx.light.css';
import { createApp } from 'vue';
import App from './App.vue';
import './assets/styles.css';
// Vuetify
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import 'vuetify/styles';


import router from './router';

import Footer from './components/Global/Footer.vue';
import Navbar from './components/Global/Navbar.vue';

const app = createApp(App);
const vuetify = createVuetify({
    components,
    directives,
})

app.component('Footer', Footer);
app.component('Navbar', Navbar);

app.use(router).use(vuetify).mount('#app');