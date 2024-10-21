<template>
      <div id="app">
        <Navbar v-if="!$route.meta.hideNavbar" />
        <main>
          <router-view />
        </main>
        <Footer/>
      </div>
</template>

<script>
export default {
  name: 'App'
};
</script>




