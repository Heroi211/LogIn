<template>
  <RoutinesDatagrid />
</template>
<script>
import RoutinesDatagrid from "@/components/rotinas/RoutinesDatagrid.vue";
import { defineComponent } from "vue";

export default defineComponent({
  name: "Routines",
  components: {
    RoutinesDatagrid
  },
});
</script>
