<template>
  <div>
    <v-data-table :items="routines">
      <template v-slot:top>
        <div style="display: inline-block;">
          <v-btn @click="toggleSelect()">Select</v-btn>
          <v-btn @click="addRoutine()">+</v-btn>
          <v-btn @click="removeSelected()">-</v-btn>
        </div>
      </template>
    </v-data-table>
  </div>
</template>
<script>
export default {
  name: "RoutinesView",
  data() {
    return {
      showSelect: false,
      routines: [
        { name: "Routine 1", description: "Description 1" },
        { name: "Routine 2", description: "Description 2" },
      ],
      headers: [
        { title: "name", key: "name", align: "end" },
        { title: "description", key: "description", align: "end" },
      ],
      selected: [],
    };
  },
  components: {},
  methods: {
    toggleSelect() {
      this.showSelect = !this.showSelect;
    },
    addRoutine() {
      const newRoutine = {
        name: `Routine ${this.routines.length + 1}`,
        description: `Description ${this.routines.length + 1}`,
      };
      this.routines.push(newRoutine);
    },
    removeSelected() {
      const dataGrid = this.$refs.dataGrid.instance;
      const selectedKeys = dataGrid.getSelectedRowKeys();
      this.routines = this.routines.filter(
        (routine) => !selectedKeys.includes(routine)
      );
      dataGrid.clearSelection();
    },
  },
};
</script>