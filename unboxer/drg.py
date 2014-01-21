from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import depth_first_search
import sys
from itertools import permutations

RHETORICAL_RELATIONS = [
    "continuation",
    "narration",
    "result",
    "contrast",
    "parallel",
    "precondition",
    "consequence", 
    "conditional",
    "alternation",
    "background",
    "elaboration",
    "explanation",
    "source",
    "attribution",
    "presupposition",
    "because",
    "since",
    "until",
]

CONDITIONS = [
    "attribute",
    "cardinality",
    "concept",
    "event",
    "role",
    "named",
    "relation",
]
def is_event(node):
    return node[0] == "e" and node[1:].isdigit()

# modified depth first visit of the Discourse unit graph
def du_dfs(drg, node, dfs):
    dfs.append(node)

    for oe in node.out_edges:
        if oe.edge_type in RHETORICAL_RELATIONS or "subordinates" in oe.edge_type or "dominates" in oe.edge_type and not oe.to_node in dfs:
            du_dfs(drg, oe.to_node, dfs)

#    for neighbor in node.neighbors_out():
#        if neighbor.type == "discourse_unit" or neighbor.type == "referent" and not neighbor in dfs:
#            du_dfs(drg, neighbor, dfs)

# returns a number indexing the discourse units
# e.g. "k15" -> 15
def du_index(du):
    return eval(du.name.replace('(', '').replace(')', '').split(":")[0][1:])


def uniq_nonzero(l):
    r = []
    for i in l:
        if (not i in r) and i > -1000:
            r.append(i)
    return r
    
class DRGNode:
    def __init__(self):
        # node types are: event, entity, discourse unit, symbol, relation
        self.type = ""
        self.name = ""
        self.in_edges = []
        self.out_edges = []

    # returns two lists containing neighboring nodes (inward and outward)
    def neighbors_in(self, edge_type=""):
        neighbors_in = []
        for e in self.in_edges:
            if edge_type=="" or e.edge_type==edge_type:
                neighbors_in.append(e.from_node)
        return neighbors_in

    def neighbors_out(self, edge_type=""):
        neighbors_out = []
        for e in self.out_edges:
            if edge_type=="" or e.edge_type==edge_type:
                neighbors_out.append(e.to_node)
        return neighbors_out
                                        
    def short(self):
        node_list = self.name.split(":")
        if len(node_list)==1:
            return node_list[0].encode("utf-8")
        else:
            return node_list[1].encode("utf-8")   
           
    def __str__(self):
        return "(%s) %s" % (self.type, self.name) 

class DRGTuple:
    def __init__(self):
        self.from_node = DRGNode()
        self.edge_type = ""
        self.to_node = DRGNode()
        self.structure = ""
        self.token_index = -1
        self.tokens = []
        self.affix = ""
           
    def __str__(self):
        return "%s -(%s)-> %s (%s '%s' %d)" % (self.from_node, self.edge_type, self.to_node, self.tokens, self.affix, self.token_index)  
        
    # key function for sorting
    def key(self):
        if self.structure == "discourse":
            return 3
        if self.structure == "structure":
            return 2
        if self.structure == "surface":
            return 1
        if self.structure == "argument":
            return 0
              
    def __cmp__(self, other):
        et1 = self.structure
        et2 = other.structure
        if et1 == "discourse" and et2 != "discourse":
            #sys.stderr.write("%s > %s\n" % (et1, et2))
            return 1
        elif et1 != "discourse" and et2 == "discourse":
            #sys.stderr.write("%s < %s\n" % (et1, et2))
            return -1
        else:
            if et1 == "structure" and et2 == "structure":
                #sys.stderr.write("%s, %s\n" % (self.to_node, other.to_node))
                if du_index(self.to_node) > du_index(other.to_node):
                    #sys.stderr.write("%d > %d\n" % (eval(self.to_node[1:]), eval(other.to_node[1:])))
                    return 1
                else: 
                    #sys.stderr.write("%d < %d\n" % (eval(self.to_node[1:]), eval(other.to_node[1:])))
                    return -1
            #sys.stderr.write("%s = %s\n" % (et1, et2))
            return 0
             

class DRG:
    def __init__(self):
        self.edges = []
        self.nodes = set()
        self.parent = dict()
        self.original = ""
        self.tokenized = []
        
    def add_tuple(self, tup):
        self.edges.append(tup)
        self.nodes.add(tup.from_node)
        self.nodes.add(tup.to_node)
        self.parent[tup.to_node] = tup.from_node
    
    def root(self):
        for node in self.nodes:
            if node.type == "discourse_unit":
                # count the 'non-referent' in-edges
                count = 0
                for e in node.in_edges:
                    if e.structure == "discourse" and e.edge_type != "main":
                        count += 1                
                if count==0:
                    return node
        
    
    # returns an ordered list of discourse unit to generate from 
    def discourse_units(self):
        dfs = []
        if self.root() != None:
            du_dfs(self, self.root(), dfs)
        return dfs
        
    def get_nodes_by_type(self, node_type):
        nodes = []
        for n in self.nodes:
            if n.type == node_type:
                nodes.append(n)
        return nodes
    
    def in_edges(self, node, edge_type="", structure=""):
        edges = []
        for tup in self.edges:
            if tup.to_node == node and (edge_type == "" or edge_type == tup.edge_type) and (structure == "" or structure == tup.structure):
                edges.append(tup)
        return edges
    
    def out_edges(self, node, edge_type="", structure=""):
        edges = []
        for tup in self.edges:
            if tup.from_node == node and (edge_type == "" or edge_type == tup.edge_type) and (structure == "" or structure == tup.structure):
                edges.append(tup)
        return edges
    
    def get_edge(self, node1, node2):
        for tup in self.out_edges(node1.name):
            if tup.to_node == node2.name:
                return tup
        return None
    
    def neighbors(self, node):
        neighbors = []
        for tup in self.edges:
            if tup.from_node == node:
                neighbors.append(tup.to_node)
        return neighbors
    
    # returns the list of neighbors to visit, ordered by token index
    def visit_neighbors(self, node):
        neighbors = []
        for tup in self.edges:
            if tup.from_node == node:
                if not (tup.edge_type == "referent" and tup.from_node == "k0"):
                    neighbors.append((tup.token_index, tup.to_node, tup.tokens))
        neighbors = sorted(neighbors, key=lambda token_index: neighbors[0])
        return neighbors

    def get_node_by_name(self, node_name):
        for n in self.nodes:
            if n.name == node_name:
                return n
                
        return None
        
    def get_node_by_type(self, node_type):
        for n in self.nodes:
            if n.type == node_type:
                return n
                
        return None
        
    def __str__(self):
        out = ""
        for t in self.edges:
            out += "%s\n" % unicode(t)
        return(out)
               
    def reassign_entities(self, bins):
        i = 0
        for e in self.edges:
            if e.edge_type == "concept":
                eref = e.to_node.neighbors_out(edge_type="instance")[0]
                j = 0
                for w in range(len(self.in_edges(eref))):
                    if bins[i][j]==0 and self.in_edges(eref)[w].token_index > 0:
                        self.in_edges(eref)[w].token_index = 0
                        j += 1
                    elif bins[i][j]>0 and self.in_edges(eref)[w].token_index == 0:
                        self.in_edges(eref)[w].token_index = 1
                        j += 1
                i += 1
           
    def rerank_entities(self, rankings):
        self.rerank(rankings, 'concept')

    def rerank_events(self, rankings):
        self.rerank(rankings, 'event')
        
    def rerank(self, rankings, node_type):
        i = 0
        for e in self.edges:
            if e.edge_type == node_type:
                eref = e.to_node.neighbors_out(edge_type="instance")[0]
                for w in range(len(self.in_edges(eref))):
                    if self.in_edges(eref)[w].token_index > 0:
                        #print "[DEBUG] {0} -> {1}".format(self.in_edges(eref)[w].token_index, rankings[i])
                        self.in_edges(eref)[w].token_index = rankings[i]
                        i += 1
                    else:
                        self.in_edges(eref)[w].token_index = -1000
     
                # normalize indexes
                indexes = map(lambda x: x.token_index, self.in_edges(eref))
                copy = [x for x in indexes]
                copy.sort()

                for w in range(len(self.in_edges(eref))):
                    if self.in_edges(eref)[w].token_index > -1000:
                        self.in_edges(eref)[w].token_index = uniq_nonzero(copy).index(self.in_edges(eref)[w].token_index)+1
                    else:
                        self.in_edges(eref)[w].token_index = 0

        
    def reassign_events(self, bins):
        i = 0
        for e in self.edges:
            if e.edge_type == "event":
                eref = e.to_node.neighbors_out(edge_type="instance")[0]
                j = 0
                for w in range(len(self.in_edges(eref))):
                    if bins[i][j]==0 and self.in_edges(eref)[w].token_index > 0:
                        self.in_edges(eref)[w].token_index = 0
                        j += 1
                    elif bins[i][j]>0 and self.in_edges(eref)[w].token_index == 0:
                        self.in_edges(eref)[w].token_index = 1
                        j += 1
                i += 1
                
    def baseline(self, node_type, baseline_file):
        baseline = dict()
        fd_freq = open(baseline_file)
        for line in fd_freq:
            key = tuple(line[:-1].split("\t")[0].split(' '))
            freq = eval(line[:-1].split("\t")[1])
            if not len(key) in baseline:
                baseline[len(key)] = dict()
            baseline[len(key)][key]=freq
        fd_freq.close()

        for e in self.edges:
            if (e.edge_type == "concept" and node_type == "ent") or (e.edge_type == "event" and node_type == "eve"):
                eref = e.to_node.neighbors_out(edge_type="instance")[0]
                j = 0

                nonzero_edges = []
                for ie in self.in_edges(eref):
                    if ie.token_index > 0:
                        nonzero_edges.append(ie)
                
                l = len(nonzero_edges)
                d = baseline[l]
                
                edge_types = tuple(map(lambda e: e.edge_type, nonzero_edges))
                
                # find most frequent permutation
                top_f = 0
                top_p = None
                for p in permutations(edge_types):
                    if p in d:
                        if d[p] > top_f:
                            top_p = p
                            top_f = d[p]

                consumed = []
                for ie in self.in_edges(eref):
                    if ie.token_index > 0:
                        for i in range(len(top_p)):
                            if ie.edge_type == top_p[i] and (not (i+1 in consumed)):
                                ie.token_index = i+1
                                consumed.append(i+1)
                                break

  
    def add_affixes(self, affix_file):
        fd = open(affix_file, 'r')
        affixes = map(lambda x: x[:-1], fd)
        fd.close()
        for e in self.edges:
            if len(e.tokens) > 0:
                e.affix = affixes.pop(0)

class DRGParser:
    def __init__(self):
        self.drg = DRG()
        
    def reset(self):
        self.drg = DRG()
        self.drg.original = ""
        
    # scan the given file line by line, excluding comments, and
    # parse the single lines
    def parse_tup_file(self, tup_file, debug=False):      
        self.reset()
        fd_tup = open(tup_file)
        self.parse_tup_lines(fd_tup.readlines())
        fd_tup.close()
        

    # scan the given text, provided as an array of lines, and
    # parse the single lines
    def parse_tup_lines(self, lines, debug=False):  
        for line in lines:
            if len(line) > 0 and not line.startswith("%") and line != "\n":
                tup = self.parse_tup_line(line, debug)
                self.drg.original += "%s\n" % line
                self.drg.add_tuple(tup)
        self.assign_node_types()
        if len(lines) > 2:
            self.drg.tokenized = lines[2].split(' ')[1:]
        
    # parse one line from a DRG  tuple representation, returns a DRGTuple
    # object representing an edge
    def parse_tup_line(self, line, debug):
        tup = DRGTuple()
        fields = line[:-1].decode("utf-8").split()

        tup.edge_type = u"{0}".format(fields[1].split("-")[0])
        
        if self.drg.get_node_by_name(fields[0]) == None:
            tup.from_node = DRGNode()
            tup.from_node.name = fields[0]
        else:
            tup.from_node = self.drg.get_node_by_name(fields[0])
            
        if self.drg.get_node_by_name(fields[2]) == None:
            tup.to_node = DRGNode()
            tup.to_node.name = fields[2]
        else:
            tup.to_node = self.drg.get_node_by_name(fields[2])
            
        # assign edge type
        if tup.edge_type in CONDITIONS:
            tup.structure = u"condition"
        elif tup.edge_type in ["referent"]:
            tup.structure = u"referent"
        elif tup.edge_type in ["surface", "function", "punctuation"]:
            tup.structure = u"surface"
        elif tup.edge_type in ["instance", "int", "ext"]:
            tup.structure = u"argument"
        else:
            tup.structure = "discourse"
        
        tup.to_node.in_edges.append(tup)
        tup.from_node.out_edges.append(tup)
        
        try:
            tup.token_index = eval(fields[3])
        except:
            # sympbol with whitespaces cause troubles
            pass
            #return None
        tup.tokens = fields[5:-1]
        return tup

    def assign_node_types(self):
        for n in self.drg.nodes:
            if len(n.in_edges)==0:
                n.type = u"discourse_unit"
            else:
                for e in n.in_edges:
                    if e.edge_type in RHETORICAL_RELATIONS or e.edge_type == "main":
                        n.type = u"discourse_unit"
                        break
                    elif e.edge_type == "referent":
                        n.type = u"referent"
                        break
                    else:
                        n.type = e.edge_type

