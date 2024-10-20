<template>
  <div id="app">
    <Navbar v-if="$route.name !== 'Login'" />
    <div class="content">
      <router-view />
    </div>
    <Footer />
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>




