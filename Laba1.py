	
import requests as r
from bs4 import BeautifulSoup
import re
from queue import Queue
from ratelimiter import RateLimiter
import argparse


def main(ur1,ur2,rps):
    depth=5
    u1=ur1.split(".org")[1]
    u2=ur2.split(".org")[1]
    baseUrl=ur1.split(".org")[0]+".org"

    @RateLimiter(max_calls=rps, period=1)
    def getLinks(url):
        resp=r.get(baseUrl+url)
        soup = BeautifulSoup(resp.text, features="lxml")
        refs1=soup.find_all("a",attrs={"class": None, "id":None, "accesskey":None,"href":re.compile(r"^(/wiki/[^:]+)$")})
        refs=[]
        for s in refs1:
            refs.append(s["href"])
        refs=list(set(refs))
        return refs

    def bfs(url1, url2):
        #i=0
        level ={url1:-1}
        parent={url1:""}
        visited=set()
        visited.add(url1)
        queue = Queue()
        queue.put(url1)
        find=False
        while not queue.empty() and not find:
            v = queue.get()
            if level[v]>depth:
                print("Глубина превышена")
                return  
            links=getLinks(v)
            links=list(set(links).difference(visited))
            for l in links:
                visited.add(l)
                parent[l]=v
                level[l]=level[v]+1
                #print(i,l,level[l])
                if l == url2:
                    find=True
                    break
                queue.put(l)
                #i+=1
        if find:
            path=[url2]
            cur=url2
            while parent[cur]!="":
                path=[parent[cur]]+path
                cur=parent[cur]
            return " -> ".join(path)

    return bfs(u1,u2)
       
if __name__=="__main__":
    parser = argparse.ArgumentParser()
   
    parser.add_argument("-s",'--url1', type=str,default="https://en.wikipedia.org/wiki/Gamma_distribution")
    parser.add_argument("-e",'--url2', type=str,default="https://en.wikipedia.org/wiki/Mathematics")
    parser.add_argument("-r",'--rps', type=int,default=10)
    args = parser.parse_args()
    print(main(args.url1,args.url2, args.rps))