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
              <v-text-field v-model="editUser.titulo" label="Titulo" aria-required="true" />
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-text-field v-model="editUser.descricao" label="Descrição" aria-required="true" />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="$emit('fechaModal')"> Cancelar </v-btn>
        <v-btn color="blue darken-1" text @click="salvarRotina"> Salvar </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: "RoutinesDialog",
  components: {},
  props: {},
  setup(props) {
    const dialog = ref(true)
    const editUser = ref({})

    function fechaModal() {
      dialog.value = false
    }
    async function salvarRotina() {

    }

    return {
      dialog,
      editUser,
      fechaModal,
      salvarRotina
    }
  }
})
</script>
