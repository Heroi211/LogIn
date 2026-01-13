<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Editar Cliente</span>
      </v-card-title>

      <v-form ref="formRef" lazy-validation>
        <v-card-text>
          <v-container>
            <v-row>
              <!-- CNPJ (Opcional) -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.cnpj"
                  label="CNPJ"
                  :rules="[cnpjRule]"
                  placeholder="00.000.000/0000-00"
                />
              </v-col>

              <!-- Razão Social (Opcional) -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.razao_social"
                  label="Razão Social"
                />
              </v-col>

              <!-- Email (Opcional) -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.email"
                  label="Email"
                  :rules="[emailRule]"
                />
              </v-col>

              <!-- Telefone (Opcional) -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.phone"
                  label="Telefone"
                  :rules="[phoneRule]"
                  placeholder="(00) 00000-0000"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-form>

      <v-card-actions>
        <v-spacer />
        <v-btn text @click="cancel">Cancelar</v-btn>
        <v-btn text @click="save">Salvar</v-btn>
        <v-spacer />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { defineComponent, ref, watch } from 'vue';
import apiService from '@/services/ApiService';

export default defineComponent({
  name: 'ClientsEditDialog',
  props: {
    client: { type: Object, required: true },
  },
  emits: ['close', 'saved', 'fail'],
  setup(props, { emit }) {
    const dialog = ref(false);
    const formRef = ref(null);
    const form = ref({
      cnpj: '',
      razao_social: '',
      email: '',
      phone: '',
    });

    // Validações de formato opcional
    const cnpjRule = v => !v || /^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$/.test(v) || 'Formato inválido';
    const emailRule = v => !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Email inválido';
    const phoneRule = v => !v || /^(\(?\d{2}\)?\s?)?[\d\s\-]{8,15}$/.test(v) || 'Telefone inválido';

    // Popula e abre sempre que props.client mudar
    watch(
      () => props.client,
      c => {
        if (c) {
          form.value = {
            cnpj: c.cnpj || '',
            razao_social: c.razao_social || '',
            email: c.email || '',
            phone: c.phone || '',
          };
          dialog.value = true;
        }
      },
      { immediate: true }
    );

    // Salva apenas campos preenchidos
    async function save() {
      try {
        const payload = {};
        if (form.value.cnpj) payload.cnpj = form.value.cnpj;
        if (form.value.razao_social) payload.razao_social = form.value.razao_social;
        if (form.value.email) payload.email = form.value.email;
        if (form.value.phone) payload.phone = form.value.phone;

        await apiService.updateClient(props.client.id, payload);
        emit('saved');
        emit('close');
        dialog.value = false;
      } catch (err) {
        console.error('Erro ao atualizar cliente:', err);
        emit('fail');
      }
    }

    function cancel() {
      dialog.value = false;
      emit('close');
    }

    return {
      dialog,
      form,
      formRef,
      cnpjRule,
      emailRule,
      phoneRule,
      save,
      cancel,
    };
  },
});
</script>
