<template>
    <nav class="sidebar">
        <ul class="sidebar-list">
            <li class="sidebar-item"><router-link to="/">Inicio</router-link></li>
            <li class="sidebar-item"><router-link to="/cadastrar-rotina">Cadastrar Rotina</router-link></li>
            <li class="sidebar-item"><router-link to="/sobre">Sobre</router-link></li>
            <li class="sidebar-item">
        <router-link to="/login" @click.native="logoff">Sair</router-link>
      </li>
        </ul>
        <button class="navbar-button" @click="logoff">Sair</button>
    </nav>
</template>

<script>
export default {
  name: 'Navbar',
  methods: {
    logoff() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
}
</script>

