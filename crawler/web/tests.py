from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from requests import request,post,get,session
import requests
from bs4 import BeautifulSoup
import gzip
import shutil
data={"username":"953611133050","password":"12726288468"}
s=session()
response=s.post(url="http://lms.ui.ac.ir/login" ,data=data )
print(s.cookies)
print(response.status_code)
# response = post()
# print(response.text)
print(s.headers.values())
bs = BeautifulSoup(response.text, "lxml")
for item in bs.find_all("a"):
    print("________________")
    try:
        # if item["href"][0] == 0 :
        url="http://lms.ui.ac.ir"+item["href"]
        print(url)
        resp=s.get(url=url)
        print(resp.text)

    except:
        continue
    # print(get(url=))
