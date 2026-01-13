<template>
  <v-card class="elevation-1 mx-auto mt-10" max-width="600">
    <v-card class="elevation-1 mx-auto mt-10" max-width="600">
      <v-alert color="red" dismissible prominent type="error" v-if="visivel">Email invalidos</v-alert>
      <v-alert color="green" dismissible prominent type="success" v-if="visivelSuccess">Link de reset de senha enviado
        para o seu email</v-alert>
      <v-toolbar dark color="primary">
        <v-toolbar-title>Reset de senha</v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <v-form>
          <v-text-field v-model="email" prepend-icon="mdi-account" name="login" label="Digite seu email" type="text" />
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="grey" outlined @click="cancelar">Cancelar</v-btn>
        <v-btn color="primary" @click="handleReset">CONFIRMAR</v-btn>
      </v-card-actions>
    </v-card>
    <v-overlay :value="overlay">
      <v-progress-circular indeterminate size="64"></v-progress-circular>
    </v-overlay>
  </v-card>
</template>

<script>
import apiService from "@/services/ApiService";
import { defineComponent, ref } from "vue";
import { useRouter } from "vue-router";
export default defineComponent({
  name: "FormForgotPassword",
  setup() {
    const visivel = ref(false)
    const overlay = ref(false)
    const email = ref('')
    const visivelSuccess = ref(false)
    const router = useRouter()

    function cancelar() {
      router.push('/login')
    }

    function handleReset() {
      overlay.value = true;
      apiService.forgotPassword(email.value).then((resp) => {
        visivelSuccess.value = true
        setTimeout(() => {
          visivelSuccess.value = false;
        }, 3000);
      }).catch((err) => {
        visivel.value = true
        setTimeout(() => {
          visivel.value = false;
        }, 3000);
      }).finally(() => {
        overlay.value = false
      })
    }

    return {
      visivel,
      overlay,
      email,
      visivelSuccess,
      handleReset,
      cancelar
    }

  }
})
</script>
