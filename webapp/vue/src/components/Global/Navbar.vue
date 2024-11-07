<template>
    <nav class="sidebar">
        <ul class="sidebar-list">
            <li class="sidebar-item"><router-link to="/home">Inicio</router-link></li>
            <li class="sidebar-item"><router-link to="/routines">Rotina</router-link></li>
            <li class="sidebar-item"><router-link to="/users">Usuário</router-link></li>
            <li class="sidebar-item"><router-link to="/clients">Cliente</router-link></li>
            <li class="sidebar-item">
        <router-link to="/login" @click.native="logoff">Sair</router-link>
      </li>
        </ul>
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

