import random
from collections import defaultdict, deque, Counter

import networkx as nx
import cliqs.mindep
import rfutils
import rfutils.flatten

import treegen
import depgraph

def random_directed_rooted_tree(n):
    t = treegen.random_directed_tree(n-1)
    nx.relabel_nodes(t, dict(zip(range(n-1), range(1, n))), copy=False) # shift all nodes to n+1
    t.add_edge(0, depgraph.root_of(t)) # add a root at 0
    assert len(t) == n
    return t

def random_directed_tree_with_crossings_slow(n, k):
    """ Simple generate-and-test solution. Intractable """
    assert n > 2
    assert k >= 0
    while True:
        t = random_directed_rooted_tree(n)
        if depgraph.num_crossings_in(t) == k:
            return t

def random_projective_linearization(t):
    _, order = cliqs.mindep.randlin_projective(t)
    # Root will always come out at the left or right edge of the tree
    if order[-1] == 0: # in case it comes out on the right, move it to the left
        order = deque(order)
        order.rotate()
    linearization = {j:i for i,j in enumerate(order)}
    return nx.relabel_nodes(t, linearization)

def random_directed_tree_with_crossings(n, k):
    assert n > 2
    assert k >= 0
    while True:
        t = random_directed_rooted_tree(n)
        p = random_projective_linearization(t)
        new_t = add_k_random_crossings(p, k)
        if new_t is None:
            continue # None signals that there are no trees with this structure with k crossings
        else:
            return new_t

def move_subsequence(s, n_min, n_max, m):
    assert not n_min <= m <= n_max
    # Running example: [0, 1, 2, 3, 4, 5, 6, 7], 4, 6, 1
    s = list(s)[:]
    k = n_max - n_min # 2
    block = list(range(n_min, n_max+1)) # [4,5,6]
    for _ in range(k+1):
        del s[n_min] # s is now [0,1,2,3,7]
    s.insert(m-k*(m>n_max), block)
    return rfutils.flatten.flatten(s) # result should be [0,4,5,6,1,2,3,7]

def test_move_subsequence():
    s = range(8)
    assert move_subsequence(s, 4, 6, 1) == [0,4,5,6,1,2,3,7]
    # [0,1,[2,3,4],5,6,7] -> # [0,1,5,6,2,3,4,7]
    assert move_subsequence(s, 2, 4, 6) == [0,1,5,6,2,3,4,7]

def move_tree_subsequence(t, n_min, n_max, m):
    if n_min <= m <= n_max:
        return None
    else:
        new_order = move_subsequence(range(len(t)), n_min, n_max, m)
        mapping = {j:i for i,j in enumerate(new_order)}
        return nx.relabel_nodes(t, mapping)

# move_block : Tree x Node x Int -> Maybe Tree
def move_block(t, n, m):
    # Move the nth node and all its descendents in a block in t to position m
    blocks = depgraph.blocks_of(t, n)
    # Which block actually contains n? Grab that one.
    block = [block for block in blocks if n in block][0]
    min_block = min(block) # left edge inside the block
    max_block = max(block) # right edge inside the block
    if min_block <= m <= max_block: # Nothing happens in these cases
        return None
    new_order = move_subsequence(range(len(t)), min_block, max_block, m)
    mapping = {j:i for i,j in enumerate(new_order)}
    return nx.relabel_nodes(t, mapping)

def test_move_block():
    E = depgraph.EquableDiGraph
    t = nx.DiGraph([(0, 1), (1, 2), (2, 5), (5, 4), (5, 3), (5, 6), (6, 7)])
    t2 = move_block(t, 5, 1)
    assert E(t2) == E(nx.DiGraph([(0, 6), (6, 7), (7, 3), (3, 2), (3, 1), (3, 4), (4, 5)]))

    t3 = move_block(t2, 5, 6)
    assert E(t3) == E(nx.DiGraph([(0, 5), (5, 7), (7, 3), (3, 1), (3, 2), (3, 4), (4, 6)]))

    t4 = move_block(t2, 2, 7)
    assert E(t4) == E(nx.DiGraph([(0, 5), (5, 6), (6, 2), (2, 7), (2, 1), (2, 3), (3, 4)]))

    t5 = nx.DiGraph([(4, 3), (6, 4), (6, 5), (5, 2), (2, 1), (0, 6)])
    # the block of 2 is [1,2]: [0,[1,2],3,4,5,6]
    t6 = move_block(t5, 2, 5)
    # new order should be [0,3,4,5,1,2,6]
    assert E(t6) == E(nx.DiGraph([(2, 1), (6, 2), (6, 3), (3, 5), (5, 4), (0, 6)]))

# add_k_random_crossings : Tree x Int -> Maybe Tree
def add_k_random_crossings(t, k):        
    while depgraph.num_crossings_in(t) < k:
        t = randomly_tangle_up_to(t, k)
        if t is None:
            return None
    return t
                
def shuffled(xs):
    xs = list(xs)[:]
    random.shuffle(xs)
    return xs

# randomly_tangle_up_to : Tree x Int -> Maybe Tree 
def randomly_tangle_up_to(t, k):
    old_num_crossings = depgraph.num_crossings_in(t)
    nodes = shuffled(t.nodes())
    for n_min in nodes:
        if n_min:
            for n_max in nodes:
                if n_min < n_max:
                    for m in nodes:
                        if m:
                            new_t = move_tree_subsequence(t, n_min, n_max, m)
                            if new_t is not None:
                                new_num_crossings = depgraph.num_crossings_in(new_t)
                                if old_num_crossings < new_num_crossings <= k:
                                    return new_t
    else:
        return None

def projection_degree(t):
    return max(v for k, v in nx.shortest_path_length(t, depgraph.root_of(t)).items())

def arity(t):
    return max(len(v) for k, v in t.edge.items())

def structural_distribution(method, n_range, k_range, num_samples):
    """ What is the empirical joint distribution of n, k, and tree structures in num_samples
    random samples according to a given generation method? """
    d = defaultdict(list)
    for n in n_range:
        for k in k_range:
            for _ in range(num_samples):
                t = depgraph.EquableDiGraph(method(n, k))
                a = arity(t)
                p = projection_degree(t)
                g = depgraph.gap_degree(t)
                d[n, k, p, a, g].append(t)
    return d

""" e.g. for length 7, uniform trees:

Format: (n, k, p, a g): Number of trees generated.

As a sanity test, we want to make sure any random generation method will match the histogram
of the slow method, which would indicate that tree structures are just as "reachable" as under 
the generate-and-test method.

Should also consider the joint distribution with arity and projection degree, etc.

p: Projection degree / tree depth
a: Arity
g: Gap degree

Format: (n, k, p, a, g): (Number of trees generated by gold method, Number generated by proposed method)

Using the variant method:
{(7, 0, 2, 5, 0): (11, 1),
 (7, 0, 3, 2, 0): (51, 47),
 (7, 0, 3, 3, 0): (142, 84),
 (7, 0, 3, 4, 0): (68, 24),
 (7, 0, 4, 2, 0): (297, 313),
 (7, 0, 4, 3, 0): (153, 114),
 (7, 0, 5, 2, 0): (230, 311),
 (7, 0, 6, 1, 0): (48, 106),
 (7, 1, 3, 2, 1): (54, 47),
 (7, 1, 3, 3, 1): (112, 89),
 (7, 1, 3, 4, 1): (20, 16),
 (7, 1, 4, 2, 1): (327, 329),
 (7, 1, 4, 3, 1): (112, 104),
 (7, 1, 5, 2, 1): (298, 316),
 (7, 1, 6, 1, 1): (77, 99),
 (7, 2, 3, 2, 1): (42, 49),
 (7, 2, 3, 2, 2): (8, 1),
 (7, 2, 3, 3, 1): (80, 88),
 (7, 2, 3, 3, 2): (4, 2),
 (7, 2, 3, 4, 1): (18, 20),
 (7, 2, 4, 2, 1): (279, 296),
 (7, 2, 4, 2, 2): (37, 12),
 (7, 2, 4, 3, 1): (96, 100),
 (7, 2, 4, 3, 2): (15, 12),
 (7, 2, 5, 2, 1): (268, 313),
 (7, 2, 5, 2, 2): (53, 15),
 (7, 2, 6, 1, 1): (91, 90),
 (7, 2, 6, 1, 2): (9, 2),
 (7, 3, 3, 2, 1): (31, 35),
 (7, 3, 3, 2, 2): (10, 13),
 (7, 3, 3, 3, 1): (69, 52),
 (7, 3, 3, 3, 2): (23, 39),
 (7, 3, 3, 4, 1): (12, 20),
 (7, 3, 4, 2, 1): (239, 229),
 (7, 3, 4, 2, 2): (72, 105),
 (7, 3, 4, 3, 1): (90, 81),
 (7, 3, 4, 3, 2): (28, 23),
 (7, 3, 5, 2, 1): (250, 232),
 (7, 3, 5, 2, 2): (86, 72),
 (7, 3, 6, 1, 1): (57, 69),
 (7, 3, 6, 1, 2): (33, 30),
 (7, 4, 3, 2, 1): (43, 28),
 (7, 4, 3, 2, 2): (14, 15),
 (7, 4, 3, 3, 1): (62, 67),
 (7, 4, 3, 3, 2): (5, 19),
 (7, 4, 3, 4, 1): (9, 17),
 (7, 4, 4, 2, 1): (250, 195),
 (7, 4, 4, 2, 2): (97, 127),
 (7, 4, 4, 3, 1): (57, 64),
 (7, 4, 4, 3, 2): (21, 41),
 (7, 4, 5, 2, 1): (169, 202),
 (7, 4, 5, 2, 2): (183, 137),
 (7, 4, 6, 1, 1): (45, 47),
 (7, 4, 6, 1, 2): (45, 41),
 (7, 5, 3, 2, 1): (19, 23),
 (7, 5, 3, 2, 2): (21, 18),
 (7, 5, 3, 3, 1): (36, 59),
 (7, 5, 3, 3, 2): (12, 36),
 (7, 5, 4, 2, 1): (190, 213),
 (7, 5, 4, 2, 2): (114, 101),
 (7, 5, 4, 3, 1): (62, 78),
 (7, 5, 4, 3, 2): (17, 49),
 (7, 5, 5, 2, 1): (203, 198),
 (7, 5, 5, 2, 2): (222, 144),
 (7, 5, 6, 1, 1): (44, 49),
 (7, 5, 6, 1, 2): (60, 32),
 (7, 6, 3, 2, 1): (18, 18),
 (7, 6, 3, 2, 2): (23, 37),
 (7, 6, 3, 3, 1): (23, 103),
 (7, 6, 4, 2, 1): (199, 175),
 (7, 6, 4, 2, 2): (150, 170),
 (7, 6, 4, 3, 1): (50, 81),
 (7, 6, 4, 3, 2): (26, 31),
 (7, 6, 5, 2, 1): (230, 203),
 (7, 6, 5, 2, 2): (112, 96),
 (7, 6, 6, 1, 1): (62, 56),
 (7, 6, 6, 1, 2): (107, 30),
 (7, 7, 3, 2, 1): (29, 44),
 (7, 7, 3, 3, 1): (6, 33),
 (7, 7, 4, 2, 1): (180, 222),
 (7, 7, 4, 2, 2): (119, 134),
 (7, 7, 4, 3, 1): (67, 110),
 (7, 7, 5, 2, 1): (197, 219),
 (7, 7, 5, 2, 2): (246, 132),
 (7, 7, 6, 1, 1): (68, 57),
 (7, 7, 6, 1, 2): (88, 49),
 (7, 8, 3, 2, 1): (23, 59),
 (7, 8, 4, 2, 1): (258, 353),
 (7, 8, 4, 2, 2): (48, 75),
 (7, 8, 5, 2, 1): (226, 241),
 (7, 8, 5, 2, 2): (236, 175),
 (7, 8, 6, 1, 1): (88, 55),
 (7, 8, 6, 1, 2): (121, 42),
 (7, 9, 4, 2, 1): (119, 217),
 (7, 9, 5, 2, 1): (648, 605),
 (7, 9, 6, 1, 1): (233, 178)}


The gap degree discrepancy persists (larger than other method):
In [164]: df2.groupby(['n', 'g']).sum()
Out[164]:
       k    p    a  diff  total
n g
7 0    0   30   22     0   2000
  1  237  220  119   408  13478
  2  159  152   72  -408   4522

Arity discrepancy:
In [165]: df2.groupby(['n', 'a']).sum()
Out[165]:
       k    p   g  diff  total
n a
7 1   80  102  23  -244   2308
  2  216  195  64    93  14529
  3   90   88  32   191   2927
  4   10   15   4   -30    224
  5    0    2   0   -10     12

Tree depth discrepancy:
In [166]: df2.groupby(['n', 'p']).sum()
Out[166]:
       k   a   g  diff  total
n p
7 2    0   5   0   -10     12
  3  108  84  37   115   2289
  4  128  73  40   385   7923
  5   80  34  23  -246   7468
  6   80  17  23  -244   2308

Question: In 18000 trees, is a discrepancy of 408 to be expected?
Binomial confidence interval. Suppose the true proportion of GD2/GD1 is 4726/13478.  18000 samples.
The 95% confidence interval is [6186,6437], of size 251
So yes, there is a significant deviation here (408>251).
99% confidence intervalis 298.

Options: 
* Say this is a conservative method. But what if it is implicity encoding language-like biases?
* Try to increase gap degree in generated trees. What is a example of an undersampled tree?


By crossings:

In [173]: df2.groupby(['n', 'k', 'g']).sum()
Out[173]:
        p   a  diff  total
n k g
7 0 0  30  22     0   2000
  1 1  28  17     0   2000
  2 1  28  17    82   1830
    2  25  13   -82    170
  3 1  28  17   -30   1466
    2  25  13    30    534
  4 1  28  17   -15   1255
    2  25  13    15    745
  5 1  25  13    66   1174
    2  25  13   -66    826
  6 1  25  13    54   1218
    2  22  10   -54    782
  7 1  25  13   138   1232
    2  15   5  -138    768
  8 1  18   7   113   1303
    2  15   5  -113    697
  9 1  15   5     0   2000


The anomaly is worse for:
(1) high k,
(2) undersample for high p, oversample for low p
(3) undersample for low a, better for high a


# should calculate badness as binomial prob, and find the worst cases that way

By ratios:
Worst scenario for undersampling is 7  0  2  5  0   -10     12 -0.833333
Worst scenario for oversampling is  7  7  3  3  1    27     39  0.692308
Worst undersampling for diff is 7 7 5 2 2 

[(4, 2), (6, 4), (5, 1), (5, 3), (3, 6), (0, 5)]


-----------
|         |
| v---v---v
0 1 2 3 4 5 6 7 




"""
