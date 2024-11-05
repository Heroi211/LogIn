<template>
  <div class="forgot-password-container">
    <div class="forgot-password-box">
      <h1>Olá,</h1>
      <h3>Informe seu e-mail</h3> 
      <h3>Redefinir sua senha</h3>
      <form @submit.prevent="submitEmail">
        <input type="email" v-model="email" placeholder="Digite seu e-mail" required />
        <div class="d-flex justify-content-end">
          <button type="submit" class="btn btn-primary ml-2">Enviar</button>
          <button type="button" @click="goToBack" class="btn btn-secondary ml-2">Voltar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: ''
    };
  },
  methods: {
    async submitEmail() {
      console.log('submitEmail chamado com o e-mail:', this.email);
      try {
        const response = await axios.post(`/v1/users/forgot-password?email=${encodeURIComponent(this.email)}`);
        console.log('Resposta do servidor:', response.data);
        alert('E-mail de redefinição de senha enviado!');
        this.$router.push('/login');
      } catch (error) {
        console.error('Erro ao enviar e-mail:', error.response ? error.response.data : error.message);
        if (error.response && error.response.data && error.response.data.detail) {
          console.error('Detalhes do erro:', error.response.data.detail);
          alert('Erro ao enviar e-mail: ' + error.response.data.detail.join(', '));
        } else {
          alert('Erro ao enviar e-mail: ' + error.message);
        }
      }
    },
    goToBack() {
      this.$router.push('/login');
    }
  }
};
</script>