<template>
    <div>
      <canvas ref="canvas"></canvas>
    </div>
  </template>
  
  <script>
  import { Chart, registerables } from "chart.js";
import { defineComponent, onMounted, ref, watch } from "vue";
  Chart.register(...registerables);
  
  export default defineComponent({
    name: "BarChart",
    props: {
      chartData: {
        type: Object,
        required: true,
      },
      chartOptions: {
        type: Object,
        default: () => ({}),
      },
    },
    setup(props) {
      const canvas = ref(null);
      let chartInstance = null;
  
      const renderChart = () => {
        if (chartInstance) {
          chartInstance.destroy();
        }
        chartInstance = new Chart(canvas.value, {
          type: "bar",
          data: props.chartData,
          options: props.chartOptions,
        });
      };
  
      onMounted(() => {
        renderChart();
      });
  
      watch(
        () => props.chartData,
        () => {
          renderChart();
        },
        { deep: true }
      );
  
      return { canvas };
    },
  });
  </script>
  