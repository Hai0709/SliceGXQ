<template>
  <div class="models">
    <div class="title" @click="toggleExpand">
      <span class="icon">🤖</span>
      <span class="selected-text">{{ selectedModel || " Select Models" }}</span>
      <span class="expand" :class="{ 'is-expanded': isExpanded }">^</span>
      <div class="dropdown-list" v-show="isExpanded">
        <div
          v-for="model in modelList"
          :key="model.id"
          class="dropdown-item"
          :class="{ active: selectedModel === model.name }"
          @click="selectModel(model)"
        >
          {{ model.name }}
        </div>
      </div>
    </div>

    <div class="model-content">
      <div class="model-diagram">
        <h4></h4>
        <div class="diagram">
          <div class="module input">
            <span>Input</span>
          </div>

          <div
            class="module gcn"
            v-for="(convModule, index) in convModules"
            :key="'conv-' + index"
          >
            <span>{{ selectedModel || "GCN" }}</span>
            <button class="remove-gcn" @click="removeConvModule(index)">×</button>
          </div>

          <div class="module mlp">
            <span>MLP</span>
          </div>

          <div class="module output">
            <span>Output</span>
          </div>
        </div>

        <button class="add-gcn" @click="addConvModule">
          Add {{ selectedModel || "GCN" }}
        </button>
        <button class="show-result-button" @click="showResult">
            Show Result
          </button>
        <div class="train-section">
          <!-- <div class="progress-bar">
            <div class="progress" :style="{ width: progress + '%' }"></div>
          </div> -->
          <!-- <button class="train-button" @click="startTraining" :disabled="isTraining">
            Train Model
          </button> -->
          <!-- <button class="show-result-button" @click="showResult">
            Show Result
          </button> -->
        </div>
      </div>

      <div class="classification-info">
        <h3>Classification Information</h3>
        <div class="table-container" v-if="showTable">
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th></th>
                  <th v-for="id in displayedPointIds" :key="id">{{ id }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in pagedTableData" :key="index">
                  <td>{{ row.label }}</td>
                  <td v-for="(value, idx) in row.values" :key="idx">{{ value }}</td>
                </tr>
                <tr>
                  <td>True Label</td>
                  <td v-for="id in displayedPointIds" :key="'true-' + id">
                    {{ Math.floor(Math.random() * 2) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="pagination">
            <button @click="currentPage = 1" :disabled="currentPage === 1"><<</button>
            <button @click="currentPage -= 1" :disabled="currentPage === 1"><</button>
            <button @click="currentPage += 1" :disabled="currentPage === totalPages">></button>
            <button @click="currentPage = totalPages" :disabled="currentPage === totalPages">>></button>
          </div>



        </div>
      </div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, computed } from "vue";

const isExpanded = ref(false);

const selectedModel = ref("");
const modelList = ref([
  { id: 1, name: "GCN" },
  { id: 2, name: "GIN" },
  { id: 3, name: "GAT" },
]);
const goToFirstPage = () => {
  currentPage.value = 1;
};

const goToPreviousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value -= 1;
  }
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value += 1;
  }
};

const goToLastPage = () => {
  currentPage.value = totalPages.value;
};

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value;
};

const selectModel = (model: { id: number; name: string }) => {
  selectedModel.value = model.name;
  isExpanded.value = false;
};

const convModules = ref<number[]>([]);

const addConvModule = () => {
  convModules.value.push(convModules.value.length + 1);
  console.log(convModules.value,'===convModules');
  
};

const removeConvModule = (index: number) => {
  convModules.value.splice(index, 1);
};

const isTraining = ref(false);
const progress = ref(0);

const startTraining = () => {
  if (isTraining.value) return;
  isTraining.value = true;
  progress.value = 0;

  const interval = setInterval(() => {
    if (progress.value >= 100) {
      clearInterval(interval);
      isTraining.value = false;
      progress.value = 100;
      alert("Training Complete!");
    } else {
      progress.value += 10;
    }
  }, 1000);
};

const showTable = ref(false);
const pointIds = ref(Array.from({ length: 2000 }, (_, i) => i + 1));


const itemsPerPage = 6;
const currentPage = ref(1);
const totalPages = computed(() => Math.ceil(pointIds.value.length / itemsPerPage));

const maxDisplayedPages = 7;

const generatePageNumbers = () => {
  const pages: (number | string)[] = []; 

  const current = currentPage.value;
  const total = totalPages.value;
  const displayedPages = maxDisplayedPages - 2;

  pages.push(1);

  if (current > 3) {
    pages.push("...");
  }

  const start = Math.max(2, current - Math.floor(displayedPages / 2));
  const end = Math.min(total - 1, current + Math.floor(displayedPages / 2));

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  if (end < total - 1) {
    pages.push("...");
  }

  if (total > 1) {
    pages.push(total);
  }

  return pages;
};

const pageNumbers = computed(generatePageNumbers);

const displayedPointIds = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return pointIds.value.slice(start, start + itemsPerPage);
});

const pagedTableData = computed(() => {
  return convModules.value.map((_, index) => ({
    label: `Layer Predict ${index + 1}`,
    values: displayedPointIds.value.map(() => Math.floor(Math.random() * 2)),
  }));
});

const emit = defineEmits(['setSelectedLayers'])
const showResult = () => {
  console.log(convModules.value,'===convModules');
  emit('setSelectedLayers', convModules.value?.length);
  showTable.value = true;
  currentPage.value = 1;
};
</script>






<style scoped lang="less">
.models {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa, #e4e8ed);

  .title {
    background: #0b0b0b;
    color: #ecf0f1;
    padding: 15px;
    font-size: 19px; 
    font-weight: bold; 
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    position: relative;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    width: 100%;
    box-sizing: border-box;
  }

  .title:hover {
    background: #34495e;
  }

  .dropdown-list {
    position: absolute;
    top: 100%;
    left: 0;
    background: #ffffff;
    border: 1px solid #ccc;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    width: 100%;
    border-radius: 8px;
    margin-top: 8px;
    z-index: 1000;
    box-sizing: border-box;
  }

  .dropdown-item {
    padding: 12px 16px;
    font-size: 14px;
    color: #090909;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .dropdown-item:hover {
    background: #f1f1f1;
    color: #007bff;
  }

  .dropdown-item.active {
    background: #007bff;
    color: #ffffff;
    font-weight: bold;
  }

  .model-content {
    flex: 1;
    padding: 10px;
    display: flex;
    gap: 15px;
    overflow: auto;

    .model-diagram {
      flex: 2;
      border: 1px solid #eee;
      border-radius: 8px;
      padding: 10px;
      background: #ffffff;
      position: relative;
      text-align: center;

      h4 {
        margin-bottom: 8px;
        font-weight: bold;
        font-size: 12px;
      }

      .diagram {
        display: flex;
        align-items: center;
        gap: 15px;
        justify-content: center;
        margin-top: 30px; 
        .module {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 8px;
          border: 2px solid #000;
          border-radius: 8px;
          min-width: 60px;
          min-height: 40px;
          text-align: center;
          font-weight: bold;
          background-color: #fff;
          font-size: 12px;
          transition: transform 0.3s ease, box-shadow 0.3s ease;

          &:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
          }

          span {
            z-index: 1;
            font-size: 20px; 
            font-weight: bold; 
          }

          &.input {
            background: #e0f7fa;
          }

          &.gcn {
            background: #ffe0b2;
          }

          &.mlp {
            background: #c8e6c9;
          }

          &.output {
            background: #d1c4e9;
          }

          .remove-gcn {
            position: absolute;
            top: -6px;
            right: -6px;
            width: 16px;
            height: 16px;
            border: none;
            border-radius: 50%;
            background: #ff5252;
            color: #fff;
            font-size: 12px;
            line-height: 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
          }
        }
      }

      .add-gcn {
        
        margin-top: 45px;
        padding: 10px 14px;
        border: none;
        background: #ffb649;
        color: #fff;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        font-size: 19px;
        transition: background-color 0.3s ease;

        &:hover {
          background-color: #fb8c00;
        }
      }
      .show-result-button {
          margin-left: 8px;
          padding: 10px 14px;
          border: none;
          background: #004ea7;
          color: #fff;
          border-radius: 8px;
          font-weight: bold;
          cursor: pointer;
          font-size: 19px;
          transition: background-color 0.3s ease;

          &:hover {
            background-color: #0189ff;
          }
        }
      .train-section {
        margin-top: 15px;
        text-align: center;

        .progress-bar {
          width: 100%;
          height: 8px;
          background: #e0e0e0;
          border-radius: 5px;
          margin-bottom: 8px;
          overflow: hidden;
          position: relative;

          .progress {
            height: 100%;
            background: #ffffff;
            transition: width 0.5s ease;
          }
        }

        .train-button {
          padding: 8px 12px;
          border: none;
          background: #0f79eb;
          color: #fff;
          border-radius: 8px;
          font-weight: bold;
          cursor: pointer;
          font-size: 12px;
          transition: background-color 0.3s ease;

          &:hover {
            background-color: #0056b3;
          }

          &:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
          }
        }

        .show-result-button {
          margin-left: 8px;
          padding: 8px 12px;
          border: none;
          background: #004ea7;
          color: #fff;
          border-radius: 8px;
          font-weight: bold;
          cursor: pointer;
          font-size: 12px;
          transition: background-color 0.3s ease;

          &:hover {
            background-color: #0189ff;
          }
        }
      }
    }


    .classification-info {
      flex: 1;
      border: 1px solid #eee;
      border-radius: 8px;
      padding: 10px;
      text-align: center;
      background: #ffffff;

      h3 {
        margin-top: 15px; 
        font-weight: bold;
        font-size: 18px;
      }

      .table-container {
        margin-top: 15px; 
        margin-top: 8px;
        overflow: hidden;
        position: relative;

        .table-wrapper {

          overflow-x: auto;
          overflow-y: auto;
          width: 100%;
          max-height: 200px;
          border: 1px solid #ddd;
          border-radius: 8px;

          table {
            width: 100%;
            border-collapse: collapse;
            min-width: 500px;

            th,
            td {
              padding: 5px;
              border: 1px solid #ddd;
              text-align: center;
              white-space: nowrap;
              font-size: 12px;
            }

            th {
              background-color: #f5f5f5;
            }
          }
        }

        .pagination {
  margin-top: 15px;
  display: flex;
  justify-content: center;
  gap: 10px; 

  button {
    padding: 10px 20px; 
    border: none;
    background-color: #007bff;
    color: #fff;
    border-radius: 8px; 
    cursor: pointer;
    font-size: 16px; 
    font-weight: bold; 
    transition: background-color 0.3s ease, transform 0.2s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 

    &:hover {
      background-color: #0056b3;
      transform: translateY(-2px);
    }

    &:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
      box-shadow: none; 
    }
  }
}


      }
    }
  }
}
</style>
