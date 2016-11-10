from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

import json
import psycopg2
import timeit


def googlemap(request):
    conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
    cur = conn.cursor()
    start = timeit.default_timer()
    cur.execute("""select latlon,storename from storetable \
    where (point(split_part(latlon, ',', 1)::numeric,split_part(latlon, ',', 2)::numeric)<@> point(24.7893351,120.9906655))<1""")
    rows = cur.fetchall()
    stop = timeit.default_timer()
    print "calclute distance take :"+str(stop - start) +"s"
    a=rows
    r=[]
    start = timeit.default_timer()
    #for i in a:
    #    cur.execute("select title,url from articletable where latlon='"+i[0]+"'")
    #    rows = cur.fetchall()
    #    r.append([i,(rows)])
    tempstr=""
    count=1
    for i in a:
        if(count!=len(a)):
            tempstr+="'"+i[0]+"',"
        else:
            tempstr+="'"+i[0]+"'"
        count+=1
    cur.execute("select title,url,latlon from articletable where latlon in ("+tempstr+")")
    rows = cur.fetchall()
    stop = timeit.default_timer()
    rx=dict()
    for i in rows:
        if(rx.get(i[2],0)==0):
            rx[i[2]]=[i]
        else:
            rx[i[2]].append(i)
    r=rx.items()
    stop = timeit.default_timer()
    print "Find child takes :"+str(stop - start) +"s"
    conn.close()
    return render(request, 'FoodBoard/google.html', {'stores':json.dumps(r)})


def donate(request):
    if request.method == 'POST':
        print(request.POST['comeon']);
        return HttpResponse(json.dumps({"689":123,"426":92}), content_type='application/json')

@ensure_csrf_cookie
def queryLatlng(request):
    qpstr=request.POST['latlngs'].split(",");
    print qpstr
    conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
    cur = conn.cursor()
    start = timeit.default_timer()
    cur.execute("""select latlon,storename from storetable \
    where (point(split_part(latlon, ',', 1)::numeric,split_part(latlon, ',', 2)::numeric)<@> point("""+qpstr[0]+","+qpstr[1]+"""))<1""")
    rows = cur.fetchall()
    stop = timeit.default_timer()
    print "calclute distance take :"+str(stop - start) +"s"
    a=rows
    r=[]
    start = timeit.default_timer()
    #for i in a:
    #    cur.execute("select title,url from articletable where latlon='"+i[0]+"'")
    #    rows = cur.fetchall()
    #    r.append([i,(rows)])
    tempstr=""
    count=1
    for i in a:
        if(count!=len(a)):
            tempstr+="'"+i[0]+"',"
        else:
            tempstr+="'"+i[0]+"'"
        count+=1
    cur.execute("select title,url,latlon from articletable where latlon in ("+tempstr+")")
    rows = cur.fetchall()
    stop = timeit.default_timer()
    rx=dict()
    for i in rows:
        if(rx.get(i[2],0)==0):
            rx[i[2]]=[i]
        else:
            rx[i[2]].append(i)
    r=rx.items()
    stop = timeit.default_timer()
    print "Find child takes :"+str(stop - start) +"s"
    conn.close()
    return HttpResponse(json.dumps(r), content_type='application/json')
