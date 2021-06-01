from django.http.response import JsonResponse
from django.shortcuts import render, resolve_url
from .models import ChartData
import io
import base64
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import os
from django.conf import settings
# Create your views here.

def timeline(request):

    if request.method == "POST":
        lists = request.FILES.get('insights')
        
        name = str(lists).replace('.csv','')

        rows = request.POST.get('rows')

        df = pd.read_csv(lists).iloc[0:,:10].dropna(axis =1, how ='all').head(int(rows))

        # save the file into db
        is_existed  = ChartData.objects.filter(name=name)
        if not is_existed:
            files,created = ChartData.objects.get_or_create(files=lists,name=name)
            files.save()
        # end

        context = {
        'data':df.to_html(),
        'name':name,
        'rows':rows,
        }

        return render(request,'timeline/timeline.html',context)
    
    ChartData.objects.all().delete()
    
    return render(request,'timeline/timeline.html')



# get graph chart
def analysis(request,name,option):
    data = ChartData.objects.get(name=name)

    df = pd.read_csv(data.files).dropna(axis =1, how ='all').head(int(option))
    columns = []
    for col in df.columns:
        if df[col].dtype == 'int64' or df[col].dtype =='float64':
            columns.append(col)

    if request.method == "POST":
        str_cols = request.POST.get('cols')
        cols = str_cols.split(',')

        # line plot graph 
        plt.style.use('fivethirtyeight')
        figline = plt.figure(figsize=(10,6))
        #raw plot
        for col in cols:
            plt.plot(df[col],label =col)

        #plot styling
        plt.xlabel("User's Data Serial",fontsize=15,fontname="serif")
        plt.ylabel("Score",fontsize=15,fontname="serif")
        plt.legend(bbox_to_anchor =(0.7,1.1),ncol=4,fontsize=12)
        
        #plot and scatter graph
        figplotscatter = plt.figure(figsize=(10,6))
        x = range(len(df))
        myline = np.linspace(0,len(df),100)

        #raw data
        for col in cols:
            mymodel = np.poly1d(np.polyfit(x,df[col], 3))
            plt.plot(myline, mymodel(myline))
            plt.scatter(range(len(df[col])),df[col],label =col)
            
        #plot styling
        plt.xlabel("User's Data Serial",fontsize=15,fontname="serif")
        plt.ylabel("Score",fontsize=15,fontname="serif")
        plt.legend(bbox_to_anchor =(0.7,1.1),ncol = 4,fontsize=12)
        
        #histogram grapth
        fighist = plt.figure(figsize=(10,6))
        bins = np.arange(10,max(df[cols[0]])+10,10).tolist()
        #raw bars
        hist_df = []
        for col in cols:
            hist_df.append(df[col])
        plt.hist(hist_df,bins,ec='white',label=cols)
        #plot styling
        plt.xlabel("Score",fontsize=15,fontname="serif")
        plt.ylabel("Data Count",fontsize=15,fontname="serif")
        plt.legend(bbox_to_anchor =(0.7,1.1),ncol =4,fontsize=12)



        encoded = fig_to_base64(figline)
        lineplot = '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
        lineins = "X-axis shows your data serial.That might be your user's no. or dates of your selling products or anything.It starts with the first index of your data and ends with the last index . Y-axis shows the amount of value based on the spacific X-axis value(score)"

        encoded = fig_to_base64(figplotscatter)
        plot_scatter = '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
        psins = "Here X and Y axis mean the same as the first chart(linepot). But here you can have an overall experience of your data where it is going .Sometimes you can understand what the behaviour of the data will be."

        encoded = fig_to_base64(fighist)
        histogram = '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
        histins = "Unlike other two here X-axis keeps the score.From the min amount to max amount it increases by 10.Every bin has the length of 10.And Y-axis shwos the number of candidate follows by the X-axis.Let's say in a math exam the amount of students who got 70-80 are 10,in that case x-axis prints 70-80 and y-axis prints 10 "

        graph1 = {
            "chart":lineplot,
            "ins":lineins,
        }
        graph2 = {
            "chart":plot_scatter,
            "ins" : psins,
        }
        graph3 = {
            "chart":histogram,
            "ins":histins,
        }
        
        charts = [graph1,graph2,graph3]


        context = {
        'columns':columns,
        'name':name,
        'option':option,
        'charts':charts
        }
        return render(request,'timeline/analysis.html',context)


    context = {
        'columns':columns,
        'name':name,
        'option':option,
    }
    return render(request,'timeline/analysis.html',context)


# image to base_64
def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)

    return base64.b64encode(img.getvalue())

#doc
def doc(request):
    return render(request,"timeline/doc.html")