import os
import torch
import json
from flask import Flask, jsonify, request
from torch_geometric.data import Data, DataLoader
from torch.serialization import add_safe_globals
from flask_cors import CORS

add_safe_globals({"Data": Data})

app = Flask(__name__)
CORS(app)  


LABEL_MAP = {
    0: "Fraud",
    1: "Benign",
    2: "Neural networks",
    3: "Probabilistic ",
    4: "Reinforcement",
    5: "Rule",
    6: "Theory",
}

def load_cora_data(data_dir):

    data_path = os.path.join(data_dir, 'Modified_Cora.pt')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} not_found。")

    data = torch.load(data_path)
    print(f"Loaded data type: {type(data)}")

    if isinstance(data, tuple):
        data = data[0]
    elif isinstance(data, dict):
        data = data.get('train', None)
        if data is None:
            raise ValueError("error")

    if not isinstance(data, Data):
        raise ValueError("error")
    if not hasattr(data, 'x') or not hasattr(data, 'edge_index'):
        raise ValueError("error")

    return data


def convert_cora_to_json(data, output_json_path):
    try:

        color_map = [
            "#FF5733",  
            "#33FF57",  
            "#3357FF",  
            "#F39C12",  
            "#8E44AD",  
            "#1ABC9C",  
            "#E74C3C", 
        ]

     
        if hasattr(data, "x") and hasattr(data, "edge_index"):
            graph_data = {
                "description": "Graph data from PyTorch Geometric",
                "nodes": [
                    {
                        "id": f"Node {i}",
                        "value": int(data.y[i]), 
                        "color": color_map[int(data.y[i]) % len(color_map)],  
                    }
                    for i in range(data.x.size(0))
                ],
                "links": [
                    {
                        "source": f"Node {int(source)}",
                        "target": f"Node {int(target)}",
                    }
                    for source, target in data.edge_index.t()
                ],
            }
        else:
            raise ValueError("Unexpected data format in the provided Data object")

     
        with open(output_json_path, "w") as f:
            json.dump(graph_data, f, indent=4)

        print(f"Graph data has been successfully converted and saved to {output_json_path}!")
        return graph_data

    except Exception as e:
        print(f"An error occurred during data conversion: {e}")
        return None


@app.route('/api/graph-data/<dataset_id>', methods=['GET'])
def get_graph_data(dataset_id):

    dataset_dir = f"./datasets/Cora/"  
    output_json_path = f"./datasets/Cora/{dataset_id}_graph.json"

    try:
       
        cora_data = load_cora_data(dataset_dir)
      
        graph_data = convert_cora_to_json(cora_data, output_json_path)

        if graph_data:
            return jsonify(graph_data)
        else:
            return jsonify({"error": f"Failed to process the dataset '{dataset_id}'"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/edge-statistics/<int:graph_id>', methods=['GET'])
def fetch_edge_statistics(graph_id):
    dataset_dir = "./datasets/Cora/"
    try:
  
        cora_data = load_cora_data(dataset_dir)

     
        edge_statistics = [[0 for _ in range(6)] for _ in range(6)]

        
        num_nodes = len(cora_data.y)

     
        for source, target in cora_data.edge_index.t():
            source, target = int(source), int(target)

    
            if source >= num_nodes or target >= num_nodes:
                print(f"Invalid edge index: source={source}, target={target}")
                continue


            source_type = int(cora_data.y[source])
            target_type = int(cora_data.y[target])
            if source_type >= 6 or target_type >= 6:
                print(f"Invalid node type: source_type={source_type}, target_type={target_type}")
                continue

    
            edge_statistics[source_type][target_type] += 1


        return jsonify({"edge_statistics": edge_statistics})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/node-data/<int:node_id>', methods=['GET'])
def fetch_node_data(node_id):
    dataset_dir = "./datasets/Cora/"
    try:

        color_map = [
            "#FF5733", "#33FF57", "#3357FF", "#F39C12", "#8E44AD", "#1ABC9C", "#E74C3C",
        ]

        cora_data = load_cora_data(dataset_dir)


        if node_id < 0 or node_id >= cora_data.x.size(0):
            return jsonify({"error": f"{node_id}  not found"}), 404


        def find_neighbors(node, max_hops=3):
            visited = set() 
            current_level = {node}  
            all_neighbors = set()  

            for _ in range(max_hops):
                next_level = set()
                for n in current_level:
                    if n in visited:
                        continue
                    visited.add(n)
                    all_neighbors.add(n)
            
                    for source, target in cora_data.edge_index.t():
                        source, target = int(source), int(target)
                        if source == n and target not in visited:
                            next_level.add(target)
                        elif target == n and source not in visited:
                            next_level.add(source)
                current_level = next_level
                if not current_level:  
                    break

            return all_neighbors


        neighbors = find_neighbors(node_id, max_hops=3)

       
        links = []
        for source, target in cora_data.edge_index.t():
            source, target = int(source), int(target)
            if source in neighbors and target in neighbors:
                links.append({"source": f"Node {source}", "target": f"Node {target}"})

  
        nodes = []
        label_count = {}  
        for neighbor in neighbors:
            label = LABEL_MAP[int(cora_data.y[neighbor])] 
            color = color_map[int(cora_data.y[neighbor]) % len(color_map)]
            nodes.append({
                "id": f"Node {neighbor}",
                "value": int(cora_data.y[neighbor]),
                "features": cora_data.x[neighbor].tolist(),
                "color": color,
            })
     
            if label not in label_count:
                label_count[label] = 0
            label_count[label] += 1

   
        print(f"Node ID: {node_id}, Label Count: {label_count}, Neighbors: {neighbors}")

 
        return jsonify({"nodes": nodes, "links": links, "label_count": label_count})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


    
@app.route('/api/graph-data/<int:graph_id>', methods=['GET'])
def fetch_graph_data(graph_id):
    dataset_dir = "./datasets/Cora/"
    try:
    
        color_map = [
            "#FF5733", "#33FF57", "#3357FF", "#F39C12", "#8E44AD", "#1ABC9C", "#E74C3C",
        ]

   
        cora_data = load_cora_data(dataset_dir)


        nodes = []
        label_count = {}  

        for node_id in range(cora_data.x.size(0)):
            label = LABEL_MAP[int(cora_data.y[node_id])]  
            color = color_map[int(cora_data.y[node_id]) % len(color_map)]
            nodes.append({
                "id": f"Node {node_id}",
                "value": int(cora_data.y[node_id]),
                "features": cora_data.x[node_id].tolist(),
                "color": color,
            })
        
            if label not in label_count:
                label_count[label] = 0
            label_count[label] += 1

    
        links = []
        for source, target in cora_data.edge_index.t():
            links.append({"source": f"Node {int(source)}", "target": f"Node {int(target)}"})

 
        print(f"Graph ID: {graph_id}, Label Count: {label_count}")

    
        return jsonify({"nodes": nodes, "links": links, "label_count": label_count})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)
