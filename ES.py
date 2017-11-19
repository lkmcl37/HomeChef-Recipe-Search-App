'''
Created on Apr 30, 2017

@author: Ti Liang, Hao Wang
'''
import shelve
import numpy as np
from datetime import datetime
from elasticsearch import Elasticsearch
from scipy import spatial

#This module is for implementing query searching and auto suggestions on recipe
es = Elasticsearch()

#output wrapper
def wrapped(item,count):

    act_min = str(item['_source']["ActiveMinutes"])+' min(s)'
    if item['_source']["Cuisine"]=='': item['_source']["Cuisine"]='Unknown'
    cur=[str(count), #0
         item['_source']["Title"],#1
         item['_source']["Instructions"],#2
         item['_source']['PhotoUrl'],#3
         item['_source']['Ing_List'],#4
         item['_source']['Category'],#5
         item['_source']['LastModified'],#6
         item['_source']['Cuisine'],#7
         act_min,#8
         item['_source']['Ing_Name']]#9
         #item['_source']['SVD']]#10
    content = cur[1]
    if len(content)>300:
        content=content[0:300]+"..."
    cur[1]=content
    cur.append(str(count))#11
    cur.append(item['_score'])#12
    return cur

#calculate cosine similarity
def cosine(list1, list2):
    return 1 - spatial.distance.cosine(list1, list2)

#output top k results with the highest cosine score
def top_k(output,matrix):

    count=0
    k=6
    for o in output:
        score=[[cosine(matrix[i],matrix[count]),i] for i in range(len(matrix))]
        score.sort(key=lambda obj:obj[0])
        index=[i[1] for i in score[1:k+1]]
        o.append(index)
        count+=1
    print "================"
    print count
    return output

#recommendation module
def search_recipe(query):

    #search the recipes that meet all conditions
    #cate = categories
    #ing = ingredient
    pre = pre_query(query)

    ings=[]
    catg=[]

    for p in pre:
        for e in p[9]:
            ings += e.split()
        ings = list(set(ings))
        if p[5] == None:
            continue
        else:
            catg.extend(p[5].split())
            catg = list(set(catg))

    index=np.array([i for i in range(min(len(ings),len(catg)))])
    #print index
    ings_str=''
    for i in index:
        #print i
        ings_str=ings[i]+' '
    catg_str=''
    for i in index:
        catg_str=catg[i]+' '

    #search other recipes related to current recipe
    #e.g. sharing the same ingredients and keywords
    recipts = es.search(index='corpus', body={
    "size" : 2400,
    "sort" : "_score",
    "query": {
        "bool": {
        "should": [
               { "match": {
            "Title":  {
              "query": query,
              "boost": 2
        }}},
        { "match": {
            "Category":  {
              "query": catg_str,
              "boost": 2
        }}},
        { "match": {
            "Ing_Name":  {
              "query": ings_str,
              "boost": 2
        }}}
            ]
        }

  }
    })
    output=[]
    count=1
    matrix=[]

    for item in recipts['hits']['hits']:
        cur=wrapped(item,count)
        output.append(cur)
        vec=[float(i) for i in cur[10].split()]
        matrix.append(vec)
        count+=1

    #calculate the cosine scores of the results
    output = top_k(output, matrix)

    return output, len(output)

def pre_query(query):

       body = {"query":{
            "bool":{
            "should":[{
                    "multi_match" : {
                            "query": query,
                            "operator":"and",
                            "type":"cross_fields",
                            "fields" : ["Title", "Cuisine"],
                             "boost": 2
                    }}],
            "should" : [
                    {"match" : {"Category" : query}},
                    {"match":{
                            "Ing_Name" : query}}
                    ]
            }}
            }


       res = es.search(index="corpus", body = body)
       result = []

       count=1
       for item in res["hits"]["hits"]:
           cur = wrapped(item, count)
           result.append(cur)
           count+=1

       return result


#first version of codes
#recipts = es.search(index="reciption2", body={

##    "size" : 2400,
##    "sort" : "_score",
##    "query": {
##        "bool": {
##        "should": [
##               { "match": {
##            "Title":  {
##              "query": query,
##              "boost": 2
##        }}},
##        { "match": {
##            "Category":  {
##              "query": query,
##              "boost": 2
##        }}},
##        { "match": {
##            "Ing_Name":  {
##              "query": query,
##              "boost": 2
##        }}}
##
##            ]
##        }
##
##  }
##    })
##    output=[]
##    count=1
##    for item in recipts['hits']['hits']:
##        #print item
##
##        cur=wrapped(item,count)
##        #cur.append(d[item['_source']["Title"]])
##        output.append(cur)
##        count+=1
###         print item['_score']
###         print item['_source']['Instructions']
###         print item['_source']["Title"]
###         print item['_source']["Category"]
###         print item['_source']["Ing_Name"]
###         print "*********"
##    #print len(output)
##    return output


# for item in movies['hits']['hits']:
#     print item['_source']['title'],'title'
#
