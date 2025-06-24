<template>
  <v-data-table
    :loading="loading"
    :items="paginatedRoutines"
    :row-props="rowProps"
    :headers="computedHeaders"
    hide-default-footer
    dense
    no-data-text="Nenhum resultado encontrado"
    loading-text="Carregando..."
    no-results-text="Nenhum resultado encontrado"
    class="elevation-1"
  >
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>Rotinas</v-toolbar-title>
        <v-divider class="mx-4" inset vertical />
        <v-spacer />

        <template v-if="showActions">
          <v-btn color="primary" dark class="mb-2" @click="openConclude">
            Concluir Rotina
          </v-btn>
          <!-- <v-btn color="primary" dark class="mb-2" @click="dialog = true">
            Atribuir Rotina
          </v-btn> -->
          <v-btn color="primary" dark class="mb-2" @click="dialog = true">
            Nova Rotina
          </v-btn>
        </template>
      </v-toolbar>

      <RoutinesDialog
        v-if="showActions && dialog"
        @fechaModal="dialog = false"
        @atualiza="getRoutine"
        @success="notifyUser('Usuário editado', 'success', 'mdi-check')"
        @fail="notifyUser('Falha ao Editar', 'red', 'mdi-alert-circle')"
      />

      <RoutinesConcludeDialog
        v-if="showActions && concludeDialog"
        @close="concludeDialog = false"
        @completed="onConcluded"
      />

      <RoutinesEditDialog
        v-if="showActions && dialogEdit"
        :routine="selectedRoutineEdit"
        @fechamodal="dialogEdit = false"
        @atualiza="getRoutine"
        @success="notifyUser('Rotina editada com sucesso', 'success', 'mdi-check')"
        @fail="notifyUser('Falha ao editar rotina', 'red', 'mdi-alert-circle')"
      />

    </template>

    <template v-slot:[`item.actions`]="{ item }">
      <template v-if="showActions">
        <v-tooltip top color="blue">
          <template v-slot:activator="{ on, attrs }">
          <v-btn icon variant="text" v-bind="attrs" v-on="on" :disabled="item.status !== 'Executando'" @click="PauseItem(item)" >
            <v-icon>mdi-pause-circle</v-icon>
          </v-btn>
          </template>
          <span>Pause</span>
        </v-tooltip>
        <v-tooltip top color="blue">
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon variant="text" v-bind="attrs" v-on="on" :disabled="!['Aberta', 'Pausada'].includes(item.status)" @click="playItem(item)" >
              <v-icon > mdi-play-circle </v-icon>
            </v-btn>
          </template>
          <span>Play</span>
        </v-tooltip>

        <v-tooltip top color="blue">
          <template v-slot:activator="{ on }">
            <v-icon medium class="mr-2" @click="editItem(item)" v-on="on">
              mdi-pencil
            </v-icon>
          </template>
          <span>Editar</span>
        </v-tooltip>

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
              <v-spacer />
              <v-btn color="blue darken-1" text @click="closeDelete">
                Cancelar
              </v-btn>
              <v-btn color="blue darken-1" text @click="deleteItemConfirm">
                Confirmar
              </v-btn>
              <v-spacer />
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-dialog v-model="dialogPlay" max-width="600px">
          <v-card>
            <v-card-title class="text-h5 justify-center">
              Tem certeza que deseja iniciar a rotina selecionada?
            </v-card-title>
            <v-card-actions>
              <v-spacer />
              <v-btn color="blue darken-1" text @click="closePlay">
                Cancelar
              </v-btn>
              <v-btn color="blue darken-1" text @click="playItemConfirm">
                Confirmar
              </v-btn>
              <v-spacer />
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-dialog v-model="dialogPause" max-width="600px">
          <v-card>
            <v-card-title class="text-h5 justify-center">
              Informe o motivo da pausa:
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="pauseReason"
                label="Motivo ( Obrigatório )"
                :rules="[v => !!v || 'Motivo é obrigatório']"
                autocomplete="off"
                required
              />
            </v-card-text>
            <v-card-actions>
              <v-spacer />
              <v-btn text @click="closePause">Cancelar</v-btn>
              <v-btn text :disabled="!pauseReason" @click="pauseItemConfirm">Confirmar</v-btn>
              <v-spacer />
            </v-card-actions>
          </v-card>
        </v-dialog>

      </template>
    </template>
  </v-data-table>

  <v-row justify="center" class="mt-4" v-if="pageCount > 1">
    <v-pagination
      v-model="page"
      :length="pageCount"
      total-visible="5"
      color="primary"
    />
  </v-row>

  <v-snackbar
    v-model="snackbar.visible"
    multi-line
    :color="snackbar.color"
    :timeout="snackbar.timeout"
    :top="snackbar.position === 'top'"
    min-width="0"
    elevation="0"
    rounded="pill"
  >
    <v-layout align-center>
      <v-icon class="pr-3" dark>{{ snackbar.icon }}</v-icon>
      <div>{{ snackbar.text }}</div>
    </v-layout>
  </v-snackbar>
</template>

<script>
import { defineComponent, ref, computed, watch } from "vue";
import { format } from "date-fns";
import apiService from "@/services/ApiService";
import RoutinesDialog from "./RoutinesDialog.vue";
import RoutinesConcludeDialog from "./RoutinesConcludeDialog.vue";
import RoutinesEditDialog from "./RoutinesEditDialog.vue";

export default defineComponent({
  name: "RoutinesDatagrid",
  components: { RoutinesDialog, RoutinesConcludeDialog,RoutinesEditDialog },
  props: {
    showActions: { type: Boolean, default: true },
  },
  setup(props) {
    const headers = ref([
      { title: "id", key: "id"},
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
      return headers.value.filter((h) => h.key !== "actions");
    });

    const routines = ref([]);

    const dialog = ref(false);
    const dialogDelete = ref(false);
    const dialogPlay = ref(false);
    const dialogPause = ref(false);
    const dialogEdit = ref(false);
    const concludeDialog = ref(false);

    const loading = ref(false);
    const selectedRoutine = ref(null);
    const selectedRoutineEdit = ref(null);
    const pauseReason = ref("");

    const snackbar = ref({
      color: "",
      icon: "",
      position: "top",
      text: "",
      timeout: 5000,
      visible: false,
    });

    const page = ref(1);
    const itemsPerPage = 9;

    const pageCount = computed(() =>
      Math.ceil(routines.value.length / itemsPerPage)
    );

    const paginatedRoutines = computed(() => {
      const start = (page.value - 1) * itemsPerPage;
      return routines.value.slice(start, start + itemsPerPage);
    });

    watch(routines, () => {
      if (page.value > pageCount.value) {
        page.value = pageCount.value || 1;
      }
    });

    function getRoutine() {
      loading.value = true;
      apiService
        .getRoutines()
        .then((resp) => {
          routines.value = resp.map((routine) => {
            console.log("Routine:", routine);
            if (routine.dt_vencimento) {
              routine.dt_vencimento_raw = routine.dt_vencimento;
              routine.dt_vencimento = format(
                new Date(routine.dt_vencimento),
                "dd/MM/yyyy HH:mm"
              );
            }
            return routine;
          });
        })
        .catch(() => {
          routines.value = [];
        })
        .finally(() => {
          loading.value = false;
        });
    }

    function notifyUser(text, color, icon) {
      snackbar.value = { visible: true, text, color, icon, position: "top", timeout: 5000 };
    }

    function rowProps({ item }) {
      if (!item.dt_vencimento_raw) return {};
      const due = new Date(item.dt_vencimento_raw);
      const today = new Date();
      return {
        class: {
          "expired-row": due < today,
        },
      };
    }

    function editItem(item) {
      selectedRoutineEdit.value = {...item};
      dialogEdit.value = true;
    }

    function playItem(item) {
      selectedRoutine.value = item;
      dialogPlay.value = true;
    }

    function PauseItem(item) {
        selectedRoutine.value = item;
        pauseReason.value = ""; 
        dialogPause.value = true;
    }

    function deleteItem(item) {
      selectedRoutine.value = item;
      dialogDelete.value = true;
    }

    function closeDelete() {
      dialogDelete.value = false;
    }

    function closePlay() {
      dialogPlay.value = false;
    }

    function closePause() {
      dialogPause.value = false;
      pauseReason.value = ""; // Reset pause reason
      selectedRoutine.value = null;
    }

    function deleteItemConfirm() {
      if (!selectedRoutine.value) return;
      loading.value = true;
      apiService
        .deleteRoutine(selectedRoutine.value.id)
        .then(() => {
          notifyUser("Rotina deletada com sucesso", "success", "mdi-check");
          getRoutine();
        })
        .catch(() => {
          notifyUser("Falha ao deletar rotina", "red", "mdi-alert-circle");
        })
        .finally(() => {
          loading.value = false;
          closeDelete();
          selectedRoutine.value = null;
        });
    }

    function playItemConfirm() {
      if (!selectedRoutine.value) return;
      loading.value = true;
      apiService
        .playRoutine(selectedRoutine.value.id)
        .then(() => {
          notifyUser("Rotina iniciada com sucesso", "success", "mdi-check");
          getRoutine();
        })
        .catch(() => {
          notifyUser("Falha ao iniciar rotina", "red", "mdi-alert-circle");
        })
        .finally(() => {
          loading.value = false;
          dialogPlay.value = false;
          selectedRoutine.value = null;
        });
    }

    function pauseItemConfirm() {
      if (!selectedRoutine.value || !pauseReason.value) return;
      loading.value = true;
      console.log("Pausing routine:", selectedRoutine.value.id,{ reason: pauseReason.value });
      apiService
        .pauseRoutine(selectedRoutine.value.id, pauseReason.value )
        .then(() => {
          notifyUser("Rotina pausada com sucesso", "success", "mdi-check");
          getRoutine();
        })
        .catch(() => {
          notifyUser("Falha ao pausar rotina", "red", "mdi-alert-circle");
        })
        .finally(() => {
          loading.value = false;
          dialogPause.value = false;
          selectedRoutine.value = null;
        });
    }

    function openConclude() {
      concludeDialog.value = true;
    }

    function onConcluded() {
      notifyUser("Rotina concluída com sucesso", "success", "mdi-check");
      concludeDialog.value = false;
      getRoutine();
    }

    getRoutine();

    return {
      headers,
      computedHeaders,
      routines,
      dialog,
      dialogDelete,
      dialogPlay,
      dialogPause,
      dialogEdit,
      concludeDialog,
      loading,
      selectedRoutine,
      selectedRoutineEdit,
      snackbar,
      page,
      pageCount,
      paginatedRoutines,
      editItem,
      playItem,
      deleteItem,
      PauseItem,
      closeDelete,
      closePlay,
      closePause,
      deleteItemConfirm,
      playItemConfirm,
      pauseItemConfirm,
      getRoutine,
      notifyUser,
      rowProps,
      openConclude,
      onConcluded,
      showActions: props.showActions,
      pauseReason
    };
  },
});
</script>