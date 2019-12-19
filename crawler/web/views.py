from django.shortcuts import render
from django.http import HttpResponse
import  json
import dryscrape
import bs4
from bs4 import BeautifulSoup,SoupStrainer
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
def Crawl(url:str):
    links=list()
    links.append(str(url))
    sub_url = url.strip().split("/")
    url=sub_url[0]+"//"+sub_url[2]
    print(url)
    session = dryscrape.Session()

    for index,address in enumerate(links):
        try:
            session.visit(address)
            response = session.body()
            print(address ,index)
            bs=BeautifulSoup(response,"lxml")
            for link in bs.find_all() :
                if (link).has_attr("href"):
                    if str(link["href"]).strip()[0]=="/" :
                        path=url+str(link["href"])[1:].strip()
                        if path not in links:
                            links.append(path)
                    elif url in str(link["href"]):
                        path=str(link["href"]).strip()
                        if path not in links:
                            links.append(path)
        except:
            continue

    return links
@csrf_exempt
def Crawler(request):
    print("xxxxxxxxxx",request)
    if request.method == "POST":
        url = request.POST["url"]
        crawl=Crawl(url=url)
        dic = {"crawl":crawl , "number":crawl.__len__()}
        jsn= json.dumps(dic)
        return HttpResponse(jsn)
    else:
        dic = {"a": "c"}
        jsn = json.dumps(dic)
        return HttpResponse(jsn)