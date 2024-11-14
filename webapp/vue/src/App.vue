<template>
  <div id="app">
    <Navbar v-if="!$route.meta.hideNavbar" />
    <main style="padding: 0; height: 100%;">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>
