<template>
  <div class="slice-gxq">
    <div class="title">
      <span class="icon">⚙️</span>
      SliceGXQ
    </div>
    <div class="content">
      <div class="query">
        <div
          class="param-box"
          :class="{ active: activeBox === 'paramBox' }"
          @click="setActiveBox('paramBox')"
        >
          <div class="param-mode">
            <div class="form-item" v-for="(label, key) in paramFields" :key="key">
              <label :for="key">
                {{ label }}
                <span class="tooltip-icon" :title="tooltips[key]">❓</span>
              </label>
              <input :id="key" type="text" v-model="params[key]" />
            </div>
          </div>
          <button class="play-param" @click="calculateQuery2">⚙️ Generate</button>
        </div>

        <div
          class="query-box"
          :class="{ active: activeBox === 'queryBox' }"
          @click="setActiveBox('queryBox')"
        >
          <label class="query-title">Query</label>
          <textarea
            v-model="queryContent"
            placeholder="Enter your query here..."
            spellcheck="false"
          ></textarea>
          <div class="query-buttons">
            <button class="history-button" @click="showHistory">📜 History</button>
            <button class="hint-button" @click="insertTemplate">💡 Help</button>
            <button class="play-query" @click="calculateQuery">⚙️ Generate</button>
          </div>
        </div>
      </div>

      <div class="explanation">
        <h3>Explanation with model-slicing</h3>
        <div class="legend"></div>
        <div class="prediction">
          <div class="model-container" ref="graphContainerRef">
            <svg width="100%" height="100%">
              <g v-if="isRunning">

                <line
                  v-for="(link, index) in currentLayer.links"
                  :key="index"
                  :x1="currentLayer.nodes.find(n => n.id === link.source)?.x"
                  :y1="currentLayer.nodes.find(n => n.id === link.source)?.y"
                  :x2="currentLayer.nodes.find(n => n.id === link.target)?.x"
                  :y2="currentLayer.nodes.find(n => n.id === link.target)?.y"
                  stroke="#aaa"
                  stroke-width="2"
                />
     
                <circle
                  v-for="(node, nodeIndex) in currentLayer.nodes"
                  :key="node.id"
                  :cx="node.x"
                  :cy="node.y"
                  r="20"
                  :fill="node.color"
                  :stroke="node.borderColor"
                  stroke-width="4"
                  @mousedown="(event) => startDrag(event, node)"
                  @mouseenter="showTooltip(node)"
                  @mouseleave="hideTooltip"
                  style="cursor: pointer;"
                />
         
                <text
                  v-if="hoveredNode"
                  :x="hoveredNode.x + 30"
                  :y="hoveredNode.y - 10"
                  font-size="12"
                  fill="#333"
                >
                  ID: {{ hoveredNode.id }}
                </text>
              </g>
            </svg>
          </div>
        </div>
        <div class="pagination">
          <button @click="changePage(1)" :disabled="currentPage === 1"><<</button>
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"><</button>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">></button>
          <button @click="changePage(totalPages)" :disabled="currentPage === totalPages">>></button>
        </div>
      </div>
    </div>


    <div v-if="isHistoryModalVisible" class="history-modal">
      <div class="history-modal-content">
        <h3>Query History</h3>
        <ul>
          <li v-for="(query, index) in queryHistory" :key="index">
            {{ index + 1 }}. {{ query }}
          </li>
        </ul>
        <button @click="closeHistory" class="close-button">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, inject } from "vue";

const activeBox = ref<string>("");

const setActiveBox = (box: string) => {
  activeBox.value = box;
};
const nodeInput = inject('nodeInput', ref(''));

const paramFields = {
  nodeSet: "Node Set:",
  targetLayer: "Target layer:",
  selectedLayers: "Selected layers:",
  mode: "Mode:",

  size: "Size:"
};
const setNodeInput = (value: string) => {
  console.log(value,'===value');
  // paramFields.nodeSet = value;
  params.value.nodeSet = value;
}
const setSelectedLayers = (value: number) => {
  console.log(value, '===value');
  const layerNumbers = Array.from({ length: value }, (_, i) => i + 1);
  const layerNumbersString = layerNumbers.join(', ');
  params.value.selectedLayers = layerNumbersString;
};

defineExpose({ setNodeInput, setSelectedLayers });

interface Params {
  nodeSet: string;
  targetLayer: string;
  selectedLayers: string; 
  mode: string;
  size: string;
}


const tooltips = {
  nodeSet: "Enter the ID of the nodes to be tested",
  targetLayer: "The target layer that needs to be explained by GNN (e.g. first layer, second layer)",
  selectedLayers: "Enter the model layer number to be parsed",
  mode: "Select the required mode, diagnose or interpret",
  size: "Enter the maximum number of nodes that need to be explained by GNN"
};

const params = ref<Params>({
  nodeSet: "",
  targetLayer: "",
  selectedLayers: "",
  mode: "",

  size: ""
});


const queryContent = ref("");
const queryHistory = ref<string[]>([]); 
const isHistoryModalVisible = ref(false); 

const insertTemplate = () => {
  queryContent.value = "EXPLAN (Model, {Nodes}) AT {Which Layers} FROM {Dataset, {Layers}} WHERE ? WITH mode";
};

const displayedModels = ref([
  "Model 1: Small Ball",
  "Model 2: Medium Ball",
  "Model 3: Large Ball"
]);
const currentPage = ref(1); 
const totalPages = ref(5); 
const isRunning = ref(false); 
const hoveredNode = ref<any>(null); 


const layers2 = ref([
{
    nodes: [
      { id: 239, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" }, 
      { id: 2418, color: "#F19C99", borderColor: "#007bff", x: 200, y: 200, category: "Fraud" },
      { id: 65, color: "#F19C99", borderColor: "#007bff", x: 300, y: 100, category: "Fraud" }
    ],
    links: [
      { source: 239, target: 2418 },
      { source: 2418, target: 65 },
      { source: 239, target: 65 }
    ]
  },
  {
    nodes: [
      { id: 2418, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" },
      { id: 239, color: "#F19C99", borderColor: "#007bff", x: 200, y: 100, category: "Fraud" },
      { id: 65, color: "#F19C99", borderColor: "#FF0000", x: 300, y: 100, category: "Fraud" },
      { id: 771, color: "#f7d38c", borderColor: "#007bff", x: 150, y: 200, category: "Benign" }, 

    ],
    links: [
    { source: 2418, target: 239 }, 
      { source: 239, target: 65 },
      { source: 2418, target: 65 },
      { source: 771, target: 65 }
    ]
  },
  {
    nodes: [
    { id: 2020, color: "#f7d38c", borderColor: "#007bff", x: 100, y: 100, category: "Benign" }, 
      { id: 55, color: "#f7d38c", borderColor: "#007bff", x: 200, y: 100, category: "Benign" },
      { id: 65, color: "#F19C99", borderColor: "#FF0000", x: 300, y: 100, category: "Fraud" },
      { id: 239, color: "#F19C99", borderColor: "#007bff", x: 150, y: 200, category: "Fraud" }, 

    ],
    links: [
    { source: 2020, target: 55 }, 
      { source: 55, target: 65 },
      { source: 65, target: 239 }
    ] 
  }
]);


const layers = ref([
  {
    nodes: [
      { id: 2418, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" }, 
      { id: 239, color: "#F19C99", borderColor: "#007bff", x: 200, y: 100, category: "Fraud" },
      { id: 65, color: "#F19C99", borderColor: "#FF0000", x: 300, y: 100, category: "Fraud" },
      { id: 771, color: "#f7d38c", borderColor: "#007bff", x: 150, y: 200, category: "Benign" }, 

    ],
    links: [
    { source: 2418, target: 239 }, 
      { source: 239, target: 65 },
      { source: 2418, target: 65 },
      { source: 771, target: 65 }
    ]
  },
  {
    nodes: [
    { id: 2020, color: "#f7d38c", borderColor: "#007bff", x: 100, y: 100, category: "Benign" }, 
      { id: 55, color: "#f7d38c", borderColor: "#007bff", x: 200, y: 100, category: "Benign" },
      { id: 65, color: "#F19C99", borderColor: "#FF0000", x: 300, y: 100, category: "Fraud" },
      { id: 239, color: "#F19C99", borderColor: "#007bff", x: 150, y: 200, category: "Fraud" }, 

    ],
    links: [
    { source: 2020, target: 55 }, 
      { source: 55, target: 65 },
      { source: 65, target: 239 }
    ] 
  }
]);

const layers3 = ref([
  {
    nodes: [
      { id: 55, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" }, 
      { id: 210, color: "#F19C99", borderColor: "#007bff", x: 200, y: 200, category: "Fraud" },
      { id: 1079, color: "#F19C99", borderColor: "#007bff", x: 300, y: 100, category: "Fraud" }
    ],
    links: [
    { source: 55, target: 210 }, 
      { source: 210, target: 1079 },
      { source: 1079, target: 55 }

    ]
  },
  {
    nodes: [
      { id: 55, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" }, 
      { id: 210, color: "#F19C99", borderColor: "#007bff", x: 200, y: 200, category: "Fraud" },
      { id: 1079, color: "#F19C99", borderColor: "#007bff", x: 300, y: 100, category: "Fraud" },
      { id: 1905, color: "#f7d38c", borderColor: "#007bff", x: 300, y: 200, category: "Benign" },
      { id: 1914, color: "#F19C99", borderColor: "#007bff", x: 400, y: 200, category: "Fraud" }
    ],
    links: [
    { source: 55, target: 210 }, 
      { source: 210, target: 1079 },
      { source: 1079, target: 55 },
      { source: 210, target: 1905 },
      { source: 1079, target: 1914 },
      { source: 1905, target: 1914 }

    ]
  },
  {
    nodes: [
      { id: 2, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" }, 
      { id: 2381, color: "#F19C99", borderColor: "#007bff", x: 200, y: 200, category: "Fraud" },
      { id: 1666, color: "#F19C99", borderColor: "#007bff", x: 300, y: 100, category: "Fraud" }
    ],
    links: [
      { source: 2, target: 2381 }, 
      { source: 2381, target: 1666 },
      { source: 1666, target: 2 }
    ]
  },
  {
    nodes: [
      { id: 2, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" },
      { id: 2381, color: "#F19C99", borderColor: "#007bff", x: 200, y: 200, category: "Fraud" },
      { id: 1666, color: "#F19C99", borderColor: "#FF0000", x: 300, y: 100, category: "Fraud" },
      { id: 49, color: "#F19C99", borderColor: "#007bff", x: 400, y: 100, category: "Fraud" },
      { id: 606, color: "#f7d38c", borderColor: "#007bff", x: 200, y: 100, category: "Benign" },

    ],
    links: [
      { source: 2, target: 2381 }, 
      { source: 2381, target: 1666 },
      { source: 1666, target: 2 },
      { source: 1666, target: 49 },
      { source: 1666, target: 606 }
    ]
  },

  {
    nodes: [
      { id: 2, color: "#F19C99", borderColor: "#007bff", x: 100, y: 100, category: "Fraud" }, 
      { id: 1666, color: "#F19C99", borderColor: "#FF0000", x: 300, y: 100, category: "Fraud" },
      { id: 606, color: "#f7d38c", borderColor: "#007bff", x: 200, y: 100, category: "Benign" },
      { id: 712, color: "#F19C99", borderColor: "#007bff", x: 140, y: 200, category: "Benign" }

    ],
    links: [
      { source: 1666, target: 2 },
      { source: 606, target: 712 },
      { source: 1666, target: 606 }
    ]
  }
  
]);

const emit = defineEmits(['updateCharts'])
const activeLayers = ref<typeof layers>([]);

let generateClickCount = ref(0); 

const calculateQuery = () => {
  if (queryContent.value.trim()) {
    queryHistory.value.push(queryContent.value); 
    console.log("Query added to history: ", queryContent.value);
  }

  generateClickCount.value++; 

  // 根据点击次数切换数据
  if (generateClickCount.value === 1) {
    activeLayers.value = layers.value; 
    console.log("Generated using layers");
  } else if (generateClickCount.value === 2) {
    activeLayers.value = layers3.value; 
    console.log("Generated using layers3");
    generateClickCount.value = 0; 
  }

  currentPage.value = 1; 
  isRunning.value = true; 
};



const calculateQuery2 = () => {
  if (queryContent.value.trim()) {
    queryHistory.value.push(queryContent.value); 
    console.log("Query calculated: ", queryContent.value);
  }
  activeLayers.value = layers2.value; 
  currentPage.value = 1;
  isRunning.value = true; 
  console.log("Generated using layers2");
};


const currentLayer = computed(() => {
  const target = activeLayers.value[currentPage.value - 1] || { nodes: [], links: [] };
  emit('updateCharts', target); 
  return target; 
});





const showHistory = () => {
  isHistoryModalVisible.value = true;
};


const closeHistory = () => {
  isHistoryModalVisible.value = false;
};


const startDrag = (event: MouseEvent, node: any) => {
  const startX = event.clientX;
  const startY = event.clientY;
  const initialX = node.x;
  const initialY = node.y;

  const onMouseMove = (moveEvent: MouseEvent) => {
    const dx = moveEvent.clientX - startX;
    const dy = moveEvent.clientY - startY;
    node.x = initialX + dx;
    node.y = initialY + dy;
  };

  const onMouseUp = () => {
    document.removeEventListener("mousemove", onMouseMove);
    document.removeEventListener("mouseup", onMouseUp);
  };

  document.addEventListener("mousemove", onMouseMove);
  document.addEventListener("mouseup", onMouseUp);
};


const resetNodePositions = () => {
  const layer = activeLayers.value[currentPage.value - 1] || { nodes: [] };
  const containerWidth = graphContainerRef.value?.clientWidth || 600; 
  const containerHeight = graphContainerRef.value?.clientHeight || 400; 
  const centerX = containerWidth / 2;
  const centerY = containerHeight / 2;
  const radius = Math.min(containerWidth, containerHeight) * 0.3; 
  const angleStep = (2 * Math.PI) / layer.nodes.length; 

  layer.nodes.forEach((node, index) => {
    const angle = index * angleStep;
    node.x = centerX + radius * Math.cos(angle);
    node.y = centerY + radius * Math.sin(angle);
  });
};

const changePage = (newPage: number) => {
  currentPage.value = newPage;
  resetNodePositions(); 
};


const graphContainerRef = ref<HTMLElement | null>(null);
let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  if (graphContainerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      resetNodePositions(); 
    });
    resizeObserver.observe(graphContainerRef.value);
  }
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});


const showTooltip = (node: any) => {
  hoveredNode.value = node;
};


const hideTooltip = () => {
  hoveredNode.value = null;
};
</script>


<style scoped lang="less">
.slice-gxq {
  height: 80%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa, #e4e8ed);
.tooltip-icon {
  margin-left: 7px; 
  font-size: 12px; 
  cursor: pointer; 
  color: #8c9daf; 
}
.param-box,
    .query-box {
      background: #f5f7fa;
      transition: box-shadow 0.3s ease, background 0.3s ease;
      box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);

      &.active {
        box-shadow: 0 0 15px rgba(0, 123, 255, 0.8);
        background: #ffffff;
      }
    }
  .history-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;

    .history-modal-content {
      background: #ffffff;
      padding: 20px;
      border-radius: 8px;
      width: 400px;
      max-height: 80vh; 
      overflow-y: auto;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);

      h3 {
        margin-bottom: 15px;
        color: #333333;
      }

      ul {
        list-style-type: none;
        padding: 0;
        margin: 0;

        li {
          padding: 10px;
          border-bottom: 1px solid #eee;
          color: #333333;

          &:last-child {
            border-bottom: none;
          }
        }
      }

      .close-button {
        margin-top: 15px;
        padding: 8px 16px;
        background-color: #0957a0;
        color: #fff;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s ease;

        &:hover {
          background-color: #59a4e1;
        }
      }
    }
  }

  .title {
    padding: 15px;
    background: #333333;
    color: white;
    display: flex;
    justify-content: center; 
    align-items: center;
    gap: 10px;
    border-radius: 8px 8px 0 0;
    font-size: 19px; 
    font-weight: bold; 
  }

  .content {
    flex: 1;
    padding: 15px;
    display: flex;
    gap: 20px;

    .query {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;

   
      .param-box,
      .query-box {
        position: relative;
        width: 100%;
        max-width: 500px;
        height: auto;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 15px;
        padding-bottom: 50px; 
        background: #ffffff;

        .param-mode {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;

          .form-item {
            display: flex;
            flex-direction: column;

            label {
              font-size: 23px; 
              font-weight: bold; 
              margin-bottom: 5px;
              color: #000000;
            }

            input {
              padding: 4px; 
              border: 1px solid #ccc;
              border-radius: 4px;
              font-size: 21px; 
              font-weight: bold; 
              outline: none;

              &:focus {
                border-color: #007bff;
                box-shadow: 0 0 3px rgba(0, 123, 255, 0.5);
              }
            }
          }
        }

        .play-param,
        .play-query {
          position: absolute; 
          bottom: 10px; 
          right: 10px; 
          width: 140px; 
          height: 38px; 
          border-radius: 5px;
          border: none; 
          background: #0957a0; 
          color: #fff; 
          cursor: pointer; 
          display: flex; 
          justify-content: center;
          align-items: center;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); 

          &:hover {
            background: #59a4e1; 
          }
        }

        .history-button, .hint-button {
          border-radius: 5px;
          position: absolute; 
          bottom: 10px; 
          padding: 10px 12px;
          border: none;
          cursor: pointer;
          transition: background-color 0.3s ease;
          font-size: 15px; 
          
        }

        .history-button {
          left: 14px;
          background-color: #6c757d;
          color: #fff;

          &:hover {
            background-color: #8b8c8d;
          }
        }

        .hint-button {
          left: 125px; 
          background-color: #a77d28;
          color: #fff;

          &:hover {
            background-color: #f7d38c;
          }
        }
      }

     
      .query-box {
        label {
          font-size: 23px; 
          font-weight: bold; 
        }

        textarea {
          width: 95%;
          height: 120px; 
          padding: 10px;
          background-color: #edecec;
          border: 1px solid #ccc;
          border-radius: 4px;
          font-family: "Courier New", Courier, monospace;
          font-size: 20px; 
          font-weight: bold; 
          resize: none;
          outline: none;

          &::placeholder {
            color: #999;
            font-weight: bold; 
          }
        }
      }
    }

    .explanation {
      background: #ffffff;
      border: 1px solid #eee;
      border-radius: 8px;
      padding: 15px;
      flex: 1.2;
      display: flex;
      flex-direction: column;

      h3 {
    margin-bottom: 15px;
    color: #000000;
    font-size: 23px; 
    font-weight: bold; 
    text-align: center; 
  }

      .model-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 300px;
        border: 1px solid #ddd;
        background-color: #edecec;
        border-radius: 8px 8px 0 0;
        margin-bottom: 20px;
        position: relative; 
        overflow: hidden; 

        svg {
          width: 100%;
          height: 100%;
          position: absolute; 
          top: 0;
          left: 0;
        }
      }

      .pagination {
        margin-top: 15px;
        display: flex;
        justify-content: center;
        gap: 5px;

        button {
          padding: 5px 10px;
          border: none;
          background-color: #007bff;
          color: #fff;
          border-radius: 5px;
          cursor: pointer;
          transition: background-color 0.3s ease;

          &:hover {
            background-color: #0056b3;
          }

          &:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
          }
        }
      }
    }
  }
}
</style>
