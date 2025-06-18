<template>
  <v-dialog v-model="visible" max-width="600px">
    <v-card v-if="visible">
      <v-card-title>Editar Rotina</v-card-title>
      <v-card-text>
        <v-text-field v-model="form.titulo" label="Título" />
        <v-textarea  v-model="form.descricao" label="Descrição" />
        <!-- outros campos -->
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="fechar">Cancelar</v-btn>
        <v-btn text @click="salvar">Salvar</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { defineComponent, ref, watch } from 'vue';
import apiService from '@/services/ApiService';

export default defineComponent({
  name: 'EditRoutineDialog',
  props: {
    visible: { type: Boolean, required: true },
    routine: { type: Object, required: true }
  },
  emits: ['update:visible','atualiza','success','fail'],
  setup(props, { emit }) {
    const form = ref({ titulo: '', descricao: '' /*…*/ });

    watch(() => props.visible, open => {
      if (!open) return;
      Object.assign(form.value, props.routine);
    });

    const fechar = () => emit('update:visible', false);

    const salvar = () => {
      apiService.updateRoutine(props.routine.id, form.value)
        .then(() => {
          emit('atualiza');
          emit('update:visible', false);
          emit('success','Rotina atualizada com sucesso');
        })
        .catch(() => emit('fail','Erro ao atualizar'));
    };

    return { form, fechar, salvar };
  }
});
</script>
