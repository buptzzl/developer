#coding:gbk
from pyquery import PyQuery as pyq
import re,urllib,os,time
import random
from util_file import transcoding
import shelve
 
def total_code(shopList=[],shp=None):    
        host="http://www.dianping.com"
        '''# 入口URL
    startUrl="http://www.dianping.com/search/category/2/10/g328"
    d=pyq(url=startUrl)
    PageLink=d('.PageLink')  # 取网页中 class="***" 的属性字段
    MaxNum=int(PageLink[-1].text)
    #MaxNum=1
    page=1
    while page<=MaxNum:
        shopList=[]
        url=startUrl+'p'+str(page)
        print url
        flag=1 
        while flag:
            try:
                pageContent=pyq(url=url)
                flag=0
            except Exception,data:
                print data
                print 'sleeping........10s'
                time.sleep(10)
                continue  
        # 获得第二级入口URL
        urls=pageContent('.BL')
        for i in urls:
            temp=i.items()[0][1]
            if temp=="#top":
                continue
            tmp=''
            tmp=host+temp
            shopList.append(tmp)  '''
        #shopList=list(set(shopList))
        sum_shop = 1
        regx=r'shopId=(\d{1,11})'
        regx_1=r'<li class="comment-list-item".*?>.*?</li>'
        regx_author=r'<div class="user-info"><a href="/member/\d{1,10}">(.*?)</a>'
        regx_content=r'<div id="review_\d{1,10}_summary">(.*?)</div>'
        for shop in shopList[-1::-1]:

            startPage=1
            shopId=re.findall(regx,shop)[0]  #;  print sum_shop,

            shopset = os.listdir(r'./output')            
            if shopId in shopset: # or shp.has_key(shopId): # 去重
                    print shopId
                    sum_shop += 1  
                    continue    # 已经被爬取
                       #if os.path.exists("./output/"+str(shopId))==True:
                         #    os.remove("./output/"+str(shopId))
                        # 建立第三级URL

            url=host+'/shop/'+str(shopId)+'/review_more'
            print url
            flag=1
            while flag:
                try:
                    pageContent=pyq(url=url)
                    flag=0
                except Exception,data:
                    print data
                    print 'sleeping........10s'
                    time.sleep(10)
                    continue
            try:
                totalNum=int(pageContent('.PageLink')[-1].text)
            except Exception,data:
                print data
                totalNum=1
            print url," ---------------- PageSize: ",str(totalNum)      
            while startPage<=totalNum:
                print 'startPage: %d, totSum: %d' %(startPage,totalNum)
                url=host+'/shop/'+str(shopId)+'/review_more?pageno='+str(startPage)
                #pageContent=pyq(url=host+'/shop/'+str(shopId)+'/review_more?pageno='+str(startPage))
                #comment=pageContent('li.comment-list-item')
                #print len(comment)
                #for i in comment:
                #    print i.info
                print url
                flag=1
                while flag:
                    try:
                        pageContent=urllib.urlopen(url).read()
                        flag=0
                    except Exception,data:
                        print data
                        print 'sleeping........10s'
                        time.sleep(10)
                        continue
                pageC=re.findall(regx_1,pageContent,re.M)
                for i in pageC:
                    author=re.findall(regx_author,i,re.M)
                    content=re.findall(regx_content,i,re.M)
                    try:
                        author=author[0]
                        re_h=re.compile('(&nbsp;)|(<font style?\w+[^>]*>.*?</font>)|(<span style?\w+[^>]*>.*?</span>)|(<br />)|(</?\w+[^>]*>)')
                        content=re_h.sub('',content[0])                 # 去除User-Info中的非法信息
                        fileobj=open('./output/'+str(shopId),'a+b')
                        fileobj.write(author+'\t'+content+'\n')
                        fileobj.close()
                    except Exception,data:
                        print data
                startPage+=1
            shp[shopId]=None    # 插入已爬取的 ID
            shp.sync()          # 数据刷新到文件
        #page+=1

if __name__ == '__main__':
    f = file(r'./dianping/urls','rb')
    urls = [ l.strip() for l in f.readlines() ]
    f.close()
    shp = shelve.open(r'./temp.bak',writeback=True)
    total_code(urls,shp)
    shp.close()
    time.sleep(10)
