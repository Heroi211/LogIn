<template>
  <v-card class="elevation-1 mx-auto mt-10" max-width="600">
    <v-card class="elevation-1 mx-auto mt-10" max-width="600">
      <v-alert color="red" dismissible prominent type="error" v-if="visivel">Senhas invalidas</v-alert>
      <v-alert color="green" dismissible prominent type="success" v-if="visivelSuccess">Link de reset de senha enviado
        para o seu email</v-alert>
      <v-toolbar dark color="primary">
        <v-toolbar-title>Reset de senha</v-toolbar-title>
      </v-toolbar>
      <v-card-text>
        <v-form>
          <v-text-field v-model="senha" prepend-icon="mdi-account" name="senha" label="Digite sua senha" type="password" />
          <v-text-field v-model="senha1" prepend-icon="mdi-account" name="senha" label="Confirme sua senha"
            type="password" />
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="grey" outlined>Cancelar</v-btn>
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
  name: "FormResetPassword",
  setup() {
    const router = useRouter()
    const visivel = ref(false)
    const overlay = ref(false)
    const senha = ref('')
    const senha1 = ref('')
    const visivelSuccess = ref(false)

    function handleReset() {
      overlay.value = true;
      if (senha.value !== senha1.value) {
        visivel.value = true
      }
      apiService.forgotPassword(senha.value, router.query.token).then(() => {
        router.push("/login")
      }).catch((err) => {
        console.error(err)
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
      senha,
      senha1,
      visivelSuccess,
      handleReset
    }

  }
})
</script>
