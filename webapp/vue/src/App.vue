<template>
  <v-app>
    <v-app-bar app color="#074293" dark extension-height="64">
      <AppNav />
    </v-app-bar>
    <v-main style="margin-top: 1%;">
      <router-view />
    </v-main>
    <AppFooter />
  </v-app>
</template>

<script setup>
import AppFooter from "@/components/AppFooter.vue";
import AppNav from '@/components/AppNav.vue';
</script>
