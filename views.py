from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

import json
import psycopg2
import timeit
from datetime import datetime
import time

stores_dict={}
timetick = time.strftime("%Y.%m.%d.%H.%M")

@ensure_csrf_cookie
def googlemap(request):
    """render FoodBoard Index"""
    global stores_dict

    #clean DB per 8 hr
    global timetick
    ch_tick=(datetime.strptime(time.strftime("%Y.%m.%d.%H.%M"),"%Y.%m.%d.%H.%M")-\
            datetime.strptime(timetick,'%Y.%m.%d.%H.%M'))

    if ch_tick.total_seconds()>48000:
        print "FoodBoard googlemap time to clean Store_dict cache"
        timetick = time.strftime("%Y.%m.%d.%H.%M")
        stores_dict.clear()

    #NTHU
    #latlon="120.99.06655,24.7893351"
    #TMU
    latlon = "121.56161799999995,25.025354"
    radius = "1.0"
    lon_,lat_ = latlon.split(",")
    if (stores_dict.get(latlon,None)==None):
        conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
        cur = conn.cursor()
        start = timeit.default_timer()
        cur.execute("""select latlon,storename from storetable \
        where (point(split_part(latlon, ',', 2)::numeric,split_part(latlon, ',', 1)::numeric)<@> point("""+latlon+"""))<"""+radius)
        rows = cur.fetchall()
        stop = timeit.default_timer()
        print "calclute distance take :"+str(stop - start) +"s"
        a=rows
        r=[]
        start = timeit.default_timer()
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
        print "Food Board queryLatlng : response from DB"
        print "Find child takes :"+str(stop - start) +"s"
        stores_json=json.dumps(r)
        #record this latlng
        stores_dict[latlon]=stores_json
        conn.close()
    else:
        #get json_from_cache
        print "Food Board queryLatlng : response from cache"
        stores_json=stores_dict[latlon]

    return render(request, 'FoodBoard/google.html', {'stores':stores_json,'lat':lat_,'lon':lon_})


def donate(request):
    if request.method == 'POST':
        print(request.POST);
        time.sleep(1);
        return HttpResponse(json.dumps({"689":123,"426":92}), content_type='application/json')


def queryScore(request):
    if request.method == 'POST':
	updated=False
	scores=[u'Worst', u'Normal', u'Nice']
	classes=[u'chinese', u'japan', u'korea', u'Tailand', u'West', u'Others']
	updateList=["",0,False,False,False,False,False,False]
        #print(request.POST);
	request_dict_tmp = dict(request.POST)
	request_dict = dict()
	for key_,value_ in request_dict_tmp.items():
		key=key_.replace('"','')
		#print type(value_)
		if type(value_) is list:
			value = [i.replace('"','') for i in value_]
		else:
			value=value_.replace('"','')
		#prevent key not exist
		request_dict[key] = request_dict.get(key, list())
		
		if type(value) is list:
			[request_dict[key].append(i) for i in value]
		else:
			request_dict[key].append(value)
		
	# print (request_dict)
	# check if bbox is verified
	if 'country' in request_dict:
		class_tuple=request_dict['country'];
		for i in class_tuple:
			updateList[classes.index(i)+2]=True
		updated=True

	if 'score' in request_dict:
		updateList[1]=scores.index(request_dict['score'][0])-1
		updated=True

        updateList[0]=request_dict['url'][0];
	print ("current tuples: ",updateList)
	# if data updated, connect psycopg2
	query_result="not valid data"
	try:
		if updated:
			print ("connecting DB")
			query="""INSERT INTO ArticleScoreTable(url,score,ch,jp,ko,tai,west,other) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) """
			conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
			cur = conn.cursor()
			cur.execute(query,updateList)
			conn.commit()	
			conn.close()
			print ("DB querydone")
			query_result="successfully sent"
	except:
		query_result="DB update fail"
		print("DB update fail")
		
        return HttpResponse(json.dumps({"result":query_result}), content_type='application/json')


def queryLatlng(request):
    print request.POST.keys()
    source_query=request.POST['Drag_Serach']
    print source_query
    latlon = request.POST['latlngs'];
    if (stores_dict.get(latlon,None)==None):
        qpstr = latlon.split(",");
        print qpstr
        conn = psycopg2.connect("dbname='foodmining' user='penolove' host='localhost' password='password'")
        cur = conn.cursor()
        start = timeit.default_timer()
        cur.execute("""select latlon,storename from storetable \
        where (point(split_part(latlon, ',', 2)::numeric,split_part(latlon, ',', 1)::numeric)<@> point("""+qpstr[1]+","+qpstr[0]+"""))<1.3""")
        rows = cur.fetchall()
        stop = timeit.default_timer()
        print "calclute distance take :"+str(stop - start) +"s"
        a=rows
        r=[]
        start = timeit.default_timer()

        count=1
        tempstr=""
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

        stores_json = json.dumps(r)
        #record this latlng only for serach
        if(source_query=="Serach"):
            print "record to stores_dict"
            stores_dict[latlon]=stores_json
        stop = timeit.default_timer()
        print "Food Board queryLatlng : response from DB"
        print "Find child takes :"+str(stop - start) +"s"
        conn.close()
    else:
        print "Food Board queryLatlng : response from cache"
        stores_json=stores_dict[latlon]

    return HttpResponse(stores_json, content_type='application/json')
