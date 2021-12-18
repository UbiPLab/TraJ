import random

class Vertex:
    def __init__(self, node,value,status):
        self.id = node
        self.adjacent = {}
        self.trust_value=value
        self.status=status
        #-1 malicious
        # 0 honest
        # 1 bootstrap


    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def get_connections(self):
        return self.adjacent.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

    def get_value(self):
        return self.trust_value

    def set_value(self,value):
        self.trust_value=value

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node,value,status):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node,value,status)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def set_vertex(self,n,value):
        if n in self.vert_dict:
            vertex=self.vert_dict[n]
            vertex.set_value(value)

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to,cost = 0):
        # if frm not in self.vert_dict:
        #     self.add_vertex(frm,frm_v)
        # if to not in self.vert_dict:
        #     self.add_vertex(to,to_v)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)

    def get_vertices(self):
        return self.vert_dict.keys()

    def compute_new_value(self,vertex):
        node=self.get_vertex(vertex)
        sum_of_weight=0
        for o in node.get_connections():
            sum_of_weight+=node.get_weight(o)
        new_TV=0
        for o in node.get_connections():
            new_TV+=o.get_value()*node.get_weight(o)/sum_of_weight
        ##
        ##node.set_value(new_TV)
        ##
        ##
        ##
        return new_TV

    def show_all_value(self):
        l=[]
        for vertex_id in self.vert_dict.keys():
            l.append(self.get_vertex(vertex_id).get_value())
        print(l)
        return l
if __name__=="__main__":
    g = Graph()
