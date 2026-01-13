<template>
    <div class="mx-5">
      <v-card class="elevation-1 mx-auto mt-10" max-width="600">
        <v-alert color="red" dismissible prominent type="error" v-if="errorVisible">
          Erro ao cadastrar usuário
        </v-alert>
        <v-alert color="green" dismissible prominent type="success" v-if="successVisible">
          Usuário cadastrado com sucesso!
        </v-alert>
  
        <v-toolbar dark color="primary">
          <v-toolbar-title>Cadastrar</v-toolbar-title>
        </v-toolbar>
        
        <v-card-text>
          <v-form>
            <v-text-field
              v-model="name"
              prepend-icon="mdi-account"
              label="Nome"
              required
            />
            <v-text-field
              v-model="email"
              prepend-icon="mdi-email"
              label="Email"
              type="email"
              required
            />
            <v-text-field
              v-model="phone"
              prepend-icon="mdi-phone"
              label="Telefone"
              required
            />
            <v-text-field
              v-model="cpf"
              prepend-icon="mdi-card-account-details"
              label="CPF"
              required
            />
            <v-text-field
              v-model="password"
              prepend-icon="mdi-lock"
              label="Senha"
              type="password"
              required
            />
          </v-form>
        </v-card-text>
        
        <v-card-actions class="justify-center">
          <v-btn color="grey" outlined @click="cancel">Cancelar</v-btn>
          <v-btn color="primary" @click="handleSignup">Cadastrar</v-btn>
        </v-card-actions>
        
        <v-overlay :value="overlay">
          <v-progress-circular indeterminate size="64"></v-progress-circular>
        </v-overlay>
      </v-card>
    </div>
  </template>
  
  <script>
import apiService from "@/services/ApiService";
import { defineComponent, ref } from "vue";
import { useRouter } from "vue-router";
  
  export default defineComponent({
    name: "FormSignup",
    setup() {
      const router = useRouter();
  
      const overlay = ref(false);
      const errorVisible = ref(false);
      const successVisible = ref(false);
  

      const name = ref("");
      const email = ref("");
      const phone = ref("");
      const cpf = ref("");
      const password = ref("");
  

      const handleSignup = async () => {
        overlay.value = true;
        try {

          await apiService.signup({
            name: name.value,
            email: email.value,
            phone: phone.value,
            cpf: cpf.value,
            password: password.value,
          });

          overlay.value = false;
          successVisible.value = true;
    
          setTimeout(() => {
            successVisible.value = false;
            router.push("/login");
          }, 3000);
        } catch (error) {
          overlay.value = false;
          errorVisible.value = true;

          console.error("Signup error:", error.response?.data || error.message);

          setTimeout(() => {
            errorVisible.value = false;
          }, 3000);
        }
      };
  
      const cancel = () => {
        router.push("/login");
      };
  
      return {
        name,
        email,
        phone,
        cpf,
        password,
        overlay,
        errorVisible,
        successVisible,
        handleSignup,
        cancel,
      };
    },
  });
  </script>
  