<template>
  <v-data-table :loading="loading" :items.sync="routines" :headers="computedHeaders" hide-default-footer dense
    no-data-text="Nenhum resultado encontrado" loading-text="Carregando..."
    no-results-text="Nenhum resultado encontrado" class="elevation-1">
    
    <!-- Top Toolbar -->
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>Rotinas</v-toolbar-title>
        <v-divider class="mx-4" inset vertical></v-divider>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <!-- Exibe os botões apenas se showActions for true -->
        <template v-if="showActions">
          <v-btn color="primary" dark class="mb-2" @click="dialog = true">
            Concluir Rotina
          </v-btn>
          <v-btn color="primary" dark class="mb-2" @click="dialog = true">
            Atribuir Rotina
          </v-btn>
          <v-btn color="primary" dark class="mb-2" @click="dialog = true">
            Nova Rotina
          </v-btn>
        </template>
      </v-toolbar>
      <!-- Exibe o diálogo apenas se showActions for true -->
      <RoutinesDialog v-if="showActions && dialog" 
        @fechaModal="dialog = false" 
        @atualiza="getRoutine"
        @success="notifyUser('Usuário editado', 'success', 'mdi-check')"
        @fail="notifyUser('Falha ao Editar', 'red', 'mdi-alert-circle')" />
    </template>
    
    <!-- Coluna de ações: Exibe apenas se showActions for true -->
    <template v-slot:[`item.actions`]="{ item }">
      <template v-if="showActions">
        <v-tooltip top color="blue">
          <template v-slot:activator="{ on }">
            <v-icon medium class="mr-2" @click="editItem(item)" v-on="on">
              mdi-pencil
            </v-icon>
          </template>
          <span>Editar</span>
        </v-tooltip>
        <!-- <v-tooltip top color="red">
          <template v-slot:activator="{ on, attrs }">
            <v-span v-blind="attrs" v-on="on" class="mr-2">
              <v-icon medium @click="deleteItem(item)">
                mdi-delete
              </v-icon>
            </v-span>
          </template>
          <span>Deletar</span>
        </v-tooltip> -->
        <v-tooltip top color="red">
          <template v-slot:activator="{ on, attrs }">
            <span v-bind="attrs" v-on="on" class="mr-2">
              <v-icon medium @click="deleteItem(item)">
                mdi-delete
              </v-icon>
            </span>
          </template>
          <span>Deletar</span>
        </v-tooltip>
        <v-dialog v-model="dialogDelete" max-width="500px">
          <v-card>
            <v-card-title class="text-h5 justify-center">
              Tem certeza que deseja deletar?
            </v-card-title>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="closeDelete">Cancelar</v-btn>
              <v-btn color="blue darken-1" text @click="deleteItemConfirm">Confirmar</v-btn>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </template>
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
import apiService from "@/services/ApiService";
import { defineComponent, ref, computed, watch } from "vue";
import RoutinesDialog from "./RoutinesDialog.vue";
import { format } from "date-fns";

export default defineComponent({
  name: "RoutinesDatagrid",
  components: { RoutinesDialog },
  props: {
 
    showActions: {
      type: Boolean,
      default: true,
    }
  },
  setup(props) {

    const headers = ref([
      { title: "titulo", key: "titulo" },
      { title: "descrição", key: "descricao" },
      { title: "status", key: "status" },
      { title: "hora estimativa", key: "hr_estimativa" },
      { title: "hora real", key: "hr_real" },
      { title: "cliente", key: "client" },
      { title: "prioridade", key: "prioridade" },
      { title: "prazo", key: "dt_vencimento" },
      { title: "Actions", key: "actions", sortable: false },
    ]);
    
    
    const computedHeaders = computed(() => {
      if (props.showActions) {
        return headers.value;
      }
      return headers.value.filter(header => header.key !== "actions");
    });
    
   
    const routines = ref([]);
    const dialog = ref(false);
    const dialogEdit = ref(false);
    const dialogDelete = ref(false);
    const loading = ref(false);
    const selectedRoutine = ref(null);
    const selectedRoutineEdit = ref(null);
    
    const snackbar = ref({
      color: "",
      icon: "",
      position: "top",
      text: "",
      timeout: 5000,
      visible: false,
    });

    function editItem(item) {
      selectedRoutineEdit.value = item;
      dialogEdit.value = true;
    }
    
    function deleteItem(item) {
      selectedRoutine.value = item;
      dialogDelete.value = true;
  
    }
    
    function closeDelete() {
      dialogDelete.value = false;
    }
    
    function deleteItemConfirm() {
      if (!selectedRoutine.value) return;
      loading.value = true;
      apiService.deleteRoutine(selectedRoutine.value.id)
        .then(() => {
          notifyUser("Rotina deletada com sucesso", "success", "mdi-check");
          getRoutine();
        })
        .catch((err) => {
          notifyUser("Falha ao deletar rotina", "red", "mdi-alert-circle");
          console.error(err);
        })
        .finally(() => {
          loading.value = false;
          closeDelete();
          selectedRoutine.value = null;
        });
    }

    
    function notifyUser(text, color, icon) {
      snackbar.value.visible = true;
      snackbar.value.text = text;
      snackbar.value.color = color;
      snackbar.value.icon = icon;
    }
    
    watch(dialog, async (newValue) => {
      getRoutine();
    });
    
    function getRoutine() {
      loading.value = true;
      apiService.getRoutines()
      .then((resp) => {
        routines.value = resp.map((routine) => {
          if (routine.dt_vencimento) {
            routine.dt_vencimento = format(new Date(routine.dt_vencimento), "dd/MM/yyyy HH:mm");
          }
          return routine;
        });
      })
      .catch((err) => {
        routines.value = [];
        console.error(err);
      })
      .finally(() => {
        loading.value = false;
      });
    }
    
    getRoutine();
    
    return {
      routines,
      computedHeaders,
      dialog,
      dialogDelete,
      editItem,
      deleteItem,
      closeDelete,
      deleteItemConfirm,
      getRoutine,
      notifyUser,
      snackbar,
      loading,
      showActions: props.showActions 
    };
  },
});
</script>
