// Utilities
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => {
    return {
      authenticated: false,
    }
  },
  actions: {
    setAuthenticated(state) {
      this.authenticated = state;
    },
  }
})
