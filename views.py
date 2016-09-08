from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render

import json
import psycopg2


def googlemap(request):
	conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
	cur = conn.cursor()
	cur.execute("""select latlon,storename from storetable \
	where (point(split_part(latlon, ',', 1)::numeric,split_part(latlon, ',', 2)::numeric)<@> point(24.7893351,120.9906655))<1""")
	rows = cur.fetchall()
	a=rows
	r=[]
	for i in a:
	    cur.execute("select title,url from articletable where latlon='"+i[0]+"'")
	    rows = cur.fetchall()
	    r.append([i,(rows)])
	conn.close()
	return render(request, 'FoodBoard/google.html', {'stores':json.dumps(r)})


def donate(request):
    if request.method == 'POST':
    	print(request.POST['comeon']);
    	return HttpResponse(json.dumps({"689":123,"426":92}), content_type='application/json')


def queryLatlng(request):
	qpstr=request.POST['latlngs'].split(",");
	print qpstr
	conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
	cur = conn.cursor()
	cur.execute("""select latlon,storename from storetable \
	where (point(split_part(latlon, ',', 1)::numeric,split_part(latlon, ',', 2)::numeric)<@> point("""+qpstr[0]+","+qpstr[1]+"""))<1""")
	rows = cur.fetchall()
	a=rows
	r=[]
	for i in a:
	    cur.execute("select title,url from articletable where latlon='"+i[0]+"'")
	    rows = cur.fetchall()
	    r.append([i,(rows)])
	conn.close()
	return HttpResponse(json.dumps(r), content_type='application/json')