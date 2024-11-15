<template>
  <v-data-table :items="routines">
    <template v-slot:top>
      <div style="display: inline-block;">
        <v-btn @click="toggleSelect()">Select</v-btn>
        <v-btn @click="addRoutine()">+</v-btn>
        <v-btn @click="removeSelected()">-</v-btn>
      </div>
    </template>
  </v-data-table>
</template>
<script>
import { defineComponent, ref } from "vue";

export default defineComponent({
  name: "RoutinesDatagrid",
  components: {},
  setup() {
    const routines = ref([
      { name: "Routine 1", description: "Description 1" },
      { name: "Routine 2", description: "Description 2" },
    ])

    const headers = ref([
      { title: "name", key: "name", align: "end" },
      { title: "description", key: "description", align: "end" },
    ])

    const showSelect = ref(false)
    const selected = ref([])

    function toggleSelect() {
      showSelect = !showSelect;
    }

    function addRoutine() {
      const newRoutine = {
        name: `Routine ${routines.value.length + 1}`,
        description: `Description ${routines.value.length + 1}`,
      };
      routines.value.push(newRoutine)
    }

    function removeSelected() {
      routines.value.pop();
    }

    return {
      routines,
      headers,
      selected,
      toggleSelect,
      addRoutine,
      removeSelected
    }
  }
});
</script>
