import networkx as nx
import math
import itertools as iter
import random as rnd
import re

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

    def get_pseudofermat_points(self, limit):
        pseudofermat_points = []
        node_positions = nx.get_node_attributes(self, 'pos').values()
        combinations = list(iter.combinations(node_positions, 3))
        node_count = limit if limit < len(combinations) else len(combinations)

        sample = rnd.sample(combinations, node_count)
        for comb in sample:
            counted_point = self.__count_pseudofermat_point_position(comb)
            pseudofermat_points.append(counted_point)
        return pseudofermat_points

    def __count_pseudofermat_point_position(self, combination):
        x = 0
        y = 0
        for point in combination:
            x += point[0]
            y += point[1]
        x /= len(combination)
        y /= len(combination)

        pseudofermat_point = (
            'F(' + '%.2f' % x + ',' + '%.2f' % y + ')', {'pos': (x, y), 'color': 'blue'})
        return pseudofermat_point

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

        solution, solution_graph = self.__get_random_solution(possible_solutions)
        best_solution, best_solution_graph = self.__simulate_annealing(solution,
                                                                       solution_graph,
                                                                       self.__get_random_solution,
                                                                       rnd.random,
                                                                       possible_solutions)

        cost = self.__get_cost(best_solution)
        best_solution_fermat_points = self.__get_fermat_points_from_graph(best_solution_graph)
        print 'First annealing: ' + str(len(best_solution_fermat_points)) + ' pseudofermat points. Cost: ' + str(cost)

        best_solution, best_solution_graph = self.__simulate_annealing(best_solution,
                                                                       best_solution_graph,
                                                                       self.__remove_random_fermat_point,
                                                                       self.__get_acceptance_point_for_removing_fermats,
                                                                       best_solution_graph)
        cost = self.__get_cost(best_solution)

        best_solution_fermat_points = self.__get_fermat_points_from_graph(best_solution)
        print 'Second annealing: ' + str(len(best_solution_fermat_points)) + ' pseudofermat points. Cost: ' + str(cost)
        best_solution, cost = self.__remove_hanging_fermats(best_solution)
        best_solution, cost = self.__remove_fermats_with_two_connections(best_solution)
        print 'Last cost: ' + str(len(best_solution_fermat_points)) + ' pseudofermat points. Cost: ' + str(cost)
        return best_solution, cost

    def __simulate_annealing(self,
                             start_solution,
                             start_solution_graph,
                             solution_provider_function,
                             acceptance_point_function,
                             *solution_provider_args):

        best_solution = start_solution
        best_solution_graph = start_solution_graph
        cost = self.__get_cost(start_solution)

        current_temperature = self.T_max
        while current_temperature > self.T_min:
            new_solution, new_solution_graph = solution_provider_function(*solution_provider_args)
            new_cost = self.__get_cost(new_solution)
            cost_diff = cost - new_cost
            acceptance_point = 0
            try:
                acceptance_point = math.exp((cost_diff) / current_temperature)
            except OverflowError:
                print 'cost - new_cost: ' + str(cost_diff) + ', current_temp: ' + str(current_temperature)
            if acceptance_point > acceptance_point_function():
                best_solution = new_solution
                best_solution_graph = new_solution_graph
                cost = new_cost
            current_temperature = current_temperature * self.cooling_factor

        return best_solution, best_solution_graph

    def __get_acceptance_point_for_removing_fermats(self):
        return rnd.uniform(1.75, 3)

    def __remove_random_fermat_point(self, input_graph):
        fermat_points = self.__get_fermat_points_from_graph(input_graph)
        graph = input_graph.copy()
        points_count = len(fermat_points)
        if points_count > 1:
            point_to_delete = fermat_points[rnd.randint(0, points_count-1)]
            graph.remove_node(point_to_delete)
            if nx.is_connected(graph):
                return nx.minimum_spanning_tree(graph), graph
        return nx.minimum_spanning_tree(input_graph), input_graph

    def __get_fermat_points_from_graph(self, graph):
        points = []
        for node_name in graph.nodes():
            if re.search('F\(', node_name):
                points.append(node_name)
        return points

    def __get_set_of_possible_solutions(self, input_graph):
        # added_points_sets = self.__get_hanan_solution_sets(input_graph)
        added_points_sets = self.__get_fermat_solution_sets(input_graph, 200)
        possible_solutions = []
        for set in added_points_sets:
            copied_graph = input_graph.copy()
            copied_graph.apply_terminal_points(set)
            # mst = nx.minimum_spanning_tree(copied_graph)
            possible_solutions.append(copied_graph)
        rnd.shuffle(possible_solutions)
        return possible_solutions

    def __get_hanan_solution_sets(self, input_graph):
        hanan_points = input_graph.get_hanan_points()
        added_points_sets = get_power_set(hanan_points)
        return added_points_sets

    def __get_fermat_solution_sets(self, input_graph, limit):
        pseudofermat_points = input_graph.get_pseudofermat_points(limit)
        added_points_sets = get_fermat_set(pseudofermat_points, len(input_graph.nodes())-2, 500)
        return added_points_sets

    def __get_cost(self, mst):
        edges = mst.edges(data=True)
        cost = 0
        for edge in edges:
            cost += edge[2]['weight']
        return cost

    def __remove_hanging_fermats(self, graph):
        nodes_to_remove = []

        for edge in graph.edge.iteritems():
            if re.search('F\(', edge[0]) and len(edge[1]) < 2:
                nodes_to_remove.append(edge[0])

        print nodes_to_remove

        for node in nodes_to_remove:
            graph.remove_node(node)
        return graph, self.__get_cost(graph)

    def __remove_fermats_with_two_connections(self, graph):
        while True:
            node_to_remove, edge_to_insert = self.__find_replacement_edge(graph)
            if node_to_remove is None or edge_to_insert is None:
                break
            else:
                graph.remove_node(node_to_remove)
                start_position = nx.get_node_attributes(graph, 'pos')[edge_to_insert[0]]
                end_position = nx.get_node_attributes(graph, 'pos')[edge_to_insert[1]]
                weight = self.euc_2d(start_position[0], start_position[1], end_position[0], end_position[1])
                graph.add_edge(edge_to_insert[0], edge_to_insert[1], weight=weight)

        return graph, self.__get_cost(graph)

    def __find_replacement_edge(self, graph):
        for edge in graph.edge.iteritems():
            print edge
            if re.search('F\(', edge[0]) and len(edge[1]) == 2:
                return edge[0], (edge[1].keys()[0], edge[1].keys()[1])
        return None, None

    def __get_random_solution(self, solutions):
        length = len(solutions)
        random = rnd.choice(xrange(0, length))
        return nx.minimum_spanning_tree(solutions[random]), solutions[random]

    def euc_2d(self, x1, y1, x2, y2):
        weight = math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        return weight


def get_power_set(iterable):
    s = list(iterable)
    return list(iter.chain.from_iterable(iter.combinations(s, r) for r in range(len(s) + 1)))


def get_fermat_set(iterable, set_size, returned_sets_count):
    fermat_sets = []
    while len(fermat_sets) < returned_sets_count:
        comb = rnd.sample(iterable, set_size)
        fermat_sets.append(comb)

    return fermat_sets