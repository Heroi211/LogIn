// src/stores/app.js
import { defineStore } from 'pinia';

export const useAppStore = defineStore('app', {
  state: () => ({
    authenticated: false,
    showLoginModal: false, // novo estado para controlar a exibição do modal
  }),
  actions: {
    setAuthenticated(state) {
      this.authenticated = state;
    },
    triggerLoginModal() {
      this.showLoginModal = true;
    },
    closeLoginModal() {
      this.showLoginModal = false;
    },
  },
});
