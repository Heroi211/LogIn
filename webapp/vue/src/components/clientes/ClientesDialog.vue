<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Novo Cliente</span>
      </v-card-title>
      <v-form ref="formRef" lazy-validation>
        <v-card-text>
          <v-container>
            <v-row>
                <v-col cols="12" sm="6">
                <v-text-field
                  v-model="client.cnpj"
                  label="CNPJ"
                  :rules="[requiredRule, cnpjRule]"
                  placeholder="00.000.000/0000-00"
                  required
                  @input="onCnpjInput"
                  maxlength="18"
                />
                </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="client.razao_social"
                  label="Razão Social"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="client.email"
                  label="Email"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="client.phone"
                  label="Telefone"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-form>
      <v-card-actions>
        <v-spacer/>
        <v-btn text @click="close">Cancelar</v-btn>
        <v-btn
          text
          :disabled="!canSave"
          @click="save"
        >Salvar</v-btn>
        <v-spacer/>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { defineComponent, ref, computed } from 'vue';
import apiService from '@/services/ApiService';

export default defineComponent({
  name: 'ClientsDialog',
  emits: ['close', 'saved', 'fail'],
  setup(_, { emit }) {
    const dialog = ref(true);
    const client = ref({ cnpj: '', razao_social: '', email: '', phone: '' });
    const formRef = ref(null);

    const requiredRule = v => !!v || 'Campo obrigatório';
    const cnpjRule = v => /^\d{2}\.\d{3}\.\d{3}\/\d{4}\-\d{2}$/.test(v) || 'Formato inválido';

    const canSave = computed(() => 
      client.value.cnpj && client.value.razao_social && cnpjRule(client.value.cnpj) === true && requiredRule(client.value.email) === true && requiredRule(client.value.phone) === true
    );

    function close() {
      emit('close');
    }

    function formatCNPJ(value) {
      const digits = value.replace(/\D/g, '').slice(0, 14);
      if (digits.length <= 2) return digits;
      if (digits.length <= 5) return `${digits.slice(0,2)}.${digits.slice(2)}`;
      if (digits.length <= 8) return `${digits.slice(0,2)}.${digits.slice(2,5)}.${digits.slice(5)}`;
      if (digits.length <= 12) return `${digits.slice(0,2)}.${digits.slice(2,5)}.${digits.slice(5,8)}/${digits.slice(8)}`;
      return `${digits.slice(0,2)}.${digits.slice(2,5)}.${digits.slice(5,8)}/${digits.slice(8,12)}-${digits.slice(12)}`;
    }
    function onCnpjInput(e) {
      client.value.cnpj = formatCNPJ(e.target.value);
    }

    async function save() {
      try {
        client.value.cnpj = client.value.cnpj.replace(/\D/g, ''); // Remove non-numeric characters
        console.log('Saving client:', client.value);
        await apiService.createClient(client.value);
        emit('saved');
        emit('close');
      } catch (err) {
        console.error(err);
        emit('fail');
      }
    }

    return { dialog, client, formRef, requiredRule, cnpjRule, canSave, close, save,onCnpjInput, formatCNPJ };
  }
});
</script>
