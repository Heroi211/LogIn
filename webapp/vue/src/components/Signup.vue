<template>
    <div class="signup-container">
      <form @submit.prevent="signup" class="bg-light p-4 rounded shadow signup-form">
        <h2 class="text-center mb-4">Cadastro</h2>
        <div class="form-group mb-3">
          <label for="name" class="form-label">
            <i class="fas fa-user"></i> Name
          </label>
          <input type="text" id="name" v-model="name" class="form-control" required />
        </div>
        <div class="form-group mb-3">
          <label for="CPF" class="form-label">
            <i class="fas fa-id-card"></i> CPF
          </label>
          <input type="text" id="CPF" v-model="CPF" class="form-control" required />
        </div>
        <div class="form-group mb-3">
          <label for="email" class="form-label">
            <i class="fas fa-envelope"></i> Email
          </label>
          <input type="email" id="email" v-model="email" class="form-control" required />
        </div>
        <div class="form-group mb-3">
          <label for="phone" class="form-label">
            <i class="fas fa-phone"></i> Telefone
          </label>
          <input type="tel" id="phone" v-model="phone" class="form-control" required />
        </div>
        <div class="form-group mb-3">
          <label for="password" class="form-label">
            <i class="fas fa-lock"></i> Password
          </label>
          <input type="password" id="password" v-model="password" class="form-control" required />
        </div>
        <div class="d-flex justify-content-end">
          <button type="submit" class="btn btn-primary ml-2">Cadastrar</button>
          <button type="button" @click="goBack" class="btn btn-secondary ml-2">Voltar</button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        name: '',
        CPF: '',
        email: '',
        phone: '',
        password: '',
      };
    },
    methods: {
      async signup() {
        try {
          const response = await axios.post('http://localhost:8000/v1/users/signup', {
            name: this.name,
            CPF: this.CPF,
            email: this.email,
            phone: this.phone,
            password: this.password
          });
          console.log(response.data);
          alert('Cadastro bem-sucedido!');
            this.name = '';
            this.CPF = '';
            this.email = '';
            this.phone = '';
            this.password = '';
            goBack();
          // Redirecionar ou mostrar mensagem de sucesso
        } catch (error) {
          console.error(error);
          // Mostrar mensagem de erro
        }
      },
      goBack() {
        this.$router.push('/login');
      }
    }
  };
  </script>