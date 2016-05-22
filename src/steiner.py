import networkx as nx
import math
import itertools as iter
import random as rnd


class TOPTGraph(nx.Graph):
    def add_node_with_position(self, node_number, x, y):
        self.add_node(node_number, pos=(x, y))

    def add_euclidian_edge(self, start, end):
        start_position = nx.get_node_attributes(self, 'pos')[start]
        end_position = nx.get_node_attributes(self, 'pos')[end]
        weight = self.euc_2d(start_position[0], start_position[1],
                             end_position[0], end_position[1])
        self.add_edge(start, end, weight=weight)

    def get_hanan_points(self):
        hanan_points = []
        node_positions = nx.get_node_attributes(self, 'pos').values()
        for i in xrange(0, len(node_positions)):
            for j in xrange(i, len(node_positions)):
                if (i != j):
                    point1 = (
                        'T' + str(i) + str(j), {'pos': (node_positions[i][0], node_positions[j][1]), 'color': 'green'})
                    point2 = (
                        'T' + str(j) + str(i), {'pos': (node_positions[j][0], node_positions[i][1]), 'color': 'green'})
                    hanan_points.append(point1)
                    hanan_points.append(point2)

        return hanan_points

    def apply_terminal_points(self, terminals):

        for terminal in terminals:
            terminal_id = terminal[0]
            position = terminal[1]['pos']
            self.add_node(terminal_id, pos=position)
            for node in self.nodes():
                if (node != terminal_id):
                    self.add_euclidian_edge(node, terminal_id)

    def euc_2d(self, x1, y1, x2, y2):
        weight = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        return weight


class SteinerTree:
    def __init__(self, T_max=1.0, T_min=0.00001, cooling_factor=0.9, number_of_iterations=100):
        self.T_max = T_max
        self.T_min = T_min
        self.cooling_factor = cooling_factor
        self.number_of_iterations = number_of_iterations

    def find_steiner_tree(self, input_graph):
        possible_solutions = self.__get_set_of_possible_solutions(input_graph)

        solution = self.__get_random_solution(possible_solutions)
        cost = self.__get_cost(solution)

        current_temperature = self.T_max
        while current_temperature > self.T_min:
            new_solution = self.__get_random_solution(possible_solutions)
            new_cost = self.__get_cost(new_solution)
            aceptance_point = math.exp((cost - new_cost) / current_temperature)
            if aceptance_point > rnd.random():
                solution = new_solution
                cost = new_cost
            current_temperature = current_temperature * self.cooling_factor
        return solution, cost

    def __get_set_of_possible_solutions(self, input_graph):
        hanan_points = input_graph.get_hanan_points()
        hanan_sets = get_power_set(hanan_points)
        possible_solutions = []
        for set in hanan_sets:
            copied_graph = input_graph.copy()
            copied_graph.apply_terminal_points(set)
            # mst = nx.minimum_spanning_tree(copied_graph)
            possible_solutions.append(copied_graph)
        rnd.shuffle(possible_solutions)
        return possible_solutions

    def __get_cost(self, mst):
        edges = mst.edges(data=True)
        cost = 0
        for edge in edges:
            cost += edge[2]['weight']
        return cost

    def __get_random_solution(self, solutions):
        length = len(solutions)
        random = rnd.choice(xrange(0, length))
        return nx.minimum_spanning_tree(solutions[random])


def get_power_set(iterable):
    s = list(iterable)
    return list(iter.chain.from_iterable(iter.combinations(s, r) for r in range(len(s) + 1)))
