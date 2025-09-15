#!/bin/python

import json as j

# load data from json
F="students.json"
try:s=j.load(open(F,'r',encoding='utf-8'))
except (FileNotFoundError,j.JSONDecodeError):s=[]

# Write data into json
def W():j.dump(s,open(F,'w',encoding='utf-8'),ensure_ascii=False,indent=4)

# pretty Print
def P(x):print(f"学号:{x['学号']} | 姓名:{x['姓名']} | 性别:{x['性别']} | 宿舍:{x['宿舍']} | 电话:{x['电话']}")
def O():print("\n\n\n\n")

# Append student
def a():
    sid=input("请输入学号:").strip()
    if any(x["学号"]==sid for x in s):return print("该学号已存在，添加失败")
    name=input("请输入姓名:").strip()
    g=input("请输入性别(男/女):").strip()
    while g not in("男","女"):
        print("性别输入无效，请输入'男'或'女'");g=input("请输入性别(男/女):").strip()
    s.append({"学号":sid,"姓名":name,"性别":g,"宿舍":input("请输入宿舍房间号:").strip(),"电话":input("请输入联系电话:").strip()})
    W();print("学生信息添加成功")

# Query student
def Q():
    sid=input("请输入要查询的学号:").strip()
    x=next((x for x in s if x["学号"]==sid),None)
    if x:O();print("查询结果:");P(x);O()
    else:O();print("未找到该学号对应的学生");O()

# print All student
def A():
    if not s:return print("当前没有任何学生信息")
    O();print("所有学生信息如下:")
    for x in s:P(x)
    O()

# the Repl
def R():
    d={"1":a,"2":Q,"3":A}
    while 1:
        print("\n===== 学生宿舍管理系统 =====\n1\t添加学生信息\n2\t查询学生信息\n3\t显示所有学生\n4\t退出系统")
        try:
            c=input("输入选项(1-4):").strip()
            if c=="4":print("exit");break
            (d.get(c) or (lambda:print("^nyi")))() # not yet implemented
        except (EOFError,KeyboardInterrupt):O();break

if __name__=="__main__":R()
