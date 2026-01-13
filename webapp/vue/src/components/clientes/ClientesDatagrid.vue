<template>
  <v-data-table :loading="loading" :items="clients" :headers="headers" hide-default-footer dense
    loading-text="Carregando..." no-data-text="Nenhum resultado encontrado"
    no-results-text="Nenhum resultado encontrado" class="elevation-1">
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>Cliente</v-toolbar-title>
        <v-divider class="mx-4" inset vertical></v-divider>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-btn color="primary" dark class="mb-2" @click="openDialog">
          Novo Cliente
        </v-btn>
      </v-toolbar>

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
      
          <ClientsDialog
        v-if="dialogNew"
        @close="dialogNew = false"
        @saved="onSaved"
        @fail="onFail"
      />

          <ClientsEditDialog
      v-if="dialogEdit"
      :client="selectedClientEdit"
      @saved="onUpdated"
      @close="dialogEdit = false"
      @fail="notifyUser('Erro ao atualizar cliente!', 'red', 'mdi-alert-circle')"
    />

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
import apiService from "@/services/ApiService";
import ClientsDialog from '@/components/clientes/ClientesDialog.vue';
import ClientsEditDialog from '@/components/clientes/ClientesEditDialog.vue';

import { se } from "date-fns/locale";


export default defineComponent({
  name: "ClientesDatagrid",
  components: { ClientsDialog, ClientsEditDialog },
  setup() {
    const clients = ref([]);
    const loading = ref(false);

    // Dialogs
    const dialogNew = ref(false);
    const dialogEdit = ref(false);
    const dialogDelete = ref(false);
    
    
    const selectedClient = ref(null);
    const selectedClientEdit = ref(null);


    const headers = ref([
      { title: "CNPJ", key: "cnpj" },
      { title: "Razão Social", key: "razao_social" },
      { title: "Tarefas", key: "tarefas" },
      { title: "Actions", key: "actions" },
    ])
    const snackbar = ref({
      color: "",
      icon: "",
      position: "top",
      text: "",
      timeout: 5000,
      visible: false,
    })

    function openDialog() {
      dialogNew.value = true
    }
    
    function onUpdated(){
      notifyUser("Cliente atualizado com sucesso!", "green", "mdi-check-circle");
      dialogEdit.value = false;
      getClients();
    }

    function onSaved(){
      notifyUser("Cliente salvo com sucesso!", "green", "mdi-check-circle");
      dialogNew.value = false;
      getClients();
    }

    function onFail() {
      notifyUser("Erro ao salvar cliente!", "red", "mdi-alert-circle");
    }

    function notifyUser(text, color, icon) {
      snackbar.value.visible = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
      snackbar.value.icon = icon;
    }

    function editItem(item) {

      selectedClientEdit.value = {...item};
      console.log(selectedClientEdit.value)
      dialogEdit.value = true
    }

    function deleteItem(item) {
      selectedClient.value = item;
      dialogDelete.value = true;
    }

    function closeDelete() {
      dialogDelete.value = false
    }
    function deleteItemConfirm(item) {
      if (!selectedClient.value.id) return;
      loading.value = true;
      apiService
        .deleteClient(selectedClient.value.id)
        .then(() => {
          notifyUser("Cliente deletado com sucesso!", "green", "mdi-check-circle");
          getClients();
        })
        .catch((err) => {
          notifyUser("Erro ao deletar cliente!", "red", "mdi-alert-circle");
          console.error(err);
        })
        .finally(() => {
          dialogDelete.value = false;
          loading.value = false;
        });  
    }

    function getClients() {
      loading.value = true
      apiService.getClients().then((resp) => {
        clients.value = resp
      }).catch((err) => {
        clients.value = []
        console.error(err)
      }).finally(() => {
        loading.value = false
      })
    }

    getClients()

    return {
      headers,
      clients,
      dialogNew,
      dialogEdit,
      dialogDelete,
      notifyUser,
      editItem,
      deleteItem,
      closeDelete,
      deleteItemConfirm,
      snackbar,
      getClients,
      openDialog,
      onSaved,
      onFail,
      loading,
      selectedClient,
      selectedClientEdit,
      onUpdated

    }
  }
})
</script>
