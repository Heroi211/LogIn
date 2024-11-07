<template>
  <div id="app">
    <Navbar v-if="!$route.meta.hideNavbar" />
    <main style="padding: 0;">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script>
import Footer from "@/components/Global/Footer.vue";
export default {
  name: 'App'
};
</script>
