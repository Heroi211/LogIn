<template>
  <div class="full-page">
    <div class="login-container">
    <form @submit.prevent="login" class="bg-light p-4 rounded shadow login-form">
      <div class="user-photo mb-3 mx-auto">
        <img :src="userPhoto" alt="User Photo" class="user-photo-img" />
      </div>
      <h2 class="text-center mb-4">Login</h2>
      <div class="form-group mb-3">
        <label for="username" class="form-label">
          <i class="fas fa-user"></i> Username
        </label>
        <input type="text" id="username" v-model="username" class="form-control" required />
      </div>
      <div class="form-group mb-3">
        <label for="password" class="form-label">
          <i class="fas fa-lock"></i> Password
        </label>
        <input type="password" id="password" v-model="password" class="form-control" required />
      </div>
      <div class="d-flex justify-content-between">
        <button type="submit" class="btn btn-primary">Login</button>
        <button type="button" @click="signup" class="btn btn-secondary">Signup</button>
      </div>
    </form>
  </div>
  </div>
</template>

<script>
import userPhoto from '@/assets/Favicons/Android.png';
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      userPhoto: userPhoto
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:8000/v1/users/login', {
          username: this.username,
          password: this.password
        });
        const token = response.data.access_token;
        localStorage.setItem('token', token);
        alert('Login bem-sucedido!');
        // Redirecionar para outra página, se necessário
      } catch (error) {
        alert('Erro no login: ' + error.response.data.detail);
      }
    },
    async signup() {
      try {
        const response = await axios.post('http://localhost:8000/v1/users/signup', {
          username: this.username,
          password: this.password
        });
        alert('Cadastro bem-sucedido!');
        // Redirecionar para a página de login ou outra página, se necessário
      } catch (error) {
        alert('Erro no cadastro: ' + error.response.data.detail);
      }
    }
  }
};
</script>