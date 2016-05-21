from steiner import *
import matplotlib.pyplot as plt


def main():
    graph = TOPTGraph()
    graph.add_node_with_position('1', 0.2, 0.3)
    graph.add_node_with_position('2', 0.5, 0.6)
    graph.add_node_with_position('3', 0.1, 0.7)
    # graph.add_node_with_position('4', 0.15, 0.9)
    # graph.add_node_with_position('5', 0.4, 0.12)
    # graph.add_node_with_position('6', 0.3, 0.7)
    # graph.add_euclidian_edge('1', '5')
    # graph.add_euclidian_edge('2', '6')
    graph.add_euclidian_edge('1', '3')
    graph.add_euclidian_edge('1', '2')
    # graph.add_euclidian_edge('3', '4')
    # graph.add_euclidian_edge('2', '6')
    # graph.add_euclidian_edge('1', '6')
    # graph.add_euclidian_edge('4', '5')
    # graph.add_euclidian_edge('4', '2')
    # graph.add_euclidian_edge('2', '5')



    weights = nx.get_edge_attributes(graph, 'weight')

    mst = nx.minimum_spanning_tree(graph)

    hanan_points = graph.get_hanan_points()

    terminals = get_power_set(hanan_points)
    copygraph = graph.copy()
    copygraph.apply_terminal_points(terminals[12])
    pos = nx.get_node_attributes(copygraph, 'pos')
    nx.draw_networkx(copygraph, pos=pos)
    plt.show()
    mst = nx.minimum_spanning_tree(copygraph)
    edges = mst.edges(data=True)
    cost = 0

    nx.draw_networkx(mst, pos=pos)

    plt.show()


if __name__ == "__main__":
    main()
