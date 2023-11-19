import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout


def create_dekiert_graph(w: str, D: nx.DiGraph) -> nx.DiGraph:
    labels = D.nodes
    label_to_nodes_mapping: dict[str, list[int]] = {label: [] for label in labels}
    nodes_to_labels_mapping: dict[int, str] = {}
    dekiert_graph = nx.DiGraph()
    node_id_incrementer = 0

    #  Constructing not optimised Graph with all the possible paths
    for action in w:
        dekiert_graph.add_node(node_id_incrementer)
        for in_node_label in set(in_node for in_node, _ in D.in_edges(action)):
            for node_id in label_to_nodes_mapping[in_node_label]:
                dekiert_graph.add_edge(node_id, node_id_incrementer)
        label_to_nodes_mapping[action].append(node_id_incrementer)
        nodes_to_labels_mapping[node_id_incrementer] = action
        node_id_incrementer += 1
    # Optimization - removing relevant paths and leaving only "the longest" ones
    for v in range(node_id_incrementer):
        for w in range(v + 1, node_id_incrementer):
            for k in range(w + 1, node_id_incrementer):
                if dekiert_graph.has_edge(v, k):
                    if dekiert_graph.has_edge(v, w) and dekiert_graph.has_edge(w, k):
                        dekiert_graph.remove_edge(v, k)

    # Revert label to original one
    nx.set_node_attributes(dekiert_graph, nodes_to_labels_mapping, "label")
    draw_graph(dekiert_graph, nodes_to_labels_mapping)
    return dekiert_graph


def draw_graph(G: nx.DiGraph, labels: dict[int, str]) -> None:
    pos = graphviz_layout(G, prog="dot")
    nx.draw(
        G,
        pos,
        with_labels=True,
        labels=labels,
        font_weight="bold",
        node_size=400,
        node_color="#FF7F50",
        edge_color="#1F78B4",
        arrowsize=20,
        font_color="black",
        font_size=10,
        linewidths=1,
        width=2,
    )
    plt.show()
