<template>
  <div class="datasets">

    <div class="title" @click="toggleExpand">
      <span class="icon">📚</span>
      <span class="selected-text">{{ selectedDataset || "Datasets" }}</span>
      <span class="expand" :class="{ 'is-expanded': isExpanded }">^</span>
      <div class="dropdown-list" v-show="isExpanded">
        <div
          v-for="dataset in datasetList"
          :key="dataset.id"
          class="dropdown-item"
          :class="{ active: selectedDataset === dataset.name }"
          @click="selectDataset(dataset)"
        >
          {{ dataset.name }}
        </div>
      </div>
    </div>


    <div class="graph-view">
      <div class="search">
        <input type="text" v-model="searchQuery" placeholder="Search for node ids..." />
        <button @click="fetchNodeData">Search</button>
      </div>
      <div ref="graphContainerRef" class="graph-container"></div>
    </div>


    <div class="info">
      <h3>Select Interested Nodes</h3>
      <div class="description">
        <div class="description-box">
   
        </div>
      </div>

      <div class="node-input">
        <input type="text" v-model="nodeInput" placeholder="Enter node ID..." />
        <button @click="addNodeId">Form</button>
      </div>
    </div>

 
    <div class="statistics">
      <h4 class="statistics-title"></h4>
      <div class="charts">
        <div class="chart-item" ref="barChartRef"></div>
        <div class="chart-item" ref="pieChartRef"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ref, onMounted, onUnmounted, provide, defineExpose } from "vue";
import * as echarts from "echarts";
import axios from "axios";

export default {
  name: "DatasetVisualization",
  emits: ["setInput"],
  setup(_, { emit }) {
    const isExpanded = ref(false); 
    const selectedDataset = ref(""); 
    const datasetList = ref([
      { id: 1, name: "Yelpchi" },
      { id: 2, name: "Cora" },
      { id: 3, name: "Ba-shape" },
    ]);
    const datasetDescription = ref("No dataset selected.");
    const searchQuery = ref(""); 

    const toggleExpand = () => {
      isExpanded.value = !isExpanded.value;
    };

    const selectDataset = (dataset: { id: number; name: string }) => {
      selectedDataset.value = dataset.name;
      datasetDescription.value = `You selected ${dataset.name}.`;
      isExpanded.value = false;

      fetchGraphData(dataset.id, "dataset"); 
    };

    const graphContainerRef = ref<HTMLElement | null>(null);
    let graphChart: echarts.ECharts | null = null;

    const updateBarChart = (edgeStatistics: number[][]) => {

      const flatEdges = edgeStatistics.flat();
      const edgeWithTypes = flatEdges.map((count, index) => {
        const sourceType = Math.floor(index / 6); 
        const targetType = index % 6;
        return {
          type: `${sourceType}->${targetType}`, 
          count: count, 
        };
      });


      const topEdges = edgeWithTypes
        .sort((a, b) => b.count - a.count) 
        .slice(0, 6);

      // 从 topEdges 中提取数据
      const xAxisData = topEdges.map((edge) => edge.type); 
      const seriesData = topEdges.map((edge) => edge.count); 

      const barChartOption = {
        title: {
          text: "",
          left: "center",
          textStyle: {
            color: "#333",
            fontSize: 16,
          },
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        grid: {
          left: "10%",
          right: "10%",
          bottom: "10%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: xAxisData, 
          axisTick: {
            alignWithLabel: true,
          },
          axisLine: {
            lineStyle: {
              color: "#ccc",
            },
          },
        },
        yAxis: {
          type: "value",
          axisLine: {
            show: false,
          },
          axisTick: {
            show: false,
          },
          splitLine: {
            lineStyle: {
              color: "#eee",
            },
          },
        },
        series: [
          {
            name: "Edge Count",
            type: "bar",
            barWidth: "40%",
            data: seriesData, 
            itemStyle: {
              color: "#007bff",
              borderRadius: [4, 4, 0, 0],
            },
          },
        ],
      };

      if (barChart) {
        barChart.setOption(barChartOption);
      }
    };
    const nodeInput = ref(""); 

    const addNodeId = () => {
      if (!nodeInput.value.trim()) {
        alert("Please enter a valid node ID");
        return;
      }
      console.log("Node ID added:", nodeInput.value);

      provide("nodeInput", nodeInput);
      emit("setInput", nodeInput.value);
    };

 
    const fetchGraphData = async (id: number, mode: "dataset" | "search") => {
      try {
        const endpoint =
          mode === "dataset" ? `http://127.0.0.1:5000/api/graph-data/${id}` : `http://127.0.0.1:5000/api/node-data/${id}`;
        const response = await axios.get(endpoint);

        console.log("Fetched graph data:", response.data);

        if (graphChart) {
          graphChart.dispatchAction({
            type: "restore", 
          });
        }

        if (response.data && response.data.nodes && response.data.links) {
          const baseSymbolSize = mode === "dataset" ? 10 : 30;

        
          updateGraphChart(response.data.nodes, response.data.links, baseSymbolSize);

        
          if (mode === "dataset" && response.data.label_count) {
            updatePieChart(response.data.label_count);
          }

         
          const edgeStatisticsEndpoint = `http://127.0.0.1:5000/api/edge-statistics/${id}`;
          const edgeStatisticsResponse = await axios.get(edgeStatisticsEndpoint);
          if (edgeStatisticsResponse.data && edgeStatisticsResponse.data.edge_statistics) {
            updateBarChart(edgeStatisticsResponse.data.edge_statistics);
          }
        } else {
          console.error("Invalid graph data structure:", response.data);
        }
      } catch (error) {
        console.error("Error fetching graph data:", error);
      }
    };


    const fetchNodeData = async () => {
      if (!searchQuery.value.trim()) {
        alert("Please enter a valid node ID");
        return;
      }

      const nodeId = parseInt(searchQuery.value);


      if (graphChart) {
        graphChart.dispatchAction({
          type: "restore", 
        });
      }

   
      fetchGraphData(nodeId, "search");
    };

    const updatePieChart = (labelCount: { [key: string]: number }) => {
      const pieData = Object.entries(labelCount).map(([label, count]) => {
    const mappedLabel = label === "0" ? "Fraud" : label === "1" ? "Benign" : label; 
    return {
      value: count,
      name: mappedLabel, 
    };
  }
      );

      const pieChartOption = {
        title: {
          text: "", 
          left: "center",
        },
        tooltip: {
          trigger: "item", 
          formatter: "{b}", 
        },
        series: [
          {
            type: "pie",

            radius: ["40%", "70%"], 
            data: pieData,
            label: {
              show: true,
              formatter: "{b}", 
            },
            itemStyle: {
              borderRadius: 8, 
              borderColor: "#fff",
              borderWidth: 2,
            },
            labelLayout: {
              hideOverlap: true, 
            },
          },
        ],
      };

      if (pieChart) {
        pieChart.setOption(pieChartOption);
      }
    };
    const updatePieChartByPagination = (chartData: any) => {
      const { nodes } = chartData;
     
      const categoryCount = nodes.reduce((acc: { [key: string]: number }, node: any) => {
        const category = node.category;
        acc[category] = (acc[category] || 0) + 1;
        return acc;
      }, {});

     
      const pieData = Object.entries(categoryCount).map(([category, count]) => {
    const mappedCategory = category === "0" ? "Fraud" : category === "1" ? "Benign" : category; 
    return {
      value: count,
      name: mappedCategory, 
    };
  });
  
      const pieChartOption = {
        title: {
          text: "", 
          left: "center",
        },
        tooltip: {
          trigger: "item", 
      
        },
        series: [
          {
            type: "pie",

            radius: ["40%", "70%"], 
            data: pieData,
            label: {
              show: true,
              formatter: "{b}", 
            },
            itemStyle: {
              borderRadius: 8, 
              borderColor: "#fff",
              borderWidth: 2,
            },
            labelLayout: {
              hideOverlap: true, 
            },
          },
        ],
      };

      if (pieChart) {
        pieChart.setOption(pieChartOption);
      }
    };

    const updateGraphChart = (nodes: Array<any>, links: Array<any>, baseSymbolSize: number) => {
      if (!graphChart) return; 

      const option = {
        tooltip: {
          trigger: "item",
          formatter: (params: any) => {
            if (params.dataType === "node") {
           
              return `Node ID: ${params.data.id}<br>Type: ${params.data.value}`;
            } else if (params.dataType === "edge") {
              
              return `Edge: ${params.data.source} --- ${params.data.target}`;
            }
            return "";
          },
        },
        series: [
          {
            type: "graph",
            layout: "force",
            roam: true, 
            data: nodes.map((node) => ({
              ...node,
              symbolSize: Math.max(baseSymbolSize, node.value * 2), 
              itemStyle: {
                color: node.color, 
              },
            })),
            links: links.map((link) => ({
              ...link,
              lineStyle: {
                color: "#aaa",
                width: 1,
                opacity: 0.8,
              },
            })),
            force: {
              edgeLength: [50, 100], 
              repulsion: 500,
            },
            lineStyle: {
              color: "#aaa",
              width: 1,
              opacity: 0.8,
            },
            itemStyle: {
              opacity: 0.9,
            },
            label: {
              show: true,
              position: "inside",
              color: "#fff",
              fontWeight: "bold",
              formatter: "{b}", 
            },
            emphasis: {
              focus: "adjacency",
              lineStyle: {
                width: 2,
                color: "#ff4500", 
              },
            },
          },
        ],
      };

      graphChart.setOption(option); 

     
      graphChart.on("click", function (params: any) {
        if (params.dataType === "node") {
          const nodeId = String(params.data.id).replace(/^Node\s*/i, ""); 

        
          const cleanedInputArray = nodeInput.value
            .split(",") 
            .map((id) => id.trim().replace(/^Node\s*/i, "")) 
            .filter((id) => id !== ""); 

         
          if (!cleanedInputArray.includes(nodeId)) {
            cleanedInputArray.push(nodeId); 
          }

         
          nodeInput.value = cleanedInputArray.join(",");
        } else {
          
          return;
        }
      });
    };

    const initGraphChart = () => {
      if (!graphContainerRef.value) return;

      graphChart = echarts.init(graphContainerRef.value);

      
    };

  
    const pieChartRef = ref<HTMLElement | null>(null);
    const barChartRef = ref<HTMLElement | null>(null);
    let pieChart: echarts.ECharts | null = null;
    let barChart: echarts.ECharts | null = null;

    const initCharts = () => {
  
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value);
    pieChart.setOption({
      title: {
        left: "center",
        textStyle: {
          color: "#333",
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: "item",
        formatter: "{b}:({d}%)", 
      },
      series: [
        {
          type: "pie",
          radius: ["40%", "70%"], 
          avoidLabelOverlap: false,
          label: {
            show: true,
            formatter: "{b}\n{d}%", 
            color: "#555",
            fontSize: 12,
          },
          labelLine: {
            show: true,
            length: 10, 
            length2: 10, 
          },
          data: [], 
          itemStyle: {
            borderRadius: 8, 
            borderColor: "#fff",
            borderWidth: 2,
          },
        },
      ],
    });
  }

  
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value);
    barChart.setOption({
      title: {
        left: "center",
        textStyle: {
          color: "#333",
          fontSize: 16,
        },
      },
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "shadow", 
        },
      },
      grid: {
        left: "10%",
        right: "10%",
        bottom: "10%",
        containLabel: true, 
      },
      xAxis: {
        type: "category",
        data: [], 
        axisTick: {
          alignWithLabel: true,
        },
        axisLine: {
          lineStyle: {
            color: "#ccc",
          },
        },
      },
      yAxis: {
        type: "value",
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false, 
        },
        splitLine: {
          lineStyle: {
            color: "#eee", 
          },
        },
      },
      series: [
        {
          name: "Sales",
          type: "bar",
          barWidth: "40%",
          data: [], 
          itemStyle: {
            color: "#007bff",
            borderRadius: [4, 4, 0, 0], 
          },
        },
      ],
    });
  }
    };

   
    onMounted(() => {
      initGraphChart();
      initCharts();

      const resizeCharts = () => {
        graphChart?.resize();
        pieChart?.resize();
        barChart?.resize();
      };

      window.addEventListener("resize", resizeCharts);
    });

    onUnmounted(() => {
      graphChart?.dispose();
      pieChart?.dispose();
      barChart?.dispose();
    });
    defineExpose({
      updatePieChartByPagination,
    });
    return {
      nodeInput,
      addNodeId,
      isExpanded,
      selectedDataset,
      datasetList,
      datasetDescription,
      searchQuery,
      toggleExpand,
      selectDataset,
      fetchNodeData,
      graphContainerRef,
      pieChartRef,
      barChartRef,
      updatePieChartByPagination,
    };
  },
};
</script>

<style scoped>

.datasets {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom, #f5f7fa, #e4e8ed); 
}


.title {
  background: #0b0b0b;
  color: #ecf0f1;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between; 
  cursor: pointer;
  position: relative;
  border-radius: 8px; 
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
  transition: all 0.3s ease; 
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
  color: #0056b2; 
}

.dropdown-item.active {
  background: #003f82; 
  color: #ffffff; 
  font-weight: bold;
}

/* 力导向图部分 */
.graph-view {
  flex: 11; 
  height: 600px; 
  border: 1px solid #eee;
  margin: 10px;
  display: flex;
  flex-direction: column;
}

.search {
  margin: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.search input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.search button {
  padding: 8px 16px;
  background-color: #013f83;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search button:hover {
  background-color: #0061c8;
}

.graph-container {
  flex: 5;
  height: 600px; 
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fff;
}


.info {
  flex: 0.8;
  max-height: 170px; 
  padding: 14px;
  background: #ffffff;
  border: 1px solid #eee;
  border-radius: 8px;
  margin: 10px; 
  display: flex;
  flex-direction: column;
  align-items: center; 
  justify-content: center; 
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); 

  h3 {
    text-align: center; 
    font-size: 18px; 
    font-weight: bold;
    color: #333; 
    margin-bottom: 10px; 
  }

  .description {
    text-align: center; 
    font-size: 14px; 
    color: #555; 
    line-height: 1.6;
  }
  .node-input {
    margin-top: 10px;
    display: flex;
    gap: 10px;
    align-items: center;
  }

  .node-input input {
    width: 400px; 
    padding: 15px; 
    border: 1px solid #ccc; 
    border-radius: 4px; 
    font-size: 14px; 
  }

  .node-input button {
    padding: 15px 20px;
    background-color: #0e5ea4; 
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  .node-input button:hover {
    background-color: #72b4ee; 
  }
}


.statistics {
  padding: 20px;
  background: #f7f9fc; 
  border-radius: 8px; 
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
  margin: 10px 0; 
}

.statistics-title {
  text-align: center; 
  font-size: 18px; 
  font-weight: bold;
  color: #333; 
  margin-bottom: 20px; 
}

.charts {
  display: flex;
  gap: 20px; 
}

.chart-item {
  flex: 1;
  height: 200px; 
  border-radius: 8px; 
  background: #ffffff; 
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); 
  overflow: hidden; 
  padding: 10px;
}
</style>
