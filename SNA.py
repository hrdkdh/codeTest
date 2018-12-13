#-*- coding: utf-8 -*-

"""
관계 분석 플로우는 아래와 같다
1. 구성원 한명씩 친밀도를 물어보는 형태로 데이터를 수집한다.
2. 피설문자별 응답결과의 평균과 표준편차를 구해 표준점수화 한다.
3. 표준점수화 하면 음수가 나오므로, 전체 데이터 테이블의 최소값을 각 데이터포인터에 더해주는 형태로 하여 모든 데이터를 양수로 변환한다.
4. 3번 데이터 테이블에서 나온 전체 평균값보다 낮은 점수는 모두 0점으로 처리한다.
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

#플롯 한글폰트 설정
plt.rcParams["font.family"] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12.
plt.rcParams['xtick.labelsize'] = 12.
plt.rcParams['ytick.labelsize'] = 12.
plt.rcParams['axes.labelsize'] = 12.

#help(plt.figure)

#플롯 설정
plt.figure(figsize=(12, 12), dpi=160, facecolor="w")
plt.axis("off")

#데이터 로드
df = pd.read_csv("data/network_test_data.csv")
matrix=df.values

#그래프 그리기
DG = nx.DiGraph()

#노드 리스트 생성
node_list=[]
for node in df["name"]:
    node_list.append(node)

#열평균을 구해 노드별 사이즈 설정
node_size_default=1600 #노드 사이즈 최소값
node_size_list_org=[]
for targetName in df["name"]:
    #1 이하 소수점이 있으므로 1로 맞춤
    thisMean=df[targetName].mean()+1
    node_size_list_org.append((targetName,thisMean))
    
node_size_list=[]
for nodeSizeOrg in node_size_list_org:
    thisNodeSize=node_size_default*nodeSizeOrg[1]
    node_size_list.append(thisNodeSize)

#엣지 리스트 생성 후 엣지 입력
edge_list=[]
for row in matrix:
    for i, column in enumerate(row):
        if (i<len(df["name"]) and row[0]!=df["name"][i] and row[i+1]>0):
            DG.add_edge(row[0],df["name"][i])
            edge_list.append((row[0],df["name"][i]))

edge_color_list=[]
for edge1 in edge_list:
    directCheck=0
    for edge2 in edge_list:
        if edge1[0]==edge2[1] and edge1[1]==edge2[0]:
            directCheck=1
    if directCheck==1:
        edge_color_list.append("#ff708a")
    else:
        edge_color_list.append("#cccccc")

#print(edge_list)
#print(edge_color_list)
        
#그래프 출력
#k는 노드 간의 최소 거리, iteration은 최적점을 찾는 반복횟수, 스케일은 크기
pos=nx.spring_layout(DG, k=3, iterations=100, scale=2)
nx.draw_networkx_edges(DG, pos, edgelist=edge_list, node_size=node_size_default-100, edge_color=edge_color_list, width=2, arrows=True)
nx.draw_networkx_nodes(DG, pos, nodelist=node_list, node_size=node_size_default, node_color="#05507d")
nx.draw_networkx_labels(DG, pos, font_family="NanumGothic", font_size=12, font_color="white", font_weight="bold")
#nx.draw_networkx_edge_labels(DG, pos, edge_labels=edge_labels, alpha=0.45, font_size=5)