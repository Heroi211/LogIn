
<template>
    <v-dialog v-model="modalVisible" persistent max-width="600px">
      <FormLogin :inModal="true" />
    </v-dialog>
  </template>
  
  <script>
  import { ref, watch } from "vue";
  import { useAppStore } from "@/stores/app";
  import FormLogin from "./FormLogin.vue"; 
  
  export default {
    name: "LoginModal",
    components: { FormLogin },
    setup() {
      const appStore = useAppStore();
      const modalVisible = ref(false);
  
      watch(() => appStore.showLoginModal, (newVal) => {
        modalVisible.value = newVal;
      });
  
      return {
        modalVisible,
      };
    },
  };
  </script>
  