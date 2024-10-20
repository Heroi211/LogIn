<template>
    <nav class="navbar">
        <ul class="navbar-list">
            <li class="navbar-item"><router-link to="/">Home</router-link></li>
            <li class="navbar-item"><router-link to="/cadastrar-rotina">Cadastrar Rotina</router-link></li>
            <li class="navbar-item"><router-link to="/sobre">Sobre</router-link></li>
        </ul>
    </nav>
</template>

<script>
export default {
    name: 'Navbar'
}
</script>

