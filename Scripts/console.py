from Scripts import graphiti as og
from Scripts import std
from Scripts import nx

import sys
import os.path
import glob

import random
import math

class Script(object):
	def run(self, args):
		print("Error: run() method not implemented!")

class Info(Script):
	def run(self, args):
		std.info()

class Load(Script):
	def run(self, args):
		if len(args) != 2:
			# TODO: og.console("Usage: {0} <filename>".format(args[0]))
			print("Usage: {0} <filename>".format(args[0]))
			return

		std.load_json(args[1])

class Save(Script):
	def run(self, args):
		if len(args) != 2:
			# TODO: og.console("Usage: {0} <filename>".format(args[0]))
			print("Usage: {0} <filename>".format(args[0]))
			return

		if os.path.isfile(args[1]):
			print("Error: File already exists!")
			return
		
		std.save_json(args[1])

class Clear(Script):

	def clear_graph(self):
	    for id in og.get_node_ids():
	        og.remove_node(id)

	def clear_colors(self):
	    og.set_attribute("og:space:linkmode", "string", "node_color")
	    for n in og.get_node_ids():
	        og.set_node_attribute(n, "og:space:color", "vec4", "1.0 1.0 1.0 1.0")

	def clear_icons(self):
	    for n in og.get_node_ids():
	        og.set_node_attribute(n, "og:space:icon", "string", "shapes/disk")

	def run(self, args):
		if len(args) == 1:
			self.clear_graph()
		elif len(args) == 2 and args[1] == "colors":
			self.clear_colors()
		elif len(args) == 2 and args[1] == "icons":
			self.clear_icons()
		else:
			print("Usage: {0} [colors|icons]".format(args[0]))
			# TODO : og.console()

class Layout(Script):
	
	def point(self):
		ids = og.get_node_ids()
		for nid in ids:
		    og.set_node_attribute(nid, "og:space:position", "vec3", "0.0 0.0 0.0")

	def sphere(self, args):
		radius = 20
		if len(args) == 2:
			radius = float(args[1])

		print(args, radius)

		ids = og.get_node_ids()
		for nid in ids:
		    r1 = random.random() * 2 * math.pi
		    r2 = random.random() * 2 * math.pi
		    r3 = 0.9 + 0.1 * random.random()
		    pos = [
		        radius * r3 * math.sin(r1) * math.cos(r2),
		        radius * r3 * math.cos(r1),
		        radius * r3 * math.sin(r1) * math.sin(r2)
		    ]
		    og.set_node_attribute(nid, "og:space:position", "vec3", std.vec3_to_str(pos))

	def cube(self):
	    ids = og.get_node_ids()
	    size = int(len(ids) ** (1.0 / 3.0))
	    count = 0
	    for nid in ids:
	        pos = [
	            count % size,
	            count / (size * size),
	            (count % (size * size)) / size
	        ]

	        for i in range(len(pos)):
	            pos[i] = 5 * (pos[i] - size / 2)

	        og.set_node_attribute(nid, "og:space:position", "vec3", std.vec3_to_str(pos))
	        count += 1

	def cone(self):
	    graph = std.load_nx_graph()

	    og.set_attribute("og:space:linkmode", "string", "node_color")

	    sorted_degrees = sorted(nx.degree(graph).values())
	    max_degree = sorted_degrees[-1]

	    degree_nodes = {}
	    for n in graph.nodes(data = True):
	        degree = nx.degree(graph, n[0])
	        if degree in degree_nodes:
	            degree_nodes[degree].append(n[0])
	        else:
	            degree_nodes[degree] = [n[0]]

	    max_radius = 30.0
	    max_height = 20
	    for n in graph.nodes(data = True):
	        degree = nx.degree(graph, n[0])

	        nodes = degree_nodes[degree]

	        radius = 1.0 + max_radius * float(1.0 - float(degree) / float(max_degree))
	        alpha = 2.0 * math.pi * random.random() #float(nodes.index(n[0])) / float(len(nodes)) 
	        # 3D
	        # beta = 2.0 * math.pi * random.random() #float(nodes.index(n[0])) / float(len(nodes)) 

	        x = radius * math.cos(alpha)
	        y = max_height * float(degree) / float(max_degree)
	        z = radius * math.sin(alpha)
	        # 3D
	        # x = radius * math.sin(alpha) * math.cos(beta)
	        # y = radius * math.sin(alpha) * math.sin(beta)
	        # z = radius * math.cos(alpha)

	        og.set_node_attribute(n[0], "og:space:position", "vec3", str(x) + " " + str(y) + " " + str(z))


	def globe_coordinates(latitude, longitude, delta = 0.0):
	    globe_radius = 50
	    radLatitude = latitude * math.pi / 180.0;
	    radLongitude = longitude * math.pi / 180.0;

	    return [
	        (globe_radius + delta) * math.cos(radLatitude) * math.cos(radLongitude),
	        (globe_radius + delta) * math.sin(radLatitude),
	        - (globe_radius + delta) * math.cos(radLatitude) * math.sin(radLongitude)
	    ]

	def globe(self):
	    ids = og.get_node_ids()
	    for id in ids:
	        geo = og.get_node_attribute(id, "og:world:geolocation")
	        if geo is not None:
	           pos = self.globe_coordinates(geo[0], geo[1])
	           og.set_node_attribute(id, "og:space:position", "vec3", std.vec3_to_str(pos))
	           og.set_node_attribute(id, "og:space:locked", "bool", "true")


	def seeds(self):
	    radius = 100.0

	    ids = og.get_node_ids()
	    zeros = []
	    for id in ids:
	        attribute = og.get_node_attribute(id, "depth")
	        if attribute == None:
	            continue
	        else:
	            if attribute == 0:
	                zeros.append(id)

	    count = 0
	    if len(zeros) == 1:
	        radius = 0.0
	    for id in zeros:
	        angle = 2.0 * math.pi * float(count) / float(len(zeros))

	        x = radius * math.cos(angle)
	        y = 0.0
	        z = radius * math.sin(angle)

	        og.set_node_attribute(id, "og:space:position", "vec3", str(x) + " " + str(y) + " " + str(z))
	        og.set_node_attribute(id, "og:space:locked", "bool", "True")
	        og.set_node_attribute(id, "og:space:activity", "float", "2.0")
	        og.set_node_attribute(id, "og:space:mark", "int", "2")
	        count += 1

	def usage(self, args):
		print("Usage: {0} [point|cube|sphere|cone|globe|seeds]".format(args[0]))

	def run(self, args):
		if len(args) == 2 and args[1] == "point":
			self.point()
		elif len(args) == 2 and args[1] == "cube":
			self.cube()
		elif len(args) >= 2 and args[1] == "sphere":
			self.sphere(args[1:])
		elif len(args) == 2 and args[1] == "cone":
			self.cone()
		elif len(args) == 2 and args[1] == "globe":
			self.globe()
		elif len(args) == 2 and args[1] == "seeds":
			self.seeds()
		else:
			self.usage(args)

class Topology(Script):

	def neighbors(self, args):
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    if og.count_selected_nodes() == 0:
	        print("Please select a node !")
	        return
	    
	    selected = og.get_selected_node(0)
	    graph = std.load_nx_graph()
	    neighbors = graph.neighbors(selected)
	    og.set_node_attribute(selected, "graphiti:space:color", "vec3", "0.0 1.0 1.0")
	    for node in neighbors:
	        og.set_node_attribute(node, "graphiti:space:lod", "float", "1.0")
	        og.set_node_attribute(node, "graphiti:space:color", "vec3", "0.0 1.0 1.0")

	def connected_components(self, args):
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    graph = std.load_nx_graph()
	    cc = nx.connected_components(graph)

	    for component in cc:
	        r = random.random()
	        g = random.random()
	        b = random.random()
	        color = str(r) + " " + str(g) + " " + str(b) 
	        
	        for node in component:
	            og.set_node_attribute(node, "graphiti:space:color", "vec3", color)

	def directions(self, args):
	    for id in og.get_link_ids():
	        og.set_link_attribute(id, "og:space:icon", "string", "styles/triangles")

	def connections(self, args):
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    # Building node degree table ...
	    edges = og.get_link_ids()
	    degree_table = dict()
	    for eid in edges:
	        nid1 = og.get_link_node1(eid)
	        nid2 = og.get_link_node2(eid)
	        if nid1 not in degree_table:
	            degree_table[nid1] = { "in" : 0, "out" : 0 }
	        if nid2 not in degree_table:
	            degree_table[nid2] = { "in" : 0, "out" : 0 }
	        degree_table[nid1]["out"] += 1
	        degree_table[nid2]["in"] += 1

	    # Randomizing color map
	    m = dict()
	    m["isolated"] = [0.95, 0.98, 0.36, 1.0]
	    m["leaf"] = [0.06, 0.94, 0.61, 1.0]
	    m["source"] = [0.91, 0.18, 0.17, 1.0]
	    m["sink"] = [0.03, 0.65, 0.94, 1.0]
	    m["other"] = [0.77, 0.78, 0.75, 1.0]

	    # Coloring
	    for nid in og.get_node_ids():
	        if nid not in degree_table:
	            t = "isolated"
	        else:
	            deg = degree_table[nid]
	            if deg["in"] == 0 and deg["out"] == 1:
	                t = "leaf"
	            elif deg["in"] == 0 and deg["out"] > 1:
	                t = "source"
	            elif deg["in"] > 0 and deg["out"] == 0:
	                t = "sink"
	            else:
	                t = "other"
	        og.set_node_attribute(nid, "graphiti:space:color", "vec4", std.vec4_to_str(m[t]))

	def degrees_high(self):
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    graph = std.load_nx_graph()
	    max_degree = max(nx.degree(graph).values())
	    for n in graph.nodes(data = True):
	        deg = nx.degree(graph, n[0])
	        tint = 0.3 + 0.9 * float(deg) / float(max_degree)

	        color = og.get_node_attribute(n[0], "graphiti:space:color")
	        color[0] = tint * color[0]
	        color[1] = tint * color[1]
	        color[2] = tint * color[2]
	        color[3] = 1.0
	        c = str(color[0]) + " " + str(color[1]) + " " + str(color[2])

	        og.set_node_attribute(n[0], "graphiti:space:color", "vec3", c)

	def degrees_low(self):
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    graph = std.load_nx_graph()
	    max_degree = max(nx.degree(graph).values())
	    for n in graph.nodes(data = True):
	        deg = nx.degree(graph, n[0])
	        tint = 0.3 + 0.9 * (1.0 - float(deg) / float(max_degree))

	        color = og.get_node_attribute(n[0], "graphiti:space:color")
	        color[0] = tint * color[0]
	        color[1] = tint * color[1]
	        color[2] = tint * color[2]
	        c = str(color[0]) + " " + str(color[1]) + " " + str(color[2])

	        og.set_node_attribute(n[0], "graphiti:space:color", "vec3", c)

	def degrees(self, args):
		if len(args) == 1:
			self.degrees_high()
		elif len(args) == 2 and args[1] == "high":
			self.degrees_high()
		elif len(args) == 2 and args[1] == "low":
			self.degrees_low()
		else:
			print("Error: {0}: Wrong arguments!".format(args[0]))

	def get_degree_map(self):
	    degrees = dict()

	    for eid in og.get_link_ids():
	        bi = False
	        e_type = og.get_link_attribute(eid, "type")
	        if e_type is not None and "<->" in e_type:
	            bi = True

	        nid1 = og.get_link_node1(eid)
	        nid2 = og.get_link_node2(eid)

	        if nid1 not in degrees:
	            degrees[nid1] = { "in" : 0, "out" : 0 }
	        if nid2 not in degrees:
	            degrees[nid2] = { "in" : 0, "out" : 0 }
	        
	        if bi:
	            degrees[nid1]["in"] += 1
	            degrees[nid1]["out"] += 1
	            degrees[nid2]["in"] += 1
	            degrees[nid2]["out"] += 1
	        else:
	            degrees[nid1]["out"] += 1
	            degrees[nid2]["in"] += 1

	    return degrees

	def spn(self, args):
	    degree_map = self.get_degree_map()
	    source_map = dict()

	    for eid in og.get_link_ids():
	        src = og.get_link_node1(eid)
	        if src not in degree_map:
	            continue
	        
	        if degree_map[src]["in"] == 0 and degree_map[src]["out"] >= 0:
	            dst = og.get_link_node2(eid)
	            if src not in source_map:
	                source_map[src] = [(dst, eid)]
	            elif dst not in source_map[src]:
	                source_map[src].append((dst, eid))

	    for nid in og.get_node_ids():
	        og.set_node_attribute(nid, "og:space:lod", "float", "0.0")
	        
	    for eid in og.get_link_ids():
	        og.set_link_attribute(eid, "og:space:lod", "float", "0.0")

	    for source in source_map.keys():
	        og.set_node_attribute(source, "og:space:lod", "float", "1.0")

	        for successor in source_map[source]:
	            og.set_node_attribute(successor[0], "og:space:lod", "float", "1.0")
	            og.set_link_attribute(successor[1], "og:space:lod", "float", "1.0")

	def run(self, args):
		if len(args) == 2 and args[1] == "neighbors":
			self.neighbors(args)
		elif len(args) == 2 and args[1] == "cc":
			self.connected_components(args)
		elif len(args) == 2 and args[1] == "directions":
			self.directions(args)
		elif len(args) == 2 and args[1] == "connections":
			self.connections()
		elif len(args) >= 2 and args[1] == "degrees":
			self.degrees(args[1:])
		elif len(args) == 2 and args[1] == "spn":
			self.spn(args)
		else:
			print("Error: {0}: Wrong arguments!".format(args[0]))



class Test(Script):

	def randomize_timeline(self):
	    ids = og.get_node_ids()
	    time = 0
	    for nid in ids:
	        time += 500
	        og.send_command(time, "graph:set_node_attribute",
	                              {
	                                  "id" : int(random.choice(ids)),
	                                  "type" : "vec4",
	                                  "name" : "graphiti:space:color",
	                                  "value" : "1.0 0.0 0.0 1.0"
	                              }) 

	def randomize_activity(self):
	    for id in og.get_node_ids():
	        if random.uniform(0.0, 1.0) > 0.10:
	            continue
	        activity = random.uniform(0.0, 5.0)
	        og.set_node_attribute(id, "og:space:activity", "float", str(activity))
  	    for id in og.get_link_ids():
	        activity = random.uniform(0.0, 2.0)
	        og.set_link_attribute(id, "og:space:activity", "float", str(activity))

	def randomize_icons(self):
	    icons = glob.glob("./Assets/Countries/*.png")
	    print(icons)
	    for id in og.get_node_ids():
	        icon = "countries/" + random.choice(icons).split("/")[-1][:2].lower()
	        og.set_node_attribute(id, "og:space:icon", "string", icon)

	    icons = glob.glob("./Assets/SpaceView/EdgeStyles/*.png")
	    print(icons)
	    for id in og.get_link_ids():
	        icon = "styles/" + random.choice(icons).split("/")[-1][:-4].lower()
	        og.set_link_attribute(id, "og:space:icon", "string", icon)

	def randomize_lod(self):
	    for id in og.get_node_ids():
	        og.set_node_attribute(id, "og:space:lod", "float", str(random.random()))   
	    for id in og.get_link_ids():
	        og.set_link_attribute(id, "og:space:lod", "float", str(random.random()))   

	def randomize_node_size(self):
	    for id in og.get_node_ids():
	        activity = random.uniform(0.0, 5.0)
	        og.set_node_attribute(id, "og:space:size", "float", str(activity))

	def randomize_edge_width(self):
	    for id in og.get_link_ids():
	        width = random.uniform(0.0, 5.0)
	        og.set_link_attribute(id, "og:space:width", "float", str(width))

	def randomize(self, args):
		if len(args) == 2 and args[1] == "activity":
			self.randomize_activity()
		elif len(args) == 2 and args[1] == "timeline":
			self.randomize_timeline()
		elif len(args) == 2 and args[1] == "lod":
			self.randomize_lod()
		elif len(args) == 2 and args[1] == "icons":
			self.randomize_icons()
		elif len(args) == 3 and args[1] == "node" and args[2] == "size":
			self.randomize_node_size()
		elif len(args) == 3 and args[1] == "edge" and args[2] == "width":
			self.randomize_edge_width()
		else:
			print("Error: {0}: Wrong arguments!".format(args[0]))

	def debug(self, args):
	    flag = og.get_attribute("og:space:debug")
	    og.set_attribute("og:space:debug", "bool", str(not flag))

	def run(self, args):
		if len(args) > 2 and args[1] == "randomize":
			self.randomize(args[1:])
		elif len(args) >= 2 and args[1] == "debug":
			self.debug(args[1:])
		else:
			print("Error: {0}: Wrong arguments!".format(args[0]))

class OpenDNS(Script):
	def score(self):
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    ids = og.get_node_ids()
	    for id in ids:
	        score = og.get_node_attribute(id, "sgraph:score")
	        if score is None:
	            og.set_node_attribute(id, "og:space:color", "vec4", "0.5 0.5 0.5 0.5")
	        elif score < -50:
	            og.set_node_attribute(id, "og:space:color", "vec3", "1.0 0.0 0.0")
	        elif score > 50:
	            og.set_node_attribute(id, "og:space:color", "vec3", "0.0 1.0 0.0")
	        else:
	            og.set_node_attribute(id, "og:space:color", "vec3", "1.0 1.0 1.0")

	def infected(self):
	    
	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    ids = og.get_node_ids()
	    for id in ids:
	        score = og.get_node_attribute(id, "sgraph:infected")
	        if score is None:
	            og.set_node_attribute(id, "og:space:color", "vec4", "0.5 0.5 0.5 0.5")
	        elif score < 0:
	            og.set_node_attribute(id, "og:space:color", "vec3", "1.0 0.0 0.0")
	        elif score > 0:
	            og.set_node_attribute(id, "og:space:color", "vec3", "0.0 1.0 0.0")
	        else:
	            og.set_node_attribute(id, "og:space:color", "vec3", "1.0 1.0 1.0")

	def dga(self):

	    og.set_attribute("graphiti:space:linkmode", "string", "node_color")

	    ids = og.get_node_ids()
	    for id in ids:
	        score = og.get_node_attribute(id, "sgraph:dga:score")
	        if score is None:
	            og.set_node_attribute(id, "og:space:color", "vec4", "0.5 0.5 0.5 0.5")
	            continue
	        else:
	            # DGA score is between [0 : not DGA, 100 : DGA]
	            sub = score / 100;
	            rgb = [1.0, 1.0 - sub, 1.0 - sub, 1.0]
	            og.set_node_attribute(id, "og:space:color", "vec4", std.vec4_to_str(rgb))

	def run(self, args):
		if len(args) == 2 and args[1] == "score":
			self.score()
		elif len(args) == 2 and args[1] == "infected":
			self.infected()
		elif len(args) == 2 and args[1] == "dga":
			self.dga()

# ----- Callbacks -----

class Console(object):
	def __init__(self):
		self.context = {
			"scripts" : {
				"info" : Info(),
				"load" : Load(),
				"save" : Save(),
				"clear" : Clear(),
				"layout" : Layout(),
				"topo" : Topology(),
				"test" : Test(),

				"opendns" : OpenDNS()
			}
		}

	def execute(self, command):
		args = command.split()
		if 'scripts' in self.context and args[0] in self.context['scripts']:
			self.context['scripts'][args[0]].run(args)
		else:
			# TODO: og.console("{0}: Command not found!".format(args[0]))
			print("{0}: Command not found!".format(args[0]))
