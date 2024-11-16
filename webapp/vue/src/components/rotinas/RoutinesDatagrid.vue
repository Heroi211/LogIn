<template>
  <v-data-table :loading="loading" :items.sync="routines" :headers="headers" hide-default-footer dense
    no-data-text="Nenhum resultado encontrado" loading-text="Carregando..."
    no-results-text="Nenhum resultado encontrado" class="elevation-1">
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>Rotinas</v-toolbar-title>
        <v-divider class="mx-4" inset vertical></v-divider>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-btn color="primary" dark class="mb-2" @click="dialog = true">
          Nova Rotina
        </v-btn>
      </v-toolbar>
      <RoutinesDialog v-if="dialog" @fechaModal="dialog = false" @atualiza="getRoutine"
        @success="notifyUser('Usuário editado', 'success', 'mdi-check')"
        @fail="notifyUser('Falha ao Editar', 'red', 'mdi-alert-circle')" />
    </template>
    <template v-slot:[`item.actions`]="{ item }">
      <v-tooltip top color="blue">
        <template v-slot:activator="{ on }">
          <v-icon medium class="mr-2" @click="editItem(item)" v-on="on">
            mdi-pencil
          </v-icon>
        </template>
        <span>Editar</span>
      </v-tooltip>
      <v-tooltip top color="red">
        <template v-slot:activator="{ on }">
          <v-icon medium class="mr-2" @click="deleteItem(item)" v-on="on">
            mdi-delete
          </v-icon>
        </template>
        <span>Deletar</span>
      </v-tooltip>
      <v-dialog v-model="dialogDelete" max-width="500px">
        <v-card>
          <v-card-title class="text-h5 justify-center">
            Tem certeza que deseja deletar?</v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue darken-1" text @click="closeDelete">Cancelar</v-btn>
            <v-btn color="blue darken-1" text @click="deleteItemConfirm">Confirmar</v-btn>
            <v-spacer></v-spacer>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>
  </v-data-table>
  <v-snackbar v-model="snackbar.visible" multi-line :color="snackbar.color" :timeout="snackbar.timeout"
    :top="snackbar.position === 'top'" min-width="0" elevation="0" rounded="pill">
    <v-layout align-center>
      <v-icon class="pr-3" dark>{{ snackbar.icon }}</v-icon>
      <div>{{ snackbar.text }}</div>
    </v-layout>
  </v-snackbar>
</template>
<script>
import { defineComponent, ref } from "vue";
import RoutinesDialog from "./RoutinesDialog.vue";
import apiService from "@/services/ApiService";

export default defineComponent({
  name: "RoutinesDatagrid",
  components: {
    RoutinesDialog
  },
  setup() {
    const headers = ref([
      { title: "titulo", key: "titulo" },
      { title: "descrição", key: "descricao" },
      { title: "status", key: 'status' },
      { title: "hora estimativa", key: "hr_estimativa" },
      { title: "hora real", key: "hr_real" },
      { title: "cliente", key: "client" },
      { title: "prioridade", key: "prioridade" },
      { title: "prazo", key: "dt_vencimento" },
      { title: 'Actions', key: 'actions', sortable: false },
    ])

    const snackbar = ref({
      color: "",
      icon: "",
      position: "top",
      text: "",
      timeout: 5000,
      visible: false,
    })

    const routines = ref([])
    const dialog = ref(false)
    const dialogEdit = ref(false)
    const dialogDelete = ref(false)
    const loading = ref(false)

    function editItem(item) {
      console.log(item)
      dialogEdit.value = true
    }

    function deleteItem(item) {
      console.log(item)
    }

    function closeDelete() {
      dialogDelete.value = false
    }
    function deleteItemConfirm(item) {
      console.log(item)
    }

    function notifyUser(text, color, icon) {
      snackbar.value.visible = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
      snackbar.value.icon = icon;
    }

    function getRoutine() {
      loading.value = true
      apiService.getRoutines().then((resp) => {
        routines.value = resp
      }).catch((err) => {
        routines.value = []
        console.error(err)
      }).finally(() => {
        loading.value = false
      })
    }

    getRoutine()
    return {
      routines,
      headers,
      dialog,
      dialogDelete,
      editItem,
      deleteItem,
      closeDelete,
      deleteItemConfirm,
      getRoutine,
      notifyUser,
      snackbar,
      loading
    }
  },
});
</script>
