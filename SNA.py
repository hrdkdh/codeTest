#-*- coding: utf-8 -*-

"""
관계 분석을 위한 데이터 처리 플로우는 아래와 같다
1. 구성원 한명씩 친밀도를 물어보는 형태로 데이터를 수집한다.
2. 피설문자별 응답결과의 평균과 표준편차를 구해 표준점수화 한다.
3. 표준점수화 하면 평균(0점) 이하점수는 음수가 나오며, 음수는 모두 0점으로 처리하여 단순화한다.
4. 그래프를 그린다.
"""

import pandas as pd

#데이터 로드
df = pd.read_csv("data/network_test_data.csv")

def getNetworkGraph(df, targetSelectionName="", figsize=(12,12), dpi=160, nodeColor="#05507d", arrowDefaultColor="#dddddd", arrowEmpathyzedColor="#ff708a"):
    import numpy as np
    import networkx as nx
    import matplotlib.pyplot as plt

    #데이터 변환
    matrix=df.values

    #플롯 설정
    plt.figure(figsize=figsize, dpi=dpi, facecolor="w")
    plt.axis("off")
    
    #그래프 그리기
    DG = nx.DiGraph()

    #노드 사이즈 최소값 설정
    node_size_default=1600
    
    """
    #열평균을 구해 노드별 사이즈 설정
    node_size_list_org=[]
    for targetName in df["name"]:
        #1 이하 소수점이 있으므로 1로 맞춤
        thisMean=df[targetName].mean()+1
        node_size_list_org.append((targetName,thisMean))

    node_size_list=[]
    for nodeSizeOrg in node_size_list_org:
        thisNodeSize=node_size_default*nodeSizeOrg[1]
        node_size_list.append(thisNodeSize)
    """

    #엣지 리스트 생성 후 엣지 입력
    edge_list=[]
    for row in matrix:
        for i, column in enumerate(row):
            if (i<len(df["name"]) and row[0]!=df["name"][i] and row[i+1]>0):
                if targetSelectionName:
                    if targetSelectionName==row[0] or targetSelectionName==df["name"][i]:
                        DG.add_edge(row[0],df["name"][i])
                        edge_list.append((row[0],df["name"][i]))
                else:
                    DG.add_edge(row[0],df["name"][i])
                    edge_list.append((row[0],df["name"][i]))                    

    #노드 리스트 생성
    node_list=np.ravel(edge_list, order="c") #엣지 리스트를 1차원 배열로 변형
    node_list=list(set(node_list)) #중복값 제거
    
    #targetSelectionName이 있을 경우 해당 인물만 색깔을 다르게 함
    node_color_list=[]
    for nodeName in node_list:
        if targetSelectionName:
            if (nodeName==targetSelectionName):
                node_color_list.append("#c80025")
            else:
                node_color_list.append(nodeColor)
        else :
            node_color_list.append(nodeColor)
    
    #단방향, 양방향 분석 후 엣지 색깔 구분
    edge_color_list=[]
    for edge1 in edge_list:
        directCheck=0
        for edge2 in edge_list:
            if edge1[0]==edge2[1] and edge1[1]==edge2[0]:
                directCheck=1
        if directCheck==1:
            edge_color_list.append(arrowEmpathyzedColor)
        else:
            edge_color_list.append(arrowDefaultColor)

    #print(edge_list)
    #print(edge_color_list)

    #그래프 출력
    #k는 노드 간의 최소 거리, iteration은 최적점을 찾는 반복횟수, 스케일은 크기
    pos=nx.spring_layout(DG, k=3, iterations=100, scale=2)
    nx.draw_networkx_edges(DG, pos, edgelist=edge_list, node_size=node_size_default-100, edge_color=edge_color_list, width=2, arrows=True)
    nx.draw_networkx_nodes(DG, pos, nodelist=node_list, node_size=node_size_default, node_color=node_color_list)
    nx.draw_networkx_labels(DG, pos, font_family="NanumGothic", font_size=12, font_color="white", font_weight="bold")
    #nx.draw_networkx_edge_labels(DG, pos, edge_labels=edge_labels, alpha=0.45, font_size=5)
    
#그래프 생성
getNetworkGraph(df, targetSelectionName="", nodeColor="#8dc63f")
