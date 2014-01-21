#!/usr/bin/env python

import sys
from unboxer.drg import DRGParser
import pygraphviz

def normalize_node_name(name):
    return name
    components = name.split(":")
    if len(components)==1:
        return name
    elif len(components)==2:
        return components[1]
    elif len(components)==3:
        if "(" in name:
            return components[2]
        else:
            return components[1]
    return name

def node_color(node):
    color = "white"
    if node.type == "discourse_unit":
        color = "cyan"
    elif node.type == "embedded":
        color = "cyan3"
    elif node.type == "event":
        color = "yellow"
    elif node.type == "concept":
        color = "gold"
    elif node.type == "referent":
        color = "palegreen"
    elif node.type == "role":
        color = "chocolate"
    elif node.type in ["attribute", "named", "cardinality"]:
        color = "coral"
    return color
    

def png(drg, pngfile):
    parser = DRGParser()
    graph = pygraphviz.AGraph(directed=True, strict=False,splines=True,overlap=False,rankdir="LR")

    parser.parse_tup_lines(drg)
    
    for tup in parser.drg.edges:
        if tup.token_index != 0:
            taillabel = "%s" % tup.token_index    
        else:
            taillabel = ""

        if len(tup.tokens) > 0:
            headlabel = "\\n\"%s\"" % " ".join(tup.tokens)
        else:
            headlabel = ""

        label = u"%s%s" % (tup.edge_type, headlabel)
        
        color = "black"
        if tup.structure == "argument":
            color = "red"
        elif tup.structure == "discourse":
            color = "black"
        elif tup.structure == "condition":
            color = "blue"
        elif tup.structure == "surface":
            color = "gray"
            
        graph.add_node(tup.from_node.name, label=tup.from_node.name, style="filled", fillcolor=node_color(tup.from_node))
        graph.add_node(tup.to_node.name, label=tup.to_node.name, style="filled", fillcolor=node_color(tup.to_node))
        graph.add_edge(tup.from_node.name, tup.to_node.name, color=color, label=label, headlabel=taillabel, fontsize=12, multiedges=True)
        
    graph.layout(prog='dot')
    graph.draw(pngfile, format='png')

