<template>
  <v-dialog v-model="dialog" max-width="800px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Editar Rotina</span>
      </v-card-title>
      <v-form ref="formRef" lazy-validation>
        <v-card-text>
          <v-container>
            <v-row>
              <!-- TÍTULO -->
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="form.titulo"
                  label="Título"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- DESCRIÇÃO -->
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="form.descricao"
                  label="Descrição"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- PRAZO (INPUT DATE NATIVE) -->
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="form.dt_vencimento"
                  label="Prazo"
                  type="date"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- ESTIMATIVA (inteiro) -->
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model.number="form.hr_estimativa"
                  label="Estimativa"
                  type="number"
                  step="1"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- CLIENTE -->
              <v-col cols="12" sm="6" md="4">
                <v-select
                  v-model="form.clients_id"
                  :items="clients"
                  item-title="razao_social"
                  item-value="id"
                  label="Cliente"
                  :loading="loadingClients"
                  dense
                  outlined
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- USUÁRIO RESPONSÁVEL -->
              <v-col cols="12" sm="6" md="4">
                <v-select
                  v-model="form.users_id"
                  :items="users"
                  item-title="name"
                  item-value="id"
                  label="Responsável"
                  :loading="loadingUsers"
                  dense
                  outlined
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- PRIORIDADE -->
                <v-col cols="12" sm="6" md="4">
                <v-select
                  v-model.number="form.prioridade"
                  :items="priorities"
                  item-title="label"
                  item-value="value"
                  label="Prioridade"
                  dense
                  outlined
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <!-- STATUS -->
                <v-col cols="12" sm="6" md="4">
                <v-select
                  v-model="form.status"
                  :items="status"
                  item-title="label"
                  item-value="value"
                  label="Status"
                  dense
                  outlined
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-form>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="cancel">Cancelar</v-btn>
        <v-btn text :disabled="!canSave" @click="save">Salvar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { defineComponent, ref, watch, computed, onMounted } from 'vue';
import apiService from '@/services/ApiService';
import { useAppStore } from '@/stores/app';

export default defineComponent({
  name: 'RoutinesEditDialog',
  props: {
    routine: { type: Object, required: true }
  },
  emits: ['fechaModal','atualiza','success','fail'],
  setup(props, { emit }) {
    const dialog = ref(false);
    const formRef = ref(null);
    const form = ref({});
    const clients = ref([]);
    const loadingClients = ref(false);
    const users = ref([]);
    const loadingUsers = ref(false);
    const priorities = ref([
      { value: 1, label: 'Baixa' },
      { value: 2, label: 'Média' },
      { value: 3, label: 'Alta' }
    ]);
    const status = ref([
      { value: 1, label: 'Aberta' },
      { value: 2, label: 'Executando' },
      { value: 3, label: 'Concluída' },
      { value: 4, label: 'Cancelada' },
      { value: 5, label: 'Vencida' },
      { value: 6, label: 'Pausada' }
    ]);
    const appStore = useAppStore();
    const userLoggedId = appStore.userLogged.id;
    const requiredRule = v => !!v || 'Campo obrigatório';
        
    // popula form ao receber routine
    watch(() => props.routine, r => {
      if (r && r.id) {
        form.value = { ...r };
        // formata dt_vencimento para date input
        const raw = r.dt_vencimento_raw || r.dt_vencimento;
        form.value.dt_vencimento = raw
          ? raw.split('T')[0]
          : '';
        dialog.value = true;
        fetchClients();
        fetchUsers();
      }
    }, { immediate: true });

    onMounted(() => {
      fetchClients();
      fetchUsers();
    });

    async function fetchClients() {
      loadingClients.value = true;
      try {
        clients.value = await apiService.getAssignedClients(userLoggedId);
      } finally {
        loadingClients.value = false;
      }
    }

    async function fetchUsers() {
      loadingUsers.value = true;
      try {
        users.value = await apiService.getUsers();
      } finally {
        loadingUsers.value = false;
      }
    }

    const canSave = computed(() =>
      !!form.value.titulo &&
      !!form.value.descricao &&
      !!form.value.dt_vencimento &&
      Number.isInteger(form.value.hr_estimativa) &&
      !!form.value.clients_id &&
      !!form.value.users_id &&
      !!form.value.prioridade
    );

    async function save() {
      try {


      const payload = { 
        titulo:        form.value.titulo,
        descricao:     form.value.descricao,
        dt_vencimento: new Date(form.value.dt_vencimento).toISOString(),
        hr_estimativa: form.value.hr_estimativa,
        clients_id:    form.value.clients_id,
        users_id:      form.value.users_id,
        prioridade:    null,
        status:       null,
      }; 
        if (payload.dt_vencimento) payload.dt_vencimento = new Date(payload.dt_vencimento).toISOString();
        console.log('prioridade', payload.prioridade);
        console.log('payload', payload);
        console.log('props.routine.id', props.routine.id);
        const sel = priorities.value.find(
          p => p.label === form.value.prioridade || p.value === form.value.prioridade
                                          );
              payload.prioridade = sel
                ? sel.value
                : Number(form.value.prioridade);
        const selStat = status.value.find(
          s => s.label === form.value.status || s.value === form.value.status
                                          );
                  payload.status = selStat
                    ? selStat.value
                    : Number(form.value.status);
        console.log('prioridade', payload.prioridade);
        await apiService.updateRoutine(props.routine.id, payload);
        emit('success');
        emit('atualiza');
        emit('fechaModal');
        dialog.value = false;
      } catch {
        emit('fail');
      }
    }

    function cancel() {
      dialog.value = false;
      emit('fechaModal');
    }

    return {
      dialog,
      form,
      clients,
      loadingClients,
      users,
      loadingUsers,
      priorities,
      status,
      formRef,
      requiredRule,
      canSave,
      save,
      cancel
    };
  }
});
</script>
