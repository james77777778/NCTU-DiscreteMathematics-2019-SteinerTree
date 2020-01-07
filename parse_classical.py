import os
import glob
import networkx as nx
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.algorithms.tree import minimum_spanning_tree


dataset_name = "I640"
data_path = os.path.join("data", dataset_name)
dataset_path = glob.glob(os.path.join(data_path, "*.stp"))
dataset_path = sorted(dataset_path)
save_path = os.path.join("data", dataset_name, "processed_graph")
os.makedirs(save_path, exist_ok=True)

for target_path in dataset_path:
    G = nx.Graph()
    terminals = []
    edges = []
    filename = os.path.basename(target_path)
    with open(target_path, 'r') as tar:
        lines = tar.read().splitlines()
        for line in lines:
            if line[:2] == "E ":
                parsed_line = line.split()
                a = int(parsed_line[1])
                b = int(parsed_line[2])
                w = float(parsed_line[3])
                G.add_edge(a, b, weight=w)
                edges.append((a, b, w))
            elif line[:2] == "T ":
                parsed_line = line.split()
                t = int(parsed_line[1])
                terminals.append(t)

    steiner_tree_ = steiner_tree(
        G, terminals, weight="weight"
    )
    minimum_spanning_tree_ = minimum_spanning_tree(G, weight='weight')
    # nx.draw(steiner_tree_, with_labels=True)
    print(os.path.basename(target_path) + ": " +
          'n=' + str(len(G.nodes())) + ' ' +
          'e=' + str(len(G.edges())) + ' ' +
          't=' + str(len(terminals)) + ' ' +
          str(steiner_tree_.size(weight="weight")))
    # save graph
    nx.write_weighted_edgelist(G, os.path.join(save_path, filename))
    # save terminals
    with open(os.path.join(save_path, filename+".terminals"), 'w') as f:
        for t in terminals:
            f.write(str(t)+'\n')
