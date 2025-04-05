<template>
  <v-dialog v-model="dialog" max-width="800px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Nova Rotina</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                v-model="editUser.titulo"
                label="Titulo"
                aria-required="true"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                v-model="editUser.descricao"
                label="Descrição"
                aria-required="true"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                v-model="prazoDias"
                label="Prazo (dias)"
                type="number"
                prepend-icon="mdi-calendar"
                @change="calcularPrazo"
              />
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                v-model="editUser.hr_estimativa"
                label="Estimativa"
                aria-required="true"
              />
            </v-col>
          </v-row>
          <v-row v-if="editUser.dt_vencimento">
            <v-col cols="12">
              <div>
                Data Calculada: {{ formatDate(editUser.dt_vencimento) }}
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="$emit('fechaModal')">
          Cancelar
        </v-btn>
        <v-btn color="blue darken-1" text @click="salvarRotina">
          Salvar
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import apiService from '@/services/ApiService';
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: "RoutinesDialog",
  emits: ['fechaModal', 'atualiza', 'success', 'fail'],
  setup(props, { emit }) {
    const dialog = ref(true);
    const editUser = ref({});
    const prazoDias = ref('');

    function calcularPrazo() {
      const dias = parseInt(prazoDias.value);
      if (isNaN(dias)) {
        editUser.value.dt_vencimento = "";
        return;
      }
      const hoje = new Date();
      const dataFinal = new Date(hoje);
      dataFinal.setDate(hoje.getDate() + dias);
      editUser.value.dt_vencimento = dataFinal.toISOString();
    }

    async function salvarRotina() {
      try {
        const novaRotina = await apiService.salvarRotina(editUser.value);
        console.log("Rotina salva:", novaRotina);
        emit('success', 'Rotina criada com sucesso!', 'success', 'mdi-check');
        emit('atualiza');
        emit('fechaModal');
      } catch (error) {
        console.error("Erro ao salvar a rotina:", error.response?.data || error.message);
        emit('fail', 'Erro ao salvar a rotina', 'red', 'mdi-alert-circle');
      }
    }

    function formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleDateString("pt-BR");
    }

    return {
      dialog,
      editUser,
      prazoDias,
      calcularPrazo,
      salvarRotina,
      formatDate,
    };
  },
});
</script>
