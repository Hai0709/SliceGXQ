<template>
  <div class="home">
    <div class="header">
      <div class="avatar" @click="toggleSidebar">SliceGXQ</div>
    </div>
    <div class="main-content">
      <div class="left-panel">
        <Datasets @setInput="handleNodeInput" ref="datasetsRef" />
      </div>
      <div class="right-panel">
        <Models @setSelectedLayers="setSelectedLayers" />
        <SliceGXQ ref="sliceGXQRef" @updateCharts="updateCharts" />
      </div>
    </div>
    <!-- Sidebar -->
    <div class="sidebar" :class="{ open: isSidebarOpen }">
      <div class="sidebar-content">
        <h2>Model Debugging</h2>
        <p></p>
        <div class="button-group">
          <button @click="showFineTuningData">⚙️ Fine-tuning</button>
          <button @click="showArchitectureOptimizationData">⚙️ Architecture Optimization</button>
        </div>
        <!-- 数据表格 -->
        <div class="data-table">
          <h3></h3>
          <table>
            <thead>
              <tr>
                <th>Dataset Name</th>
                <th>Before</th>
                <th>Fine-tuning</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in tableData" :key="index">
                <td>{{ row.col1 }}</td>
                <td>{{ row.col2 }}</td>
                <td>{{ row.col3 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <button @click="toggleSidebar" class="close-btn">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Datasets from './components/Datasets.vue';
import Models from './components/Models.vue';
import SliceGXQ from './components/SliceGXQ.vue';


const sliceGXQRef = ref<InstanceType<typeof SliceGXQ> | null>(null);
const datasetsRef = ref<InstanceType<typeof Datasets> | null>(null);


const isSidebarOpen = ref(false);


const tableData = ref<Array<{ col1: string; col2: string; col3: string }>>([]);


const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};


const showFineTuningData = () => {
  tableData.value = [

    { col1: "YelpChi", col2: "0.7416", col3: "  0.8389" }
  
  ];
};


const showArchitectureOptimizationData = () => {
  tableData.value = [
  { col1: "YelpChi", col2: "0.7416", col3: "  0.8289" }
  ];
};


const handleNodeInput = (nodeInput: string) => {
  console.log("Node ID addedddd:", nodeInput);
  console.log(sliceGXQRef.value, "===sliceGXQRef");
  sliceGXQRef.value?.setNodeInput(nodeInput);
};
const setSelectedLayers = (selectedLayers: number) => {
  console.log("Selected layers:", selectedLayers);
  sliceGXQRef.value?.setSelectedLayers(selectedLayers);
};
const updateCharts = (charts: any) => {
  console.log("Charts updated:", charts);
  console.log(datasetsRef.value, "===datasetsRef");
  datasetsRef.value?.updatePieChartByPagination(charts);
};
</script>

<style scoped lang="less">
.home {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa, #ffffff); 

  .header {
    height: 50px;
    background: #0b0b0b; 
    display: flex;
    justify-content: flex-end;
    align-items: center;
    padding: 0 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 

    .avatar {
      font-size: 16px;
      font-weight: bold;
      color: #ffffff; 
      cursor: pointer;
      transition: color 0.3s ease;

      &:hover {
        color: #40a9ff; 
      }
    }
  }

  .main-content {
    margin-top: 20px;
    flex: 1;
    display: flex;
    column-gap: 40px;

    .left-panel {
      width: 600px;
      border-right: 1px solid #eee;
      background: #ffffff; 
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
    }

    .right-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #ffffff; 
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
    }
  }

  .sidebar {
    position: fixed;
    top: 0;
    right: -33.333%; 
    width: 33.333%; 
    height: 45%;
    background: #ffffff;
    box-shadow: -4px 0 8px rgba(0, 0, 0, 0.1);
    transform: translateX(0);
    transition: transform 0.3s ease;

    &.open {
      transform: translateX(-100%); 
    }

    .sidebar-content {
      padding: 20px;
      text-align: center; 
      font-size: 20px; 
      font-weight: bold; 

      h2 {
        margin: 0;
        font-size: 20px;
        font-weight: bold;
        color: #333;
      }

      p {
        margin: 10px 0;
        color: #666;
        line-height: 1.5;
      }

      .button-group {
        display: flex;
        justify-content: center; 
        gap: 10px;
        margin-bottom: 20px;
        font-size: 20px; 
      font-weight: bold; 
        button {
          padding: 10px 20px;
          background: #40a9ff;
          color: #fff;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          transition: background 0.3s ease;
          font-size: 23px; 
      font-weight: bold; 
          &:hover {
            background: #1890ff;
          }
        }
      }

      .data-table {
        margin-top: 20px;

        h3 {
          font-size: 18px;
          margin-bottom: 10px;
        }

        table {
          width: 100%;
          border-collapse: collapse;

          th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
          }

          th {
            background-color: #f5f5f5;
            font-weight: bold;
          }
        }
      }

      .close-btn {
        margin-top: 20px;
        padding: 10px 20px;
        background: #f5222d;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.3s ease;

        &:hover {
          background: #cf1322;
        }
      }
    }
  }
}
</style>
