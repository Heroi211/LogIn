<template>
  <v-data-table :loading="loading" :items="users" :headers="headers" hide-default-footer dense
    loading-text="Carregando..." no-data-text="Nenhum resultado encontrado"
    no-results-text="Nenhum resultado encontrado" class="elevation-1">
    <template v-slot:top>
      <!-- <v-toolbar flat>
        <v-toolbar-title>Usuario</v-toolbar-title>
        <v-divider class="mx-4" inset vertical></v-divider>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-btn color="primary" dark class="mb-2" @click="dialog = true">
          Novo Usuario
        </v-btn>
      </v-toolbar> -->

    </template>
    <template v-slot:[`item.active`]="{ item }">
      <v-icon color="green" v-if="item.active">mdi-check</v-icon>
      <v-icon color="red"   v-else>mdi-close</v-icon>
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

  <UsersEditDialog
      v-if="dialogEdit"
      :user="selectUserEdit"
      @saved="onUpdated"
      @close="dialogEdit = false"
      @fail="notifyUser('Erro ao atualizar Usuario!', 'red', 'mdi-alert-circle')"
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
import { defineComponent } from 'vue';
import apiService from '@/services/ApiService';
import UsersEditDialog from './UserEditDialog.vue';

export default defineComponent({
  name: "UsuariosDatagrid",
  components: { UsersEditDialog },
  setup() {
    const loading = ref(false)
    const users = ref([])

    const dialogEdit = ref(false)
    const dialogDelete = ref(false)

    const selectUser = ref(null)
    const selectUserEdit = ref(null)


    const headers = ref([
      { title: "Nome", key: "name" },
      { title: "Email", key: "email" },
      { title: "CPF", key: "cpf" },
      { title: "Ativo", key: "active"},
      { title: "Telefone", key: "phone"},
      { title: "Tarefas", key: "tarefas"},
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

    function notifyUser(text, color, icon) {
      snackbar.value.visible = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
      snackbar.value.icon = icon;
    }

    function editItem(item) {
      selectUserEdit.value = item
      console.log("Editando usuario", item)
      dialogEdit.value = true
    }

      function onUpdated(){
      notifyUser("Usuario atualizado com sucesso!", "green", "mdi-check-circle");
      dialogEdit.value = false;
      getUsers();
    }

    function deleteItem(item) {
      selectUser.value = item
      dialogDelete.value = true
    }

    function closeDelete() {
      dialogDelete.value = false
    }
    function deleteItemConfirm(item) {
      if (!selectUser.value) return;
      loading.value = true
      apiService
        .deleteUser(selectUser.value.id)
        .then(() => {
          notifyUser("Usuario deletado com sucesso!", "green", "mdi-check-circle");
          dialogDelete.value = false;
          getUsers();
        })
        .catch((err) => {
          notifyUser("Erro ao deletar usuario!", "red", "mdi-alert-circle");
          console.error(err);
        })
        .finally(() => {
          loading.value = false
        });
    }
    function getUsers() {
      loading.value = true
      apiService.getUsers().then((resp) => {
        users.value = resp
      }).catch((err) => {
        users.value = []
        console.error(err)
      }).finally(() => {
        loading.value = false
      })
    }

    getUsers()

    return {
      loading,
      users,
      dialogEdit,
      dialogDelete,
      headers,
      snackbar,
      notifyUser,
      editItem,
      deleteItem,
      closeDelete,
      deleteItemConfirm,
      getUsers,
      onUpdated,
      selectUser,
      selectUserEdit

    }
  }
})
</script>
