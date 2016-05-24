from steiner import *
import matplotlib.pyplot as plt





def main():
    graph = TOPTGraph()
    graph.add_node_with_position('1', 0.2, 0.3)
    graph.add_node_with_position('2', 0.5, 0.6)
    graph.add_node_with_position('3', 0.1, 0.7)
    graph.add_node_with_position('4', 0.15, 0.9)
    graph.add_node_with_position('5', 0.4, 0.12)
    graph.add_node_with_position('6', 0.3, 0.7)
    graph.add_node_with_position('7', 0.2, 0.3)
    graph.add_node_with_position('8', 0.5, 0.6)
    graph.add_node_with_position('9', 0.1, 0.7)
    graph.add_node_with_position('10', 0.5, 0.9)
    graph.add_node_with_position('11', 0.12, 0.12)
    graph.add_node_with_position('12', 0.8, 0.7)
    graph.add_node_with_position('13', 1.0, 0.3)
    graph.add_node_with_position('14', 1.5, 0.6)
    graph.add_node_with_position('15', 1.2, 0.7)
    graph.add_node_with_position('16', 0.15, 1.2)
    graph.add_node_with_position('17', 0.8, 0.1)
    graph.add_node_with_position('18', 0.31, 1.7)
    # graph.add_euclidian_edge('1', '5')
    # graph.add_euclidian_edge('2', '6')
    # graph.add_euclidian_edge('1', '3')
    # graph.add_euclidian_edge('1', '2')
    # graph.add_euclidian_edge('3', '4')
    # graph.add_euclidian_edge('3', '4')
    # graph.add_euclidian_edge('2', '6')
    # graph.add_euclidian_edge('1', '6')
    # graph.add_euclidian_edge('4', '5')
    # graph.add_euclidian_edge('4', '2')
    # graph.add_euclidian_edge('2', '5')



    pos = nx.get_node_attributes(graph, 'pos')
    nx.draw_networkx(graph, pos=pos)
    plt.show()

    steiner = SteinerTree()
    solution, cost = steiner.find_steiner_tree(graph)
    # steiner_pos = get_positions_from_solution(solution)
    steiner_pos = nx.get_node_attributes(solution, 'pos')
    nx.draw_networkx(solution, steiner_pos)
    plt.show()
    print cost


if __name__ == "__main__":
    main()
