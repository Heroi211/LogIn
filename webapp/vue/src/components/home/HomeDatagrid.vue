<template>
    <v-container fluid>
      <v-row>
        <v-col cols="12" md="4">
          <v-card class="pa-3">
            <v-card-title>{{ userTitle }}</v-card-title>
            <v-data-table
              :headers="userInfoHeaders"
              :items="userInfo"
              hide-default-footer
              dense
            />
          </v-card>
        </v-col>
  
        <v-col cols="12" md="8">
          <v-card class="pa-3" height="300">
            <v-card-title>Rotinas por Status</v-card-title>
            <bar-chart :chart-data="chartData" :chart-options="chartOptions" />
          </v-card>
        </v-col>
      </v-row>
  
      <v-row>
        <v-col cols="12">
          <routines-datagrid :show-actions="false" />
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script>
import RoutinesDatagrid from "@/components/rotinas/RoutinesDatagrid.vue";
import apiService from "@/services/ApiService";
import { onMounted, ref } from "vue";
import BarChart from "./BarChart.vue";
  
  export default {
    name: "Home",
    components: {
      RoutinesDatagrid,
      BarChart,
    },
    setup() {
      const userTitle = "Colaborador / Mês Corrente";
  
      const userInfoHeaders = [
        { text: "Colaborador", value: "colaborador" },
        { text: "Qtd Rotinas", value: "qtd" },
        { text: "Status", value: "status" },
      ];
      const userInfo = ref([
        { colaborador: "João", qtd: 5, status: "Em andamento" },
        { colaborador: "Maria", qtd: 3, status: "Concluído" },
        { colaborador: "Pedro", qtd: 2, status: "Pendente" },
      ]);
  
      const chartData = ref({
        labels: [],
        datasets: [
          {
            label: "Rotinas",
            backgroundColor: "#42A5F5",
            data: [],
          },
        ],
      });
      const chartOptions = ref({
        responsive: true,
        maintainAspectRatio: false,
      });
  
      const fetchChartData = async () => {
        try {
          const routines = await apiService.getRoutines();
          const statusCounts = {};
          routines.forEach((routine) => {
            const status = routine.status || "Desconhecido";
            if (!statusCounts[status]) {
              statusCounts[status] = 0;
            }
            statusCounts[status]++;
          });
          chartData.value.labels = Object.keys(statusCounts);
          chartData.value.datasets[0].data = Object.values(statusCounts);
        } catch (err) {
          console.error("Erro ao carregar dados para o gráfico:", err);
        }
      };
  
      onMounted(() => {
        fetchChartData();
      });
  
      return {
        userTitle,
        userInfoHeaders,
        userInfo,
        chartData,
        chartOptions,
      };
    },
  };
  </script>
  