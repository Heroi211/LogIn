<!-- src/components/login/FormLogin.vue -->
<template>
  <div class="mx-5">
    <v-card class="elevation-1 mx-auto mt-10" max-width="600">
      <v-alert color="red" dismissible prominent type="error" v-if="visivel">
        Usuário ou senha inválidos
      </v-alert>
      <v-toolbar dark color="primary">
        <v-toolbar-title>Faça Seu Login</v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <v-form>
          <v-text-field v-model="login" prepend-icon="mdi-account" name="login" label="Digite seu usuário" type="text" />
          <v-text-field v-model="password" id="password" prepend-icon="mdi-lock" name="password" label="Digite Sua Senha" type="password" />
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="grey" outlined @click="cancelLogin">Cancelar</v-btn>
        <v-btn color="primary" @click="handleLogin">CONFIRMAR</v-btn>
      </v-card-actions>
      <div class="d-flex justify-center">
        <a @click="goToForgotPassword" class="forgot-password-link mr-0" style="cursor: pointer;">Esqueceu a senha?</a>
      </div>
      <div class="d-flex right justify-center mr-0">
        <a @click="goToSignUp" class="signup-link mr-0" style="cursor: pointer;">Não tem uma conta?</a>
      </div>
    </v-card>
    <v-overlay :value="overlay">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>
  </div>
</template>

<script>
import apiService from "@/services/ApiService";
import { useAppStore } from "@/stores/app";
import { defineComponent, ref } from "vue";
import { useRouter } from "vue-router";
import { processQueue } from "@/services/ApiService";

export default defineComponent({
  name: "FormLogin",
  props: {
    inModal: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const appStore = useAppStore();
    const router = useRouter();

    const overlay = ref(false);
    const login = ref("");
    const password = ref("");
    const visivel = ref(false);

    async function handleLogin() {
      overlay.value = true;
      await apiService
        .login(login.value, password.value)
        .then(async (response) => {
          const token = response.access_token;  
          localStorage.setItem("token", token);

          appStore.setAuthenticated(true);
          const user = await apiService.getUserLogged();
          console.log("user", user);
          appStore.userLogged = user;
          overlay.value = false;
          if (props.inModal) {
            // Se estiver no modal, apenas fecha-o
            appStore.closeLoginModal();
          } else {
            // Se estiver na página de login, redireciona para /home
            router.push("/home");
          }
          processQueue(null, token);
        })
        .catch((err) => {
          overlay.value = false;
          visivel.value = true;
          processQueue(err, null);
          setTimeout(() => {
            visivel.value = false;
          }, 3000);
        });
    }

    function cancelLogin() {
      if (props.inModal) {
        // Se desejar permitir o cancelamento, pode fechar o modal
        appStore.closeLoginModal();
      } else {
        // Redirecionamento ou outra lógica se estiver na página de login
      }
    }

    function goToForgotPassword() {
      router.push('/ForgotPassword');
    }

    function goToSignUp() {
      router.push('/signup');
    }

    return {
      overlay,
      login,
      password,
      visivel,
      handleLogin,
      cancelLogin,
      goToForgotPassword,
      goToSignUp,
    };
  },
});
</script>
