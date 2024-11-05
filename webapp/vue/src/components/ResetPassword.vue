<template>
  <div class="reset-password-container">
    <div class="reset-password-box">
      <h1>Redefinir senha</h1>
      <form @submit.prevent="resetPassword">
        <input type="password" v-model="password" placeholder="Digite sua nova senha" required />
        <input type="password" v-model="confirmPassword" placeholder="Repita sua nova senha" required />
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
        <button type="submit" class="btn btn-primary">Redefinir senha</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useRoute } from 'vue-router';

export default {
  data() {
    return {
      password: '',
      confirmPassword: '',
      errorMessage: '',
      successMessage: ''
    };
  },
  setup() {
    const route = useRoute();
    return { route };
  },
  methods: {
    async resetPassword() {
      console.log('resetPassword chamado com a senha:', this.password);
      if (this.password !== this.confirmPassword) {
        this.errorMessage = 'As senhas não correspondem.';
        console.error('Erro: As senhas não correspondem.');
        return;
      }
      this.errorMessage = '';
      this.successMessage = '';

      const token = this.route.query.token;
      if (!token) {
        this.errorMessage = 'Token não encontrado na URL.';
        console.error('Erro: Token não encontrado na URL.');
        return;
      }
      console.log('Token obtido da URL:', token);

      try {
        const response = await axios.post(`/v1/users/reset-password?token=${encodeURIComponent(token)}&password=${encodeURIComponent(this.password)}`);
        console.log('Resposta do servidor:', response.data);
        this.successMessage = 'Senha alterada com sucesso!';
      } catch (error) {
        console.error('Erro ao redefinir a senha:', error.response ? error.response.data : error.message);
        if (error.response && error.response.data && error.response.data.detail) {
          console.error('Detalhes do erro:', error.response.data.detail);
          this.errorMessage = 'Erro ao redefinir a senha: ' + error.response.data.detail.join(', ');
        } else {
          this.errorMessage = 'Erro ao redefinir a senha: ' + error.message;
        }
      }
    }
  }
};
</script>