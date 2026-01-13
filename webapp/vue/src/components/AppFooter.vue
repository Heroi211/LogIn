<template>
  <v-footer fixed padless color="primary darken-2" style="padding: 0%;">
    <v-row no-gutters>
      <v-col class="text-center white--text px-4"> {{ currentYear }} Cod3bit. All rights reserved. </v-col>
    </v-row>
  </v-footer>
</template>

<script>
export default {
  name: 'AppFooter',
  data() {
    return {
      currentYear: new Date().getFullYear()
    };
  }
};
</script>
