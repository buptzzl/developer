# coding=utf8
from pyquery import PyQuery as pyq
import re,urllib,os,time
import random
from util_file import transcoding
import shelve

def URL_ERROR(url,error=''):
    ''' URL爬取 错误LOG '''
    fp = open( r'./error_py.log','ab')
    fp.write('\t'.join([str(time.time()),url,error]))
    fp.close()
    return False

def get_html(url, host=None, cnt=8):
    ''' pyquery 爬起网页，并用外部函数解析其HTML '''
    startUrl = url
    try:
        d = pyq( url=startUrl ) ;   #PageLink = d(tgt_str)
        return d 
    except Exception,err:
        print '-'*8,err, ' sleep %ds -------------' % 2<<(7-cnt)
        time.sleep(2<<(7-cnt))  # 按指数规律递增
        cnt -= 1
        if cnt!=0:        # 重复尝试爬取
            return get_html(url,host,cnt)
        else:
            return URL_ERROR(url)
        
def code_check(strs,code_tgt='utf8'):
    ''' 检查 str 的编码方式 并转换为对应的编码 '''
    re_code = re.compile('charset="?([-\w]+)')
    if not isinstance(strs,str): return strs  
    mod = str(re_code.findall(html)[0])
    if mod!=code_tgt: return transcoding(strs,mod,code_tgt)
        
    
def page_list(html,url,num=False,host=None):
    ''' 获取 class="PageLink" 字段的值--MaxPage数; 产出URL: http://www.dianping.com/search/category/2/10/g328p1 '''
    url_sh = []
    lst = html('.PageLink')
    if len(lst)==0: return []
    MaxNum = int(lst[-1].text)                   #; print 'MaxNum:%d;' % MaxNum , 'lst: ', lst[-1]
    if num: return  [MaxNum]
    for shid in range(1,MaxNum+1):
        url_sh.append('p'.join([url,str(shid)])) #; print url_sh[-1]; exit(1)
    return url_sh
# 店铺URL列表
def id_list(html,url,host=None):
    ''' 获取href="/shop/4534036?KID=53628#!hippo/index=2,shopId=4534036,page=1,adType=20" class="BL"
        中的完整URL  '''
    res = []
    lst = html('.BL')
    for l in lst:
        temp = l.items()[0][1]           #; print 'temp:%d;' % temp , 'lst: ', l.items()[0]
        if temp == "#top":  continue
        res.append(''.join([url,temp]))  #; print res[-1];# exit(1)
    return res

def shop_list(host=None,startUrl=None,save=r'./dianping/'):
    ''' 爬取所有目录页面的目标URL 并添加到文件 '''
    if not host: host = "http://www.dianping.com"
    if not startUrl: startUrl="http://www.dianping.com/search/category/2/10/g328"
    html = get_html(startUrl,host)        ; print '='*8,' get total Category URLs ', '='*8
    urls = page_list(html,startUrl)     # 获得类别页面URLs
    shops = []
    if not os.path.exists(save):
        os.makedirs(save)
    save_url = open(save+'urls','ab')
    save_url.write('============= ADD NEW URLS; TIME: %s =============\n'%str(time.time()))
    for lst in urls:
        html = get_html(lst,host)         ; print '='*8,' get the Shop-urls in Category ','='*8
        shops.extend(id_list(html,host))        # 获得店铺URLs
        save_url.write( '\n'.join(shops))        
        save_url.flush()
    save_url.close()
    return shops

def comm_list(html,url=None,host=None):
    ''' 获取HTML中的评论 '''
    comments = []
    # HTML 结构： <li class="comment-list-item" ..> ..<div class="user-info"> .. <a href="/member/20822036"><div class="comment-entry"><div ..>评论内容
    conts = html('.content')
    users = conts('.user-info')('a')     # 获取所有User信息; pyquery支持迭代检索;按元素索引则变为为XML
    comms = [ cc.getchildren()[-1].text for cc in conts('.comment-entry') ]
    #comments = [ [users[i].items()[0][1].split('/')[-1],comms[i]] for i in range(len(users))]
    for i in range(len(users)):
        uid = users[i].items()[0][1].split('/')[-1]           # 抽取子节点中href的值部分
        if not uid.isdigit() or not comms[i] or len(comms[i])<2:
            print '!'*8,' Drop Error Comment ','!'*8, '\n\t\tInfo: UID=%s\t'%uid,comms[i]
            continue
        comments.append([uid,comms[i]])
    '''for cc in conts('.comment-entry'):
        com = 
        for ci in cc.getchildren():
            com = ''.join([com,ci.text]) # 取得评论文本
    for cc in html('.content'):          # 得到xml对象，没有COMMENT时返回[]   
        #user = cc('.user-info')('a').attr('href').split('/')[-1]  # 非pyquery对象，不支持jquery操作
        cu = cc.getchildren()[0].getchildren()[0]   # 对xml对象去子节点
        user = cu.items()[1].split('/')[-1]
        comm = cc.getchildren()[2].getchildren().getchildren()[0].text  # 评论文本（无解码操作）
        comments.append([user,comm])
    '''
    return comments

def comment_re(html,host=None):
    ''' 基于正则抽取HTML中的目标串 '''
    re_id = r'shopId=(\d{1,11})'
    re_ll = re.compile(r'<li class="comment-list-item".*?>.*?</li>',re.I)
    re_authorId = re.compile(r'<div class="user-info"><a href="/member/(\d{1,10})">',re.I)
    re_comment = re.compile(r'<div id="review_\d{1,10}_summary">(.*?)</div>',re.I)
    re_space = re.compile('(&nbsp;)|(<font style?\w+[^>]*>.*?</font>)|(<span style?\w+[^>]*>.*?</span>)|(<br />)|(</?\w+[^>]*>)')
    comments = []   # 存放所有 用户ID+评论
    comms = re_ll.findall(cont,re.M)
    tmp = []
    for l in comms:
        try:
            user = re_authorId.findall(l,re.M)[0] #; print user,'\n',l
            tmp  = re_comment.findall(l,re.M)[0]
        except Exception,data:
            print '='*20, data, '='*20;  continue
            comm = re_space.sub('', tmp) # 去除空白
            comments.append( '\t'.join([user,comm]) )
    return comments

def comment_list(url,host=None):
    ''' 获取店铺的全部点评 '''
    comments = []   # 存放所有 用户ID+评论
    page = 1
    url_pre = re.findall('.*shop/\d+',url)[0]+'/review_more?pageno='  # 获取 http://www.dianping.com/**/shop4534036/review_more?.... 的路径部分
    url_shop = url_pre+str(page)       ; print 'url_shop: %s\n' % url_shop
    html = get_html(url_shop)
    Mpage = page_list(html,url_shop,True)       # 取MaxpageNum    
    print '='*8, ' Html-size=%d  MaxPageNum=%s' % (len(html),Mpage),'='*8
    if(len(Mpage)!=0):
        page = int(Mpage[0])
        cont = html.html()                      # pyquery 爬取的网页
        for pgs in range(2,page+1):             # 遍历所有Pages                      
            '''
            comments.append(comment_re(cont))  # 正则抽取
            url_shop = url_pre+str(pgs)
            cont = urllib.urlopen(url_shop).read()      # urllib 库爬取的网页
            '''                
            if html:           temp = comm_list(html)
            else:              temp = []
            if len(temp)!=0: comments.extend(temp)    # 合并前一网页的评论信息
            url_shop = url_pre+str(pgs)         
            html = get_html(url_shop)
    else:
        comments = comm_list(html)
    return comments

def DianPing(save=r'./dianping/',shops=None):
        ''' 爬取点评网火锅网页URL中的评论 '''
    #host = "http://www.dianping.com"
    #startUrl="http://www.dianping.com/search/category/2/10/g328"
    #shops = shop_list(host,startUrl,save) 
        for sh in shops:
            temp = comment_list(sh)
            if len(temp)==0: continue               # 无评论内容
            comm =[ '\t'.join(i) for i in temp ]
            sh_id = sh[:sh.find('?')].split('/')[-1]
            fp = file(os.path.join(save,sh_id),'wb')
            for l in comm: 
                try: fp.write('%s\n'%l)
                except Exception: continue
            fp.close()                    ;
            print '='*8,' comments of shop:%s over '%sh_id, '='*8 #; exit(1)

if __name__ == '__main__':
    #total_code()
    f = open(r'./dianping/urls','rb')
    shops = [ i.strip() for i in f.readlines() ]
    f.close()
    DianPing(shops=shops)
