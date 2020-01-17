import requests
from bs4 import BeautifulSoup
import gzip
import shutil
url = "https://dkstatics-public.digikala.com/digikala-site-map/100127566.gz"
filename = url.split("/")[-1]
with open(filename, "wb") as f:
    r = requests.get(url)
    f.write(r.content)



with gzip.open(filename, 'rb') as f_in:
    with open('file.htm', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

file = open('file.htm' , "r")
bs = BeautifulSoup(file.read(), "lxml")
for item in bs.find_all("loc"):
    print(item)
