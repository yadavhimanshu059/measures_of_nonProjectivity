""" treegen """
from math import log, exp
import random
import itertools as it
import functools
import operator
import copy
import bisect

import networkx as nx

from rfutils import the_only, partition, flatmap
from rfutils.nondet import nondet_map

import depgraph


def endpoints_of(tree):
    return [n for n in sorted(tree.nodes()) if tree.degree(n) == 1]

def pruefer_code_for(tree):
    # from https://www.math.upenn.edu/~wilf/website/CombinatorialAlgorithms.pdf
    # Ch. 28, pp. 267--268
    # This implementation closely follows this reference:
    #@inbook{nijenhuis1978labeled,
    #  title="Combinatorial Algorithms",
    #  chapter="28",
    #  edition = "2",
    #  pages="267--274"
    #  author = "Albert Nijenhuis and Herbert S. Wilf",
    #  publisher = "Academic Press",
    #  address = "New York",
    #  series = "Computer Science and Applied Mathematics",
    #  editor = "Werner Rheinboldt",
    #  year = "1978"
    # }    
    tree = copy.deepcopy(tree)
    while len(tree.edges()) > 1:
        x = min(endpoints_of(tree))
        _, a = the_only(tree.edges(x))
        yield a
        tree.remove_edge(x, a)

def tree_edges_from_pruefer_code(code):
    # https://www.math.upenn.edu/~wilf/website/CombinatorialAlgorithms.pdf
    # Ch. 28
    # This is O(n^2); Gottlieb et al. (2001) say there is an O(nlogn)
    # decoding algorithm using heaps; I'll implement that if this turns
    # out to be a bottleneck.
    # Could use sympy.combinatorics.prufer.Prufer(code).tree_repr, but that's 2x slower
    code = list(code)
    l1 = set(range(len(code) + 2))
    while code and len(l1) > 2:
        x = min(l1.difference(code))
        yield (x, code[0])
        l1.remove(x)
        code.pop(0)
    assert len(l1) == 2
    yield tuple(l1) # two things left in l1; make those the final edge

def tree_from_pruefer_code(code):
    edges = tree_edges_from_pruefer_code(code)
    return nx.Graph(edges)

def test_pruefer_code():
    edges = {(2, 0), (0, 1), (2, 3)}
    tree = nx.Graph(list(edges))
    code = pruefer_code_for(tree)
    assert list(code) == [0, 2]

def test_pruefer_code_roundtrip():
    edges = {(2, 0), (0, 1), (2, 3)}
    tree = nx.Graph(list(edges))    
    new_tree = tree_from_pruefer_code(pruefer_code_for(tree))
    assert set(map(frozenset, new_tree.edges())) == set(map(frozenset, edges))

def all_pruefer_codes(n):
    return it.product(range(n), repeat=n-2)

def random_pruefer_code(n):
    return [random.choice(range(n)) for _ in range(n-2)]

def random_undirected_tree(n):
    assert n > 1
    return tree_from_pruefer_code(random_pruefer_code(n))

def random_directed_tree(n):
    assert n > 1
    return random_directed_tree_from(random_undirected_tree(n))

def all_undirected_trees(n):
    """ Generate all labeled undirected trees with n vertices. 
    There are n ^ (n - 2) such trees. Only works for n > 1. """
    # idea: generate all Pruefer codes of length n - 2,
    # https://en.wikipedia.org/wiki/Pr%C3%BCfer_sequence
    # then convert them to undirected trees.    
    assert n > 1
    return map(tree_from_pruefer_code, all_pruefer_codes(n))

def test_all_undirected_trees():
    # test we generate the right number
    def count(xs):
        result = 0
        for x in xs:
            result += 1
        return result
    def test_count_equals_cayley(n):
        assert count(all_undirected_trees(n)) == n ** (n - 2)
    test_count_equals_cayley(2)
    test_count_equals_cayley(5)

    # test they are unique
    n = 4
    ts = [
        (
            frozenset(t.nodes()),
            frozenset(map(frozenset, t.edges())),
        )
        for t in all_undirected_trees(n)
    ]
    assert len(ts) == len(set(ts))
    
    # test correct number of nodes
    assert all(len(nodes) == n for nodes, edges in ts)

    # test tree structure
    nodes_in_edges = {
        n
        for nodes, edges in ts
        for edge in edges
        for n in edge
    }
    for nodes, edges in ts:
        assert all(n in nodes_in_edges for n in nodes)

def with_nodes(g, nodes):
    g2 = type(g)()
    g2.add_nodes_from(g.nodes())
    g2.add_edges_from(g.edges())
    g2.add_nodes_from(nodes)
    return g2    

def with_edges(g, edges):
    g2 = type(g)()
    g2.add_nodes_from(g.nodes())
    g2.add_edges_from(g.edges())
    g2.add_edges_from(edges)
    return g2

def nondecreasing_sequences_adding_to(n):
    """ Yield all nondecreasing sequences of integers which add to n. """
    def seqs_with_max(n, max_k):
        if n == 0:
            yield []
        else:
            for m in range(1, min(n, max_k) + 1):
                for seq in seqs_with_max(n - m, m):
                    yield [m] + seq
    return seqs_with_max(n, n)

def all_undirected_forest_components(n):
    """ Enumerate undirected forests with n nodes. """
    # First get all the nondecreasing sequences that add to n
    sequences = nondecreasing_sequences_adding_to(n)

    # Now for each sequence get all the forests
    return flatmap(functools.partial(nondet_map, all_undirected_trees), sequences)

def all_undirected_forests(n):
    return map(forest_of_trees, all_undirected_forest_components(n))

def all_directed_forest_components(n):
    forests = all_undirected_forest_components(n)
    return flatmap(functools.partial(nondet_map, directed_trees), forests)

def all_directed_forests(n):
    forests = all_directed_forest_components(n)
    return map(forest_of_trees, forests)

def forest_of_trees(trees):
    """ Combine an iterable of trees into a forest graph. """
    max_node = 0
    first_time = True
    for tree in trees:
        if first_time:
            forest = type(tree)()
            first_time = False
        edges = [(h+max_node, d+max_node) for h, d in tree.edges()]
        forest.add_edges_from(edges)
        max_node += max(tree.nodes())
    return forest

def directed_trees(undirected_tree):
    """ Given an undirected tree, yield all possible rooted directed trees. """
    edges = undirected_tree.edges()
    for node in undirected_tree.nodes():
        arcs = rooted_at(edges, node)
        yield nx.DiGraph(arcs)

def random_directed_tree_from(undirected_tree):
    edges = undirected_tree.edges()
    root = random.choice(undirected_tree.nodes())
    arcs = rooted_at(edges, root)
    return nx.DiGraph(arcs)

def all_directed_trees(n):
    """  Generate all rooted directed trees with n nodes. 
    There are n ^ (n - 1) such trees. """
    return flatmap(directed_trees, all_undirected_trees(n))

def tree_has_consistent_head_direction(cmp, directed_tree):
    return all(it.starmap(cmp, directed_tree.edges_iter()))

tree_is_head_final = functools.partial(tree_has_consistent_head_direction, operator.gt)
tree_is_head_initial = functools.partial(tree_has_consistent_head_direction, operator.lt)

def tree_is_partially_head_final(directed_tree, p):
    num_edges = directed_tree.size()
    desired_num_head_final = round(num_edges * p)
    num_head_final = sum(d < h for h, d in directed_tree.edges_iter())
    return num_head_final == desired_num_head_final

def all_projective_trees(n):
    return filter(depgraph.is_projective, all_undirected_trees(n))

def all_head_initial_trees(n):
    return filter(
        tree_is_head_initial,
        flatmap(directed_trees, all_undirected_trees(n))
    )

def all_head_final_trees(n):
    return filter(
        tree_is_head_final,
        flatmap(directed_trees, all_undirected_trees(n))
    )

def pair_element(pair, x):
    assert x in pair
    one, two = pair
    if one == x:
        return one, two
    else:
        return two, one

def only_one(xs):
    """ Return whether exactly one element of xs is truthy. """
    xs_iter = filter(None, iter(xs))
    for x in xs_iter: # take the first thing that is truthy,
        return not any(xs_iter) # return whether there are none after that one.
    return False # case where none were truthy

def at_most(n, xs):
    """ Return whether at most n elements of xs are truthy. """
    so_far = 0
    for x in filter(None, xs):
        so_far += 1
        if so_far > n:
            return False
    return True

def rooted_at(edges, node):
    """ Given edges of an undirected tree and some node, yield the arcs of a directed
    tree with the same structure rooted at that node. """
    relevant_edges, irrelevant_edges = partition(lambda e: node in e, edges)
    irrelevant_edges = list(irrelevant_edges)
    for edge in relevant_edges:
        h, d = pair_element(edge, node)
        yield (h, d)
        for cont in rooted_at(irrelevant_edges, d):
            yield cont

def num_directed_forests_with_components(n, k):
    """ Number of possible directed forests with n nodes and k components. """
    # from https://math.berkeley.edu/~mhaiman/math172-spring10/matrixtree.pdf
    return choose(n - 1, k - 1) * n ** (n - k)

def num_directed_forests(n):
    """ Number of possible directed forests with n nodes. """
    return sum(
        num_directed_forests_with_components(n, k)
        for k in range(1, n + 1)
    )

def test_rooted_at():
    edges = [(1, 2), (1, 3), (3, 4)]
    assert set(rooted_at(edges, 1)) == set(edges)
    assert set(rooted_at(edges, 2)) == {(2, 1), (1, 3), (3, 4)}
    assert set(rooted_at(edges, 3)) == {(3, 1), (1, 2), (3, 4)}
    assert set(rooted_at(edges, 4)) == {(4, 3), (3, 1), (1, 2)}

if __name__ == '__main__':
    import nose
    nose.runmodule()
