<template>
  <v-data-table v-model="selected" :items="routines" :headers="headers" show-select>
    <template v-slot:top>
      <v-toolbar flat>
        <v-toolbar-title>Rotinas</v-toolbar-title>
        <v-divider class="mx-4" inset vertical></v-divider>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-btn color="primary" dark class="mb-2" @click="dialog = true">
          Nova Rotina
        </v-btn>
      </v-toolbar>

    </template>
  </v-data-table>
</template>
<script>
import { computed, defineComponent, ref } from "vue";

export default defineComponent({
  name: "RoutinesDatagrid",
  components: {},
  setup() {
    const routines = ref([{
      "id": 1,
      "titulo": "Implementação do 2FA no sistema.",
      "descricao": "Para melhorar a segurança do logon no sistema, precisamos implementar o 2FA por email.",
      "status": "completo",
      "hr_estimativa": "2024-11-30T14:28:24.012000",
      "hr_real": "2024-11-30T14:28:24.012000",
      "client": "gabriel",
      "prioridade": "alta",
      "dt_vencimento": "2024-11-30T14:28:24.012000"
    }
    ])

    const headers = ref([
      { title: "titulo", key: "titulo", align: "end" },
      { title: "descrição", key: "descricao", align: "end" },
      { title: "status", key: 'status' },
      { title: "hora estimativa", key: "hr_estimativa" },
      { title: "hora real", key: "hr_real" },
      { title: "cliente", key: "client" },
      { title: "prioridade", key: "prioridade" },
      { title: "prazo", key: "dt_vencimento" }
    ])

    const selected = ref([])
    const editedIndex = ref(-1)
    const formTitle = computed(() => {
      return editedIndex.value === -1 ? 'Nova Rotina' : 'Editar Rotina'
    })

    return {
      routines,
      headers,
      selected,
      formTitle
    }
  }
});
</script>
