<template>
  <div class="mx-5">
    <v-card class="elevation-1 mx-auto mt-10" max-width="600">
      <v-alert color="red" dismissible prominent type="error" v-if="visivel">Usuario ou senha invalidos</v-alert>
      <v-toolbar dark color="primary">
        <v-toolbar-title>Faça Seu Login</v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <v-form>
          <v-text-field v-model="login" prepend-icon="mdi-account" name="login" label="Digite seu usuario"
            type="text" />
          <v-text-field v-model="password" id="password" prepend-icon="mdi-lock" name="password"
            label="Digite Sua Senha" type="password" />
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="grey" outlined>Cancelar</v-btn>
        <v-btn color="primary" @click="handleLogin">CONFIRMAR</v-btn>
      </v-card-actions>
      <div class="d-flex justify-center">
        <a @click="goToForgotPassword" class="forgot-password-link mr-0">Esqueceu a senha?</a>
      </div>
    </v-card>
    <v-overlay :value="overlay">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script>
import { defineComponent, ref } from "vue";
import apiService from "@/services/ApiService";
import { useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";

export default defineComponent({
  name: "FormLogin",
  setup() {
    const appStore = useAppStore()
    const router = useRouter()

    const dialog = ref(true)
    const overlay = ref(false)
    const login = ref("")
    const password = ref("")
    const visivel = ref(false)

    function handleLogin() {
      overlay.value = true;
      apiService
        .login(login.value, password.value)
        .then((response) => {
          localStorage.setItem("token", response.access_token);
          appStore.setAuthenticated(true);
          overlay.value = false;
          router.push("/home");
        })
        .catch(() => {
          overlay.value = false;
          visivel.value = true;
          setTimeout(() => {
            visivel.value = false;
          }, 3000);
        })
    }

    function goToForgotPassword() {
      router.push('/ForgotPassword');
    }

    return {
      dialog,
      overlay,
      login,
      password,
      visivel,
      handleLogin,
      goToForgotPassword
    }
  }
})
</script>
