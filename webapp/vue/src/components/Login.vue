<template>
  <div class="login-container">
    <form @submit.prevent="login" class="bg-light p-4 rounded shadow login-form">
      <div class="user-photo mb-3 mx-auto">
        <img :src="userPhoto" alt="User Photo" class="user-photo-img" />
      </div>
      <h2 class="text-center mb-4">Login</h2>
      <div class="form-group mb-3">
        <label for="username" class="form-label">
          <i class="fas fa-user"></i> CPF
        </label>
        <input type="text" id="username" v-model="username" class="form-control" required />
      </div>
      <div class="form-group mb-3">
        <label for="password" class="form-label">
          <i class="fas fa-lock"></i> Password
        </label>
        <input type="password" id="password" v-model="password" class="form-control" required />
      </div>
      <div class="d-flex justify-content-end mb-3">
        <button type="submit" class="btn btn-primary ml-2">Login</button>
        <button type="button" @click="goToSignup" class="btn btn-secondary ml-2">Signup</button>
      </div>
      <div class="d-flex justify-content-between">
        <a href="/forgotPassword" class="forgot-password-link">Forgot Password?</a>
      </div>
    </form>
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
      userPhoto: userPhoto // Mantendo a importação correta da imagem
    };
  },
  methods: {
    async login() {
      const formData = new URLSearchParams();
      formData.append('username', this.username);
      formData.append('password', this.password);
      
      try {
        const response = await axios.post('http://localhost:8000/v1/users/login', formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        const token = response.data.access_token;
        localStorage.setItem('token', token);
        alert('Login bem-sucedido!');
        this.$router.push('/home');
      } catch (error) {
        alert('Erro no login: ');
        console.log(error);
      }
    },
    goToSignup() {
      this.$router.push('/signup');
    }
  }
};
</script>

<style scoped>
/* Adicione seus estilos aqui */
</style>