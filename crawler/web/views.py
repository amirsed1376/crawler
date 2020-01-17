from django.http import HttpResponse
import  json
from django.views.decorators.csrf import csrf_exempt
from requests import request
import requests
from bs4 import BeautifulSoup
import gzip
import shutil
from rest_framework.response import Response
from rest_framework.views import APIView
#
# def Crawl2(url:str, ):
#     links=list()
#     links.append(str(url))
#     sub_url = url.strip().split("/")
#     url=sub_url[0]+"//"+sub_url[2]
#     print(url)
#     session = dryscrape.Session()
#
#     for index,address in enumerate(links):
#         time.sleep(1)
#         try:
#             # print(session.complete_url(address))
#             session.visit(address)
#             response = session.body()
#             print(index," ",address)
#             # print(response.status_code)
#             # if response.status_code >= 500 :
#             #     print("error",response.status_code)
#             #     time.sleep(3)
#             #     continue
#
#
#             bs=BeautifulSoup(response,"lxml")
#             for link in bs.find_all() :
#                 if (link).has_attr("href"):
#                     if str(link["href"]).strip()[0]=="/" :
#                         path=url+"/"+str(link["href"])[1:].strip()
#                         if path not in links:
#                             links.append(path)
#                     elif url in str(link["href"]):
#                         path=str(link["href"]).strip()
#                         if path not in links:
#                             links.append(path)
#         except Exception as e :
#             session = dryscrape.Session()
#             print("except" , e)
#             continue
#
#
#
#
#     return links
#
#
# @csrf_exempt
# def crawler2(request):
#     if request.method == "POST":
#         url = request.POST["url"]
#         # crawl=Crawl(url=url)
#         crawl=Crawl2(url)
#         dic = {"crawl":crawl , "number":crawl.__len__()}
#         jsn= json.dumps(dic)
#         return HttpResponse(jsn)
#     else:
#         dic = {"a": "c"}
#         jsn = json.dumps(dic)
#         return HttpResponse(jsn)
#


class Crawler:
    def __init__(self , url , depth , use_sitemap):
        self.base_url = url
        self.dis_allow=self.Nofollow()
        self.depth = int(depth)
        self.no_index=self.dis_allow
        self.use_sitemap=use_sitemap
        self.sitemap = self.sitemap_url()
        print('self.sitemap',self.sitemap)
        if len(self.sitemap)== 0:
            self.use_sitemap=False

    def crawl_gz(self,url):
        # url = "https://dkstatics-public.digikala.com/digikala-site-map/100127566.gz"
        filename = url.split("/")[-1]
        with open(filename, "wb") as f:
            r = requests.get(url)
            f.write(r.content)

        with gzip.open(filename, 'rb') as f_in:
            with open('file.htm', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        file = open('file.htm', "r")
        bs = BeautifulSoup(file.read(), "lxml")
        locs=bs.find_all("loc")
        links=[]
        for loc in locs:
            index1=str(loc).index(">")
            index2=str(loc).index("</")
            links.append(str(loc)[index1+1:index2])
            print("<<<<<<<",str(loc)[index1+1:index2])
        return links

    def Nofollow(self):
        disallow_list=[]
        try:
            response = request(method="get", url=self.base_url+"robots.txt")
            text = response.text
            for line in text.splitlines():
                if "disallow" in line.lower():
                    index=line.index("/")
                    url = self.base_url + line[index+1:]
                    disallow_list.append(url)
        except:
            pass
        return disallow_list

    def sitemap_url(self):
        print("xxxxxxxxxx")
        url_list=[]
        try:
            response = request(method="get", url=self.base_url + "robots.txt")
            text = response.text
            for line in text.splitlines():
                if "sitemap" in line.lower():
                    index = line.index(":")
                    url = line[index + 1:]
                    url=str(url).strip()
                    path=None
                    if url[0] == "/":
                        path = self.base_url + str(url)[1:].strip()
                    elif self.base_url in str(url):
                        path = url
                    url_list.append(path)
        except:
            pass
        if self.base_url + "sitemap.xml" not in url_list:
            url_list.append(self.base_url + "sitemap.xml")
        return url_list

    def no_visit(self,path , links):
        for depth_list in links :
            if path in depth_list:
                return False
        return True

    def size(self,links):
        len_size = []
        for i in links:
            len_size.append(len(i))
        return sum(len_size)


    def is_not_readable(self,url:str):
        resource = url[len(self.base_url):]
        print("RESOURSE",resource)
        if "." not in resource:
            return False
        if str(resource).split(".")[-1] in ["html","htm","php"]:
            return False
        return True

    def meta_tag(self,tags):
        index = True
        follow =True
        for tag in tags :
            if "content=" in str(tag):
                if "noindex" in tag["content"]:
                    index=False
                if "nofollow" in tag["content"]:
                    follow = False
        return (index , follow)

    def crawl_sitemap(self):
        links=[]
        for url in self.sitemap:
            response = request(method="get", url=url)
            bs = BeautifulSoup(response.text, "lxml")
            locs=bs.find_all("loc")
            depth = 0
            for loc in locs:
                index1=str(loc).index(">")
                index2=str(loc).index("</")
                location=str(loc)[index1+1:index2]
                if "." in location:
                    if location.split(".")[-1] == "gz":
                        if depth >= self.depth:
                            continue
                        links.extend(self.crawl_gz(url=location))
                        depth+=1
                        continue
                print("<<<<<<<",location)
                links.append(location)
        return links

    def crawl(self):
        if self.use_sitemap:
            return self.crawl_sitemap()

        links=[[self.base_url]]
        for depth , depth_list in enumerate(links):
            print("__________________depth=",depth)
            # print(links)
            links.append([])
            if depth >= self.depth:
                return links
            if depth_list.__len__()==0:
                return links
            for url in depth_list:
                print(">>>>>>>>>>>>", url)


                try:
                    if self.is_not_readable(url=url):
                        continue

                    if url in self.dis_allow:
                        depth_list.remove(url)
                        continue
                    response = request(method="get", url=url)
                    bs = BeautifulSoup(response.text, "lxml")
                    (index , follow) = self.meta_tag(bs.find_all("meta"))
                    if not index :
                        print("___noindex___")
                        self.no_index.append(url)
                        depth_list.remove(url)
                    if not follow:
                        print("__nofollow____")
                        continue
                    for link in bs.find_all("a"):
                        if "href=" not in str(link):
                            continue
                        if len(link["href"])==0:
                            continue
                        if str(link["href"]).strip()[0] == "/":
                            path = self.base_url  + str(link["href"])[1:].strip()
                            if self.no_visit(path=path, links=links):
                                if path not in self.dis_allow:
                                    links[depth + 1].append(path)
                        elif self.base_url in str(link["href"]):
                            path = str(link["href"]).strip()
                            if self.no_visit(path=path ,links=links):
                                if path not in self.dis_allow:
                                    links[depth+1].append(path)
                except Exception as e:
                    print("--------error",e)
                    print(e.args)
                    print(link)
                    continue
        return links


@csrf_exempt
def crawler(request):
    if request.method == "POST":
        use_sitemap=True
        print("XXXXXXXXXXXX",request.POST)
        if request.POST["sitemap"].lower()=="false":
            use_sitemap=False
        crawler = Crawler(url=request.POST["url"] , depth=request.POST["depth"],use_sitemap=use_sitemap)
        links = crawler.crawl()
        urls=[]
        if not crawler.use_sitemap:
            for depth in links :
                for url in depth:
                    if url not in crawler.no_index:
                        urls.append(urls)
        else:
            urls=links
        dic = {"number":len(urls),"crawl":links }
        # dic = {"number":len(urls),"crawl":"cooooossss" }
        jsn= json.dumps(dic)
        return HttpResponse(jsn)

# class crawler5()
# class Crawler5(APIView):
#     def get(self, request, format=None):
#         print("xxxxxxxxxxxxxxxxxxxxxxxx")
#         return Response({"content": "there is an error"})
