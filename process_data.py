import pandas as pd
import math

def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Read the raw file
with open('usa.txt', 'r') as f:
    lines = f.readlines()

# Parse Header
header = lines[0].split()
num_vertices = int(header[0])
num_edges = int(header[1])

print(f"Processing {num_vertices} vertices and {num_edges} edges...")

# 1. Process Vertices (Intersections)
# Lines 1 to num_vertices + 1 contain node data
nodes = []
# Store coordinates in a dict for fast lookup when calculating edge distances
node_coords = {} 

for i in range(1, num_vertices + 1):
    parts = lines[i].split()
    node_id = int(parts[0])
    x = float(parts[1])
    y = float(parts[2])
    
    nodes.append({"id": node_id, "x": x, "y": y})
    node_coords[node_id] = (x, y)

# Save Nodes to CSV
df_nodes = pd.DataFrame(nodes)
df_nodes.to_csv('intersections.csv', index=False)
print("Created intersections.csv")

# 2. Process Edges (Roads)
# Lines after the nodes contain edges
edges = []
start_line_edges = num_vertices + 1

for i in range(start_line_edges, len(lines)):
    parts = lines[i].split()
    if len(parts) < 2: 
        continue # Skip empty lines
    
    source = int(parts[0])
    target = int(parts[1])
    
    # Calculate Euclidean distance
    if source in node_coords and target in node_coords:
        x1, y1 = node_coords[source]
        x2, y2 = node_coords[target]
        dist = calculate_distance(x1, y1, x2, y2)
        
        edges.append({"source": source, "target": target, "distance": dist})

# Save Edges to CSV
df_edges = pd.DataFrame(edges)
df_edges.to_csv('roads.csv', index=False)
print("Created roads.csv")