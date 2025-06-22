<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Concluir Rotina</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="form">
          <v-select
            v-model="selectedId"
            :items="routines"
            item-title="titulo"
            item-value="id"
            label="Selecione a rotina"
            :loading="loading"
            return-object="false"
            dense
            outlined
            required
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="close">Cancelar</v-btn>
        <v-btn
          :disabled="!selectedId"
          color="primary"
          text
          @click="conclude"
        >
          Concluir
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { defineComponent, ref, onMounted } from "vue";
import apiService from "@/services/ApiService";

export default defineComponent({
  name: "RoutinesConcludeDialog",
  emits: ["close", "completed"],
  setup(_, { emit }) {
    const dialog = ref(true);
    const routines = ref([]);
    const selectedId = ref(null);
    const loading = ref(false);

    async function fetchAssigned() {
      loading.value = true;
      try {
        console.log("Carregando rotinas atribuídas...");
        routines.value = await apiService.getAssignedRoutines();
      } catch (e) {
        console.error("Erro ao carregar rotinas atribuídas:", e);
        console.error("Erro ao carregar rotinas:", e);
      } finally {
        loading.value = false;
      }
    }

    function close() {
      emit("close");
    }

    async function conclude() {
      if (!selectedId.value) return;
      loading.value = true;
      try {
        console.log("Concluindo rotina com ID:", selectedId.value.id);
        await apiService.completeRoutine(selectedId.value.id);
        emit("completed");
      } catch (e) {
        console.error("Falha ao concluir rotina:", e);
      } finally {
        loading.value = false;
      }
    }

    onMounted(fetchAssigned);

    return {
      dialog,
      routines,
      selectedId,
      loading,
      close,
      conclude,
    };
  },
});
</script>
