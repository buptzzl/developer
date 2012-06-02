# coding=utf8

import os, re, shelve
from time import sleep,ctime
import urllib2, urllib, urlparse
from threading import Thread, Lock
from Queue import Queue
from util_file import log_info

def curl_proxy(url,prox):
    '''基于代理爬取'''
    proxy_support = urllib2.ProxyHandler({'http':prox})
    proxy_supp_null = urllib2.ProxyHandler({})           # 不用代理
    opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    # 使用cookie: urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
    # 设置 urllib2 的全局 opener
    urllib2.install_opener(opener)
    # 直接调用 opener 的 open 方法代替全局的 urlopen 方法
    # html=operer.open(url).read()
    return urllib2.urlopen(url).read()
def curl_log(url,paras,beExplor=False):
    '''表单处理'''
    postdata=urllib.urlencode({
        'UserName':'stund',
        'password':'852123'
        # 加入其他相关POST方式的Key:val; 建议案httpfox的headers全写上
        })
    req = urllib2.Request(url,data=postdata)
    return urllib2.urlopen(req).read()

def curl_google(flog,url,cnt=3,timeout=20):
    '''爬取给定产品的Google评论 TODO: 记录失败'''
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.142 Safari/535.19',
             'Cookie':'GDSESS=ID=cf8ac8be49f8acdb:TM=1334745971:C=c:IP=59.64.138.143-:S=ADSvE-eqbAFWgJvEN9jwBqGchL-v7B-QPQ; PREF=ID=a4da58a0b2f23f10:NW=1:TM=1334745976:LM=1334745977:S=IxLhWtuXtWNUg034'
             }
    req = urllib2.Request(url,headers=headers)
    try:
        html = urllib2.urlopen(req,timeout=timeout).read()    # 超时Raise time-out ERROR
    except Exception,data:
        print "!!!! ERROR::curl_google( %s ) sleep(5) \t"%url,data        
        if cnt!=0:
            sleep(5)
            return curl_google(flog,url,cnt-1)  # 递归调用；最多尝试cnt次
        else:
            log_info(flog,'curl_google',data,{'url':url},ctime())
            return ""
    return html
def get_size(html,code='gbk'):
    sre = re.compile('<span id="n-to-n-start">(.*?)</span>',re.S)
    res = sre.findall(html)
    if res!=[]: 
        upat = u'\u5171(.*?)\u4e2a'.encode(code)      # 构造”共N个“的正则模式
        tmp = re.compile(upat).findall(res[0])
        if tmp==[]: return 0
        res = ''.join([ i for i in tmp[0] if i.isdigit() ])     # 清洗
        return int(res)
    return 0
def get_code(html):
    cre  = re.compile('charset=(.*[0-9a-zA-Z])',re.I)
    res = cre.findall(html)
    if res==[]: return None
    else:       return res[0].strip()    
def get_comm(html,codes):
    '''抽取HTML中的编码|评论 存为两级list'''
    if not html or html=='':
        print "!!!! WARN::get_comm() html-doc is empty !!!!"
        return []    
    ends = '>'                      # 空白字符的结束标识
    begs = '<'
    bad = u'\u7f3a\u70b9'.encode(codes)       # 汉字 缺点的unicode编码
    goo = u'\u4f18\u70b9'.encode(codes)       # 汉字 优点
    re1 = re.compile('<div class="review-content">(.*?)</div>',re.S)
    rec = re.compile('(&\w+)|(<.*?>)|(\s+)')
    res = []
    for one in re1.findall(html):
        one = one.strip()
        '''sz = one.count(ends)
        if sz==0 and one=='':   # 忽略空行
            continue
        tmp = ['', '', '']      # 存放 [tot, bad, good]的评论内容
        # 按ends 裁字符串, 
        ntmp = [i.strip() for i in one.split(ends) if i.strip().find(begs)!=0 ] #; return [codes,bad,goo,ntmp]
        ftmp = 0                # 存储前一次的状态 1:good -1:bad 0：total; 优缺点内容连续分配
        for ii in range(len(ntmp)):
            i = ntmp[ii]
            if i.find(begs)!=-1:    i=i[:i.find(begs)].strip()
            if len(i)<6: continue               # 全为无效字符
            if bad in i[:6] or ftmp==-1:                    # 负面评价              
                tmp[1] = ''.join([tmp[1],i.strip(bad)])
                ftmp = -1
            elif goo in i[:6] or ftmp==1:                   # 正面评价
                tmp[2] = ''.join([tmp[2],i.strip(goo)])
                ftmp = 1
            else:
                tmp[0] = ''.join([tmp[0],i])    # 整体评价
        tmp = [ rec.sub("",tmp[i]) for i in [0,1,2] ]+['\n']# 清洗无效字符
        '''
        tmp = rec.sub(" ",one)   # 清洗无效字符
        res.append(tmp)    
    return res
def crawler_one(path_log,psave,pre_url):
    '''爬取一个产品的所有评论，每次10个，一行存一个，列分割符为@@@@'''
    f = file(path_log,'ab')
    url = ''.join([pre_url,'0'])     # 默认第一个从
    html = curl_google(f,pre_url)
    codes = get_code(html)
    sz = get_size(html,codes)        #; print codes,sz; return html;
    res = get_comm(html,codes)
    emptyF = 0                       # 记录连续为空的网页数，达到阀值则终止抓取
    # 建立缓存文件，文件名与结果同前缀，后面添加.bak
    sh = shelve.open(''.join([psave,'.bak']),writeback=True)
    tbpos = url.find('q=') ; tepos = url[tbpos:].find('&')+tbpos
    keys=url[tbpos:tepos]
    sh[keys]=[res]
    sh.sync()
    sleep(1)
    sf = file(psave,'ab')            # 保存结果
    sf.write( '\n'.join(res) )
    sf.flush() 
    for i in range(0,sz,10):        # google每页返回10个
        url = ''.join([pre_url,str(i)])
        html = curl_google(f,url)    # ;return html;
#        codes = get_code(html)
        res = get_comm(html,codes)   # 默认使用同一编码
        print "!!!! INFO::crawler_one(%s) html-sz:%d, comment-list-sz:%d, total=%d !!!!"%(url,len(html),len(res),sz)
        if res==[]:
            emptyF += 1
            if emptyF <5: continue
            else:
                log_info(f,'crawler_one()','get continues empty HTML',{'emptyF':emptyF},ctime())
                break               # 终止正式抓取
        sf.write( '\n'.join(res) )
        sf.flush()
        sh[keys].append(res)
        sh.sync() 
        sleep(3)                    # wait for flush()
    sf.close()
    sh.close()

if __name__=='__main__':
    url_iphone = "http://www.google.cn/products/catalog?q=iphone&hl=zh-CN&cid=6622644360270162286&os=reviews&start="
    url_nokia = "http://www.google.cn/products/catalog?q=nokia&hl=zh-CN&cid=9196014927029443297&os=reviews&start="
    url_ipad = "http://www.google.cn/products/catalog?q=ipad&hl=zh-CN&cid=14971257728125277323&os=reviews&start="
    plog = r'./test/google_product.log'; psv = r'./test/goo_nokia.txt'
    tt=crawler_one(plog,psv,url_nokia)
    #f = file(plog,'ab')
    #tt = curl_google(f,''.join([url_iphone,'0']))
    #f.close()
    
    '''  # 对返回gzip压缩的html解压（一般发送时在header部分传递了参数 'Accept-Encoding':'gzip'）
f = urllib2.urlopen(url)
headers = f.info()
rawdata = f.read()
if ('Content-Encoding' in headers and headers['Content-Encoding']) or \
    ('content-encoding' in headers and headers['content-encoding']):
    import gzip
    import StringIO
    data = StringIO.StringIO(rawdata)
    gz = gzip.GzipFile(fileobj=data)
    rawdata = gz.read()
    gz.close()

# 使用PUT|DELETE方法
request = urllib2.Request(uri, data=data)
request.get_method = lambda: 'PUT' # or 'DELETE'

# 设置打印log
httpHandler = urllib2.HTTPHandler(debuglevel=1)
httpsHandler = urllib2.HTTPSHandler(debuglevel=1)
opener = urllib2.build_opener(httpHandler, httpsHandler)
    '''   
