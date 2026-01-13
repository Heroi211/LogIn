
<template>
  <nav class="navbar bg-custom navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">
        <img
          src="/src/assets/logo.png"
          alt="Logo"
          width="50"
          height="50"
          class="d-inline-block align-text-top"
        />
      </a>
     
      <div v-show="showMenu">
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <li class="nav-item">
              <router-link class="nav-link text-white" to="/">Início</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link text-white" to="/routines">Rotinas</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link text-white" to="/clients">Clientes</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link text-white" to="/users">Usuários</router-link>
            </li>
          </ul>
          <router-link to="/login" @click.native="logout">Sair</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed, defineComponent } from "vue";
import { useAppStore } from "@/stores/app";
import { useRouter, useRoute } from "vue-router";

export default defineComponent({
  name: "Navbar",
  setup() {
    const appStore = useAppStore();
    const router   = useRouter();
    const route    = useRoute();

    
    const showMenu = computed(
      () => appStore.authenticated && route.name !== "login"
    );

    function logout() {
      localStorage.removeItem("token");
      appStore.setAuthenticated(false);
      router.push("/login");
    }

    return {
      showMenu,
      logout,
    };
  },
});
</script>
