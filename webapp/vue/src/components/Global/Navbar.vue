<template>
    <nav class="sidebar">
        <ul class="sidebar-list">
            <li class="sidebar-item"><router-link to="/">Home</router-link></li>
            <li class="sidebar-item"><router-link to="/cadastrar-rotina">Cadastrar Rotina</router-link></li>
            <li class="sidebar-item"><router-link to="/sobre">Sobre</router-link></li>
        </ul>
        <button class="navbar-button" @click="logoff">Logoff</button>
    </nav>
</template>

<script>
export default {
  name: 'Navbar',
  methods: {
    logoff() {
      // Limpar dados de autenticação (exemplo: remover token do localStorage)
      localStorage.removeItem('authToken');
      
      // Redirecionar para a página de login
      this.$router.push('/login');
    }
  }
}
</script>

