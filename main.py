import csv
import random

import pandas as pd
import numpy as np
import os
import time
import folium
from math import sin, radians, cos, asin, sqrt
from xml.dom.minidom import parse
import xml.dom.minidom
import xml.etree.cElementTree as ct
import matplotlib.pyplot as plt
from queue import Queue
from Graph import *


def randomcolor():
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += colorArr[random.randint(0, 14)]
    return "#" + color


def transpose_2d(data):
    # transposed = list(zip(*data))
    # [(1, 5, 9), (2, 6, 10), (3, 7, 11), (4, 8, 12)]

    transposed = list(map(list, zip(*data)))
    return transposed


def haversine(lonlat1, lonlat2):
    lat1, lon1 = lonlat1
    lat2, lon2 = lonlat2
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def read_data(path, gap):
    datas = os.listdir(path)
    datalist = []
    for data in datas:
        df = pd.read_csv(path + "/" + data, header=None)
        df = df[[0, 1, 2, 3]]
        df[1] = pd.to_datetime(df[1], format='%Y-%m-%d %H:%M:%S')
        df['timeNo'] = ((df[1].dt.minute.fillna(0).astype("int") + 60 * df[1].dt.hour.fillna(0).astype(
            "int")) / gap).astype("int")
        df = df.drop(1, axis=1)
        df = df.drop(0, axis=1)
        # df['count'] = df.groupby("timeNo").count()
        df = df.groupby("timeNo").mean().reset_index()
        datalist.append(df)
        # print(df)
    return datalist


def read_data_fromXML(path, targetTime):
    tree = ct.parse(path)
    root = tree.getroot()
    for timestep in root.findall("timestep"):
        time = timestep.get("time")
        if (time == targetTime):
            vehicle_set = timestep.findall("vehicle")
            break

    idlist = []
    coorpair = {}
    for vehicle in vehicle_set:
        id = vehicle.get("id")
        coor = [float(vehicle.get("x")), float(vehicle.get("y"))]
        idlist.append(id)
        coorpair[id] = coor
    # list of id, and dict of coordinate
    return idlist, coorpair


def bfs(vehicle_id, idlist, coorpair, threshold):
    resuld_list = []
    print(len(idlist))
    count = 0
    q = []
    visited = set()
    q.append(vehicle_id)
    visited.add(vehicle_id)
    while (len(q) > 0):
        v = q.pop(0)
        resuld_list.append(v)
        for id in idlist:
            if id not in visited:
                coors = coorpair[id]
                coore = coorpair[v]
                if (coors[0] - coore[0]) ** 2 + (coors[1] - coore[1]) ** 2 < threshold ** 2:
                    q.append(id)
                    visited.add(id)
        count += 1
    print(count)
    return resuld_list


if __name__ == "__main__":
    """
    
    """
    idlist, coorpair = read_data_fromXML("data/fcdoutput.xml", "1836.00")
    result_file_name = "result.csv"
    print(idlist)
    threshold = 30
    round = 80
    number_of_malicious_node = 100
    result_vehicles = bfs("1000000_23_1__75", idlist, coorpair, threshold)
    # draw
    x = []
    y = []
    # Add attack nodes to result_vehicles
    # 0 30 60... 150
    for i in range(0, number_of_malicious_node):
        nid = "Att_" + str(i)
        result_vehicles.append(nid)
        coorpair[nid] = [random.uniform(2748, 2752), random.uniform(2284, 2288)]
        #coorpair[nid] = [random.uniform(2600, 2900), random.uniform(2000, 2400)]


    g = Graph()
    for id in result_vehicles:
        if "Att" in id:
            # Trust Value
            g.add_vertex(id, 0, -1)
        else:
            # Trust Value
            if random.random() < 0.2:  # 20%
                g.add_vertex(id, 10, 1)
            else:
                g.add_vertex(id, 0, 0)
    # plt.plot(x,y,'bo')
    # plt.axis("scaled")
    # plt.show()
    # Make graph

    result_vehicles = g.get_vertices()

    for from_id in result_vehicles:
        for to_id in result_vehicles:
            if from_id != to_id:
                # weight
                coorf = coorpair[from_id]
                coort = coorpair[to_id]
                if (coorf[0] - coort[0]) ** 2 + (coorf[1] - coort[1]) ** 2 < threshold ** 2:
                    weight = 0
                    if "Att" in from_id and "Att" in to_id:
                        weight = random.uniform(2, 5)
                    elif ("Att" not in from_id) and ("Att" not in to_id):
                        weight = random.uniform(2, 5)
                    else:
                        weight = random.uniform(2, 5)
                    g.add_edge(from_id, to_id, cost=weight)
                    # Compute cost(weight)
    X = range(0, round + 1)
    data = []
    with open(result_file_name, 'w', newline='')as f:
        TV_dict = {}
        header = g.get_vertices()
        data.append(header)
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        before_run = g.show_all_value()
        f_csv.writerow(before_run)
        data.append(before_run)
        # INIT
        for i in range(0, round):
            for vertex_id in g.get_vertices():
                TV_dict[vertex_id] = g.compute_new_value(vertex_id)
                # new TV
            for vertex_id in g.get_vertices():
                g.set_vertex(vertex_id, TV_dict[vertex_id])

            one_row = g.show_all_value()
            f_csv.writerow(one_row)
            data.append(one_row)
        tdata = transpose_2d(data)

    print("********************************************************************")
    plt.figure(figsize=(8, 6))
    for level_list in tdata:
        print(level_list)
        vehicle_id = level_list.pop(0)
        vehicle_v = g.get_vertex(vehicle_id)
        if vehicle_v.status == -1:
            color = "r"
            label = "Malicious node"
        elif vehicle_v.status == 0:
            color = "g"
            label = "Honest node"
        else:
            color = "b"
            label = "Bootstrap node"
        plt.plot(X, level_list, color=color, label=label)

    plt.grid()
    label_font = {'family': 'Times New Roman',
                  'size': 16,
                  }

    plt.xlabel("Number of iterations", label_font)
    plt.ylabel("Mass value", label_font)
    """Delete duplicate labels"""
    handles, labels = plt.gca().get_legend_handles_labels()
    i = 1
    while i < len(labels):
        if labels[i] in labels[:i]:
            del (labels[i])
            del (handles[i])
        else:
            i += 1
    """Delete duplicate labels"""
    plt.legend(handles, labels, fontsize=18)
    plt.show(dpi=300)
    # gap=5
    # timeframes=24*60/gap
    # targetframe=1
    # #From 0 to timeframes-1
    # print(timeframes)
    # datalist=read_data("data",gap)
    # incidents = folium.map.FeatureGroup()
    # m = folium.Map(zoom_start=12, tiles='https://mt.google.com/vt/lyrs=h&x={x}&y={y}&z={z}', attr='default')
    # count=0
    # slice_data=[]
    # for data in datalist:
    #     piece=data[data['timeNo']==targetframe].reset_index()
    #     if not piece.empty:
    #         slice_data.append(piece)
    #         #print(piece)
    #         lat = piece.loc[0].loc[3]
    #         long = piece.loc[0].loc[2]
    #         # ptext=dict[str(lat)+","+str(long)]
    #         incidents.add_child(
    #             folium.CircleMarker(
    #                 (lat, long),
    #                 radius=3,  # define how big you want the circle markers to be
    #                 fill=True,
    #                 fill_opacity=0.9,
    #             )
    #         )
    #         count+=1
    # print(count)
    # print(len(slice_data))
    # #Generating Graph
    # ExistTbale={}
    # samecount=0
    # for i in range(0,len(slice_data)):#ori
    #     for j in range(0, len(slice_data)):#dest
    #         if i!=j:
    #             olat = slice_data[i].loc[0].loc[3]
    #             olong = slice_data[i].loc[0].loc[2]
    #             dlat = slice_data[j].loc[0].loc[3]
    #             dlong = slice_data[j].loc[0].loc[2]
    #             if haversine((olat,olong),(dlat,dlong))<0.2:
    #                 #key=str(i) + "," + str(j)
    #                 if i<j:
    #                     key=(i+j)*(i+j+1)/2+j
    #                 else:
    #                     key=(i+j)*(i+j+1)/2+i
    #                 if key in ExistTbale:
    #                     print("Existed Edge:",i,",",j)
    #                 else:
    #                     print("Edge:",i,",",j)
    #                     folium.PolyLine(locations=[[olat,olong],[dlat,dlong]]).add_to(m)
    #                     ExistTbale[key]=True
    #                     #ExistTbale[str(j) + "," + str(i)] = True
    # # print(count)
    # #     # show
    # m.add_child(incidents)
    # file_path = "map.html"
    # m.save(file_path)
