<template>
    <div>
      <dx-button text="Select" @click="toggleSelect"></dx-button>
      <dx-button text="+" @click="addRoutine"></dx-button>
      <dx-button text="-" @click="removeSelected"></dx-button>
  
      <dx-data-grid
        :dataSource="routines"
        :showBorders="true"
        v-if="showSelect"
        ref="dataGrid"
      >
        <dxo-selection mode="multiple"></dxo-selection>
        <dxo-editing mode="row" allowUpdating="true" allowDeleting="true" allowAdding="true"></dxo-editing>
        <dxi-column dataField="name" caption="Name"></dxi-column>
        <dxi-column dataField="description" caption="Description"></dxi-column>
      </dx-data-grid>
    </div>
  </template>
  
  <script>
  import DxButton from 'devextreme-vue/button';
import { DxColumn, DxDataGrid, DxEditing, DxSelection } from 'devextreme-vue/data-grid';
  
  export default {
    name: 'RoutinesView',
    components: {
      DxDataGrid,
      DxColumn,
      DxSelection,
      DxEditing,
      DxButton,
    },
    data() {
      return {
        showSelect: false,
        routines: [
          { name: 'Routine 1', description: 'Description 1' },
          { name: 'Routine 2', description: 'Description 2' },
        ],
        selected: [],
      };
    },
    methods: {
      toggleSelect() {
        this.showSelect = !this.showSelect;
      },
      addRoutine() {
        const newRoutine = { name: `Routine ${this.routines.length + 1}`, description: `Description ${this.routines.length + 1}` };
        this.routines.push(newRoutine);
      },
      removeSelected() {
        const dataGrid = this.$refs.dataGrid.instance;
        const selectedKeys = dataGrid.getSelectedRowKeys();
        this.routines = this.routines.filter(routine => !selectedKeys.includes(routine));
        dataGrid.clearSelection();
      },
    },
  };
  </script>
