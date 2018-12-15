#-*- coding: utf-8 -*-

"""
관계 분석을 위한 데이터 처리 플로우는 아래와 같다
1. 구성원 한명씩 친밀도를 물어보는 형태로 데이터를 수집한다.
2. 피설문자별 응답결과의 평균과 표준편차를 구해 표준점수화 한다.
3. 표준점수화 하면 평균(0점) 이하점수는 음수가 나오며, 음수는 모두 0점으로 처리하여 단순화한다.
4. 그래프를 그린다.
"""
import pandas as pd
import numpy as np

GRNO="1"
CATE="task"

if CATE=="task":
    pltTitleStr="[업무친밀도]"

if CATE=="people":
    pltTitleStr="[개인친밀도]"

def getScoreFromGongam():
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    import json
    
    url_source = "http://www.gongamplus.com/adm/?ca=getDataForSocialNetwork&grNo="+GRNO+"&cate="+CATE
    webpage = urlopen(url_source)
    source = BeautifulSoup(webpage, 'html5lib')
    score=json.loads(source.get_text().strip())
    return score


def isNumber(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

def getNetworkGraph(df, pltTitle="", targetSelectionName="", figsize=(12,12), dpi=160, nodeColor="#05507d", arrowDefaultColor="#dddddd", arrowEmpathyzedColor="#ff708a"):
    import networkx as nx
    import matplotlib.pyplot as plt

    #데이터 변환
    matrix=df.values

    #플롯 설정
    #help(plt.rc)
    plt.rc("font", family="NanumGothic", weight="bold", size=18)
    plt.figure(figsize=figsize, dpi=dpi, facecolor="w")
    plt.axis("off")
    if (pltTitle):
        plt.title(pltTitle);
    
    #그래프 만들기
    DG = nx.DiGraph()

    #노드 사이즈 최소값 설정
    node_size_default=1600

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
    
    #targetSelectionName이 있을 경우 해당 인물만 색깔을 다르게 함. 또한 무응답 혹은 불성실응답의 경우에는 연하게 처리함. (0점자)
    no_answer_check_list=[]
    for row in matrix:
        thisScoreCheck=False
        thisName=""
        for i, column in enumerate(row):
            if i>0:
                if float(column)>0:
                    thisScoreCheck=True
            else:
                thisName=column
        if thisScoreCheck==False:
            no_answer_check_list.append(thisName)

    node_color_list=[]
    for nodeName in node_list:
        if targetSelectionName:
            if nodeName==targetSelectionName:
                node_color_list.append("#c80025")
            else:
                if nodeName in no_answer_check_list:
                    node_color_list.append("#cccccc")
                else:
                    node_color_list.append(nodeColor)
        else :
            if nodeName in no_answer_check_list:
                node_color_list.append("#cccccc")
            else:
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

    #엣지 사이즈 설정
    if targetSelectionName:
        edge_width=4
        edge_node_size=node_size_default-395
    else:
        edge_width=2
        edge_node_size=node_size_default-100

    #그래프 출력
    #k는 노드 간의 최소 거리, iteration은 최적점을 찾는 반복횟수, 스케일은 크기
    pos=nx.spring_layout(DG, k=3, iterations=100, scale=2)
    nx.draw_networkx_edges(DG, pos, edgelist=edge_list, node_size=edge_node_size, edge_color=edge_color_list, width=edge_width, arrows=True)
    nx.draw_networkx_nodes(DG, pos, nodelist=node_list, node_size=node_size_default, node_color=node_color_list)
    nx.draw_networkx_labels(DG, pos, font_family="NanumGothic", font_size=12, font_color="white", font_weight="bold")
    #nx.draw_networkx_edge_labels(DG, pos, edge_labels=edge_labels, alpha=0.45, font_size=5)

def getDataFromScore(score, noAnswerRemove=True):
    import math
    
    df=pd.DataFrame.from_dict(score)
    matrix=df.values
    newDataTable=[]
    noAnswerName=[]
    
    for r, row in enumerate(matrix):
        if r==0:
            thisRowForNewDataTable=[]
            for col in row:
                thisRowForNewDataTable.append(col)
            newDataTable.append(thisRowForNewDataTable)
        else:
            thisSum=0
            thisCnt=0
            thisAvr=0
            thisStd=0
            thisRowForNewDataTable=[]
            thisScoreArr=[]
            thisStdArr=[]
            for c, col in enumerate(row):
                if c==0:
                    thisRowForNewDataTable.append(col)
                #각 행의 평균, 표준편차 구하기
                if col!=None and isNumber(col)==True:
                    thisScore=int(col)
                    if (thisScore>0):
                        thisSum=thisSum+thisScore
                        thisCnt=thisCnt+1
                else:
                    thisScore=0
                if c>0:
                    thisScoreArr.append(thisScore)                    
            if thisSum>0 and thisCnt>0:
                thisAvr=thisSum/thisCnt
            else:
                thisAvr=0
                noAnswerName.append(r)
            
            thisSumForVari=float()
            nowCnt=0
            #개인별 평균 및 표준편차 구하기
            for nowScore in thisScoreArr:
                if nowScore>0:
                    thisSumForVari=thisSumForVari+math.pow(nowScore-thisAvr, 2)
                    nowCnt=nowCnt+1
            if thisSumForVari>0 and nowCnt>0:
                thisStd=math.sqrt(thisSumForVari/thisCnt)

            #개인별 표준점수 입력하여 새테이블 완성
            thisStScore=float()
            for nowScore in thisScoreArr:
                if nowScore>0 and thisStd!=0:
                    thisStScore=(nowScore-thisAvr)/thisStd
                else:
                    thisStScore=0
                thisRowForNewDataTable.append(thisStScore)
            newDataTable.append(thisRowForNewDataTable)
    
    lastDataTable=[]
    arrForIndex=[]
    
    if (noAnswerRemove==True):
        #데이터가 없는 행(무응답행)이 있다면 행열에서 모두 제거한다
        for r, row in enumerate(newDataTable):
            noAnswerCheckRow=0
            for noAnswer in noAnswerName:
                if r==noAnswer:
                    noAnswerCheckRow=1
            if noAnswerCheckRow==0:
                lastRowData=[]
                for c, col in enumerate(row):
                    noAnswerCheckCol=0
                    for noAnswer in noAnswerName:
                        if c==noAnswer:
                            noAnswerCheckCol=1
                    if noAnswerCheckCol==0:
                        lastRowData.append(col)
                        if c==0:
                            arrForIndex.append(col)
                lastDataTable.append(lastRowData)
        del lastDataTable[0]
    else:
        for r, row in enumerate(newDataTable):
            lastRowData=[]
            for c, col in enumerate(row):
                lastRowData.append(col)
                if c==0:
                    arrForIndex.append(col)
            lastDataTable.append(lastRowData)
        del lastDataTable[0]
    
    df=pd.DataFrame(lastDataTable, columns=arrForIndex) 
    return df
    
#점수 로드
score=getScoreFromGongam()

#점수 표준화 및 데이터 정제
df=getDataFromScore(score, noAnswerRemove=False)
print(df)

#그래프 생성
#getNetworkGraph(df, pltTitle=pltTitleStr, targetSelectionName="", figsize=(8,8), nodeColor="#8dc63f")
