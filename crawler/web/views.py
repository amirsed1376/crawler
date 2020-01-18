from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from requests import request
import requests
from bs4 import BeautifulSoup
import gzip
import shutil
from django.shortcuts import render
class Crawler:
    def __init__(self, url, depth, use_sitemap , use_form, form_data):
        self.base_url = url
        self.dis_allow = self.Nofollow()
        self.depth = int(depth)
        self.no_index = self.dis_allow
        self.use_sitemap = use_sitemap
        self.sitemap = self.sitemap_url()
        self.links=[[self.base_url]]
        self.session=requests.session()
        self.use_form = use_form
        self.form_data={}
        self.find_form_data(form_data=form_data)
        print("form_data",self.form_data)
        if len(self.sitemap) == 0:
            self.use_sitemap = False

    def find_form_data(self,form_data):
        try:
            form_datas=str(form_data).split(",")
            for data in form_datas:
                try:
                    self.form_data[data.split("=")[0].strip()]=data.split("=")[1].strip()
                except:
                    pass
        except:
            pass

    def crawl_gz(self, url):
        filename = url.split("/")[-1]
        with open(filename, "wb") as f:
            r = requests.get(url)
            f.write(r.content)

        with gzip.open(filename, 'rb') as f_in:
            with open('file.htm', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        file = open('file.htm', "r")
        bs = BeautifulSoup(file.read(), "lxml")
        locs = bs.find_all("loc")
        links = []
        for loc in locs:
            index1 = str(loc).index(">")
            index2 = str(loc).index("</")
            links.append(str(loc)[index1 + 1:index2])
            print("<<<<<<<", str(loc)[index1 + 1:index2])
        return links

    def Nofollow(self):
        disallow_list = []
        try:
            response = request(method="get", url=self.base_url + "robots.txt")
            text = response.text
            for line in text.splitlines():
                if "disallow" in line.lower():
                    index = line.index("/")
                    url = self.base_url + line[index + 1:]
                    disallow_list.append(url)
        except:
            pass
        return disallow_list

    def sitemap_url(self):
        print("xxxxxxxxxx")
        url_list = []
        try:
            response = request(method="get", url=self.base_url + "robots.txt")
            text = response.text
            for line in text.splitlines():
                if "sitemap" in line.lower():
                    index = line.index(":")
                    url = line[index + 1:]
                    url = str(url).strip()
                    path = None
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

    def no_visit(self, path):
        for depth_list in self.links:
            for url in depth_list:
                if str(url) == str(path):
                    return False
        return True

    def size(self, links):
        len_size = []
        for i in links:
            len_size.append(len(i))
        return sum(len_size)

    def is_not_readable(self, url: str):
        resource = url[len(self.base_url):]
        print("RESOURSE", resource)
        if "." not in resource:
            return False
        if str(resource).split(".")[-1] in ["html", "htm", "php"]:
            return False
        return True

    def meta_tag(self, tags):
        index = True
        follow = True
        for tag in tags:
            if "content=" in str(tag):
                if "noindex" in tag["content"]:
                    index = False
                if "nofollow" in tag["content"]:
                    follow = False
        return (index, follow)

    def crawl_sitemap(self):
        links = []
        for url in self.sitemap:
            print("URLLLLL",url)
            response = self.session.request(method="get", url=url)
            bs = BeautifulSoup(response.text, "lxml")
            locs = bs.find_all("loc")
            depth = 0
            for loc in locs:
                index1 = str(loc).index(">")
                index2 = str(loc).index("</")
                location = str(loc)[index1 + 1:index2]
                if "." in location:
                    if location.split(".")[-1] == "gz":
                        if depth >= self.depth:
                            continue
                        links.extend(self.crawl_gz(url=location))
                        depth += 1
                        continue
                print("<<<<<<<", location)
                links.append(location)
        return links



    def crawl(self):
        if self.use_sitemap:
            return self.crawl_sitemap()

        # session=requests.session()
        # links = [[self.base_url]]
        for depth, depth_list in enumerate(self.links):
            print("__________________depth=", depth)
            self.links.append([])
            if depth >= self.depth:
                return self.links
            if depth_list.__len__() == 0:
                return self.links
            for url in depth_list:
                print(">>>>>>>>>>>>", url)

                try:
                    if self.is_not_readable(url=url):
                        print("NO READABLE")
                        continue

                    if url in self.dis_allow:
                        print("DIS ALLOW")
                        depth_list.remove(url)
                        continue
                    response = self.session.get(url=url)
                    bs = BeautifulSoup(response.text, "lxml")
                    if self.use_form:
                        self.form_expand(forms=bs.find_all("form"),depth=depth)

                    (index, follow) = self.meta_tag(bs.find_all("meta"))
                    if not index:
                        print("___noindex___")
                        self.no_index.append(url)
                        depth_list.remove(url)
                    if not follow:
                        print("__nofollow____")
                        continue
                    # for link in bs.find_all("a"):
                    #     if "href=" not in str(link):
                    #         continue
                    #     if len(link["href"]) == 0:
                    #         continue
                    #     if str(link["href"]).strip()[0] == "/":
                    #         path = self.base_url + str(link["href"])[1:].strip()
                    #         if self.no_visit(path=path, links=links):
                    #             if path not in self.dis_allow:
                    #                 links[depth + 1].append(path)
                    #     elif self.base_url in str(link["href"]):
                    #         path = str(link["href"]).strip()
                    #         if self.no_visit(path=path, links=links):
                    #             if path not in self.dis_allow:
                    #                 links[depth + 1].append(path)
                    # self.links[depth+1].extend(self.expand(bs=bs,links=self.links))
                    for url in self.expand(bs=bs):
                        if self.no_visit(path=url):
                            self.links[depth + 1].append(url)
                except Exception as e:
                    print("--------error", e)
                    print(e.args)
                    continue
        return self.links


    def expand(self,bs):
        urls=[]
        for link in bs.find_all("a"):
            if "href=" not in str(link):
                continue
            if len(link["href"]) == 0:
                continue
            if str(link["href"]).strip()[0] == "/":
                path = self.base_url + str(link["href"])[1:].strip()
                if self.no_visit(path=path):
                    if path not in self.dis_allow:
                        urls.append(path)
            elif self.base_url in str(link["href"]):
                path = str(link["href"]).strip()
                if self.no_visit(path=path):
                    if path not in self.dis_allow:
                        urls.append(path)
        return urls


    def form_expand(self,forms,depth):
        if len(forms) == 0 :
            return

        for form in forms:
            try:
                path=self.base_url
                method="post"
                if "action=" in str(form):
                    if str(form["action"]).strip()[0] == "/":
                        path = self.base_url + str(form["action"])[1:].strip()
                    elif self.base_url in str(form["action"]):
                        path = str(form["action"]).strip()
                if not self.no_visit(path=path):
                    continue
                if "method=" in str(form):
                    method = form["method"]
                inputs=form.find_all("input")
                inputs_name=[]
                for input in inputs:
                    try:
                        inputs_name.append(input["name"])
                    except:
                        pass

                print('inputs_name',inputs_name)
                data=self.fill_data_form(inputs_name)
                print('data',data)
                # data={"username":"953611133050" , "password":"1272628868"}
                self.links[depth].append(path)
                response=self.session.request(method=method , url=path ,data=data)
                bs = BeautifulSoup(response.text, "lxml")
                (index, follow) = self.meta_tag(bs.find_all("meta"))
                if not index:
                    print("___noindex___")
                    self.no_index.append(path)
                    self.links[depth].remove(path)
                if not follow:
                    print("__nofollow____")
                    continue
                # self.links[depth + 1].extend(self.expand(bs=bs, links=self.links))
                for url in self.expand(bs=bs):
                    if self.no_visit(path=url):
                        self.links[depth+1].append(url)
                        print("expand ",url," in depth ",depth+1)
            except Exception as e:
                print("NOOOOOOOOOOOOOOOOOOOOOO   ",e)
                continue
    def fill_data_form(self,args):
        data={}
        for arg in args :
            try:
                data[arg]=self.form_data[arg]
            except:
                pass
        return data
@csrf_exempt
def crawler(request):
    if request.method == "POST":
        print("--------------------")
        for key in request.POST.keys():
            print(request.POST[key])
        print("--------------------")

        use_sitemap = False
        use_form = False
        try:
            if request.POST["sitemap"].lower() == "on":
                use_sitemap = True
            if request.POST["use_form"].lower() == "on":
                use_form = True
        except:
            pass
        crawler = Crawler(url=request.POST["url"], depth=request.POST["depth"], use_sitemap=use_sitemap , use_form=use_form , form_data=request.POST["form_data"])
        links = crawler.crawl()
        urls = []
        if not crawler.use_sitemap:
            for depth in links:
                for url in depth:
                    if url not in crawler.no_index:
                        urls.append(url)
        else:
            urls = links
        dic = {"number": len(urls), "crawl": urls}
        # jsn = json.dumps(dic)
        # return HttpResponse(jsn)
        return render(request,"list.html",dic)

    else:
        return render(request,"crawler.html",{})
# class crawler5()
# class Crawler5(APIView):
#     def get(self, request, format=None):
#         print("xxxxxxxxxxxxxxxxxxxxxxxx")
#         return Response({"content": "there is an error"})
