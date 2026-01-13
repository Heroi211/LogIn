<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Editar Usuário</span>
      </v-card-title>

      <v-form ref="formRef" lazy-validation>
        <v-card-text>
          <v-container>
            <v-row>
              <!-- Nome (Opcional) -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.name"
                  label="Nome"
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

              <!-- CPF (Opcional) -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.cpf"
                  label="CPF"
                  :rules="[cpfRule]"
                  placeholder="000.000.000-00"
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

              <!-- Ativo (Opcional) -->
              <v-col cols="12" sm="6">
                <v-switch
                  v-model="form.active"
                  label="Ativo"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-form>

      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="cancel">Cancelar</v-btn>
        <v-btn text @click="save">Salvar</v-btn>
        <v-spacer/>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { defineComponent, ref, watch } from 'vue';
import apiService from '@/services/ApiService';

export default defineComponent({
  name: 'UsersEditDialog',
  props: {
    user: { type: Object, required: true },
  },
  emits: ['close', 'saved', 'fail'],
  setup(props, { emit }) {
    const dialog = ref(false);
    const formRef = ref(null);
    const form = ref({
      name: '',
      email: '',
      cpf: '',
      phone: '',
      active: false,
    });

    // Validações opcionais
    const emailRule = v =>
      !v || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'Email inválido';
    const cpfRule = v =>
      !v || /^\d{3}\.\d{3}\.\d{3}\-\d{2}$/.test(v) || 'Formato inválido';
    const phoneRule = v =>
      !v || /^(\(?\d{2}\)?\s?)?[\d\s\-]{8,15}$/.test(v) || 'Telefone inválido';

    // Abre o diálogo e popula o form sempre que props.user mudar
    watch(
      () => props.user,
      u => {
        if (u) {
          form.value = {
            name: u.name || '',
            email: u.email || '',
            cpf: u.cpf || '',
            phone: u.phone || '',
            active: typeof u.active === 'boolean' ? u.active : false,
          };
          dialog.value = true;
        }
      },
      { immediate: true }
    );

    // Ao clicar em Salvar
    async function save() {
      try {
        const payload = {};
        if (form.value.name) payload.name = form.value.name;
        if (form.value.email) payload.email = form.value.email;
        if (form.value.cpf) payload.cpf = form.value.cpf;
        if (form.value.phone) payload.phone = form.value.phone;
        payload.active = form.value.active;

        await apiService.updateUser(props.user.id, payload);
        emit('saved');
        emit('close');
        dialog.value = false;
      } catch (err) {
        console.error('Erro ao atualizar usuário:', err);
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
      emailRule,
      cpfRule,
      phoneRule,
      save,
      cancel,
    };
  },
});
</script>
