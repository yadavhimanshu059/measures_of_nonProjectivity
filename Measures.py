# Packages used: NetworkX -- for tree representation as directed acyclic graphs

import networkx as nx

class Compute_measures(object):
    def __init__(self, tree):
        self.tree=tree                          # tree encodes the nodes and edges content in dictionary format. It uses directed graph (DiGraph) feature of networkX package. For example, nodes are encoded like this - tree.nodes={1:{form:'this',POS:'PRN'},2:{...}}   
        self.root=0                             # ROOT is an abstract node in the tree and is encoded as empty and with name=0    
        
    def dependency_direction(self, edge):       # Computes the direction of an edge (i.e., dependency) according to relative position of dependent and head  
        direction=''
        if edge[0]>edge[1]:                     # edge is a list data type in the format [head,dependent]
            direction='RL'
        else:
            direction='LR'

        return direction                        # return direction as 'LR' (Left-to-Right) or RL ('Right-to-Left')  
            
    def dependency_distance(self, edge):        # Computes the dependency length i.e., no. of nodes between head and its dependent 
        dd=0
        if edge[0]>edge[1]:                      
            for nodex in nx.descendants(self.tree, self.root):        
                if edge[1]<nodex<edge[0]:                             # all the nodes that lies linearly between dependent and head   
                    dd+=1
        else:
            for nodex in nx.descendants(self.tree, self.root):
                if edge[0]<nodex<edge[1]:
                    dd+=1
        return dd                              # returns the dependency distance of the edge
        
    def is_projective(self, edge):             # Checks if an edge is projective or not and returns a boolean value.
        projective=True
        if edge[0]>edge[1]:
            for nodex in nx.descendants(self.tree, self.root):
                if edge[1]<nodex<edge[0]:                          
                    if edge[0] in nx.ancestors(self.tree, nodex):          
                        projective=projective
                    else:                                                       # if a node 'x' occurring the edge span is not dominated by the head of the edge
                        if not self.tree.nodes[nodex]['deprel']=='punct':
                            projective=False
        else:
            for nodex in nx.descendants(self.tree, self.root):
                if edge[0]<nodex<edge[1]:
                    if edge[0] in nx.ancestors(self.tree, nodex):
                        projective=projective
                    else:                                                       # if a node 'x' occurring the edge span is not dominated by the head of the edge
                        if not self.tree.nodes[nodex]['deprel']=='punct':
                            projective=False
        return projective                                                       # Returns TRUE is edge is projective otherwise FALSE

    def edge_degree(self, edge):                                 # Computes the number of edges causing non-projectivity              
        eD=0
        edge_span=[]                 
        if edge[0]>edge[1]:                                      
            for nodex in nx.descendants(self.tree, self.root):   
                if edge[1]<nodex<edge[0]:
                    edge_span.append(nodex)                       
        else:
            for nodex in nx.descendants(self.tree, self.root):
                if edge[0]<nodex<edge[1]:
                    edge_span.append(nodex)

        for nodeI in edge_span:
            if not edge[0] in nx.ancestors(self.tree, nodeI):
                if not self.tree.nodes[nodeI]['head'] in edge_span:         # if the head of any intervening node exists outside the span of the edge
                    if not self.tree.nodes[nodeI]['deprel']=='punct':
                        eD += 1
                    
        return eD                                                        

    def gap_degree(self, node):                     # Computes the gaps in the projection chain containing maximum number of gaps 
        chains_gapD=[]
        terminals=[]
        for nodex in self.tree.nodes:
            if self.tree.out_degree(nodex)==0:
                terminals.append(nodex)

        for nodeT in terminals:                       
            gapD=0
            if nx.has_path(self.tree, node, nodeT):     
                pathx=next(nx.all_simple_paths(self.tree, node, nodeT, cutoff=None))     # Projection chain from ROOT to each Terminal node is encoded as list of nodes in the chain   
                for nodeP in pathx:
                    if not nodeP==self.root:
                        if not self.is_projective([self.tree.nodes[nodeP]['head'],nodeP]):   # If any edge in a projection chain is non-projective 
                            gapD=gapD+1                                                      # No. of non-projective edges in a projection chain = No. of gap degree
            chains_gapD.append(gapD)

        gap_deg=max(chains_gapD)                                                             # Gap degree of a node is the maximum gap degree in its dependents
        return gap_deg

    def projection_degree(self, node):
        size_chains=[]
        terminals=[]
        for nodex in self.tree.nodes:
            if self.tree.out_degree(nodex)==0:
                terminals.append(nodex)

        for nodeT in terminals:
            size=0
            if nx.has_path(self.tree, node, nodeT):
                pathx=next(nx.all_simple_paths(self.tree, node, nodeT, cutoff=None))              # Projection chain from ROOT to each Terminal node is encoded as list of nodes in the chain
                size=len(pathx)-1
            size_chains.append(size)
 
        proj_degree=max(size_chains)                                    # Projection degree = No. of nodes in the longest projection chain from ROOT to a terminal node 
        return proj_degree            

    def is_wellnested(self, node1, node2):
        wellnested=True
        if self.gap_degree(node1)>=1 and self.gap_degree(node2)>=1:
            if self.tree.nodes[node1]['head']==self.tree.nodes[node2]['head']:
                wellnested=False

        return wellnested

    def arity(self):                                                    # Computes arity of the tree using out-degree of nodes 
        tree_arity=self.tree.out_degree(list(self.tree.nodes))          # returns a dictionary containing nodenames as keys and its out-degree (or arity) as its values
        max_arity=max([x[1] for x in tree_arity])                       # Maximum out-degree = maximum arity in the tree
        histogram={}
        for arityx in [x[1] for x in tree_arity]:
            if arityx in histogram.keys():
                histogram[arityx]=histogram[arityx]+1                   # Creates arity histogram i.e. frequency of each arity
            else:
                histogram[arityx]=1
        arity_histogram=histogram                                       
        return [max_arity, tree_arity, arity_histogram]                    

    def endpoint_crossing(self,edge):
        edge_span=[]
        if edge[0]>edge[1]:
            for nodex in nx.descendants(self.tree, self.root):
                if edge[1]<nodex<edge[0]:
                    edge_span.append(nodex)
        else:
            for nodex in nx.descendants(self.tree, self.root):
                if edge[0]<nodex<edge[1]:
                    edge_span.append(nodex)

        endpoint={}
        
        for nodeI in edge_span:
            if not edge[0] in nx.ancestors(self.tree, nodeI):
                if not self.tree.nodes[nodeI]['head'] in edge_span:       # nodes intervening the edge span which are not dominated by the any node in the edge span    
                    if not self.tree.nodes[nodeI]['deprel']=='punct':
                        endpoint[self.tree.nodes[nodeI]['head']]=1        # creates a dictionary of all nodes having their outside their span. This dictionary has keys as 'heads' of the intervening nodes 

        endpoint_cross=len(endpoint)                                   # If the intervening nodes belongs to more than head outside the edge span, then 1-endpoint crossing constraint is voilated
        return endpoint_cross                                          # returns the no. of heads outside the edge span which dominates the intervening nodes   

    def compute_all(self):
        Arity=self.arity()
        Projection_degree=self.projection_degree()
        Gap_degree=self.gap_degree()
        direction={}
        dep_distane={}
        projectivity={}
        Edge_degree={}
        endpoint_cross={}
        for edgex in self.tree.edges:
            direction[edgex]=self.dependency_direction(edgex)
            dep_distance[edgex]=self.dependency_distance(edgex)
            projectivity[edgex]=self.is_projective(edgex)
            Edge_degree[edgex]=self.edge_degree(edgex)
            endpoint_cross[edgex]=self.endpoint_crossing(edgex)

        return [Arity, Projection_degree, Gap_degree, direction, dep_distance, projectivity, Edge_degree, endpoint_cross]
            
