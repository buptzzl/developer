# coding=utf8
import re

def test_dict_sogou_size():
    fp = file(r'../resources/dict/sogou_dic_10W/total.dic','rb')
    lines = [ l.strip().split() for l in fp.readlines() ]
    words = [ l[0] for l in lines if len(l)>1 ]
    words = ''.join(words)
    words = re.sub('[\d[a-z]\s]*','',words)
    wd_set = [ words[i:i+2] for i in range(0,len(words),2)]
    wd_dict = {}
    for w  in wd_set: wd_dict[w]=True
    print len(wd_dict.keys()) # 4778 个汉字
    return [words,wd_dict]

""" 测试、属性 Pyquery 的用法 """

from pyquery import PyQuery as pq
from lxml import etree
from BeautifulSoup import BeautifulSoup as bs

html = ''' <html><head>
<title  test='test'>Page标题</title></head>
<body>insert 0<p id="firstpara" align="center">This is paragraph <b>one</b>.</p>
<p id="secondpara" align="blah">This is paragraph <b>two</b>.</p>

<table cellpadding="0" cellspacing="0" class="result" id="4" ><tr>
<a onmousedown="return c({'fm':'as','F':'778717EA','F1':'9D73F1E4',
'F2':'4CA6BE6B','F3':'54E5243F','T':'1330258662','title':this.innerHTML,
'url':this.href,'p1':4,'y':'F9FDFEBF'})" href="http://home.focus.cn/msgview/1278/1/128860529.html"
target="_blank">aaa  <em></em>bbbb   </a>
</h3><font size=-1> topic <em> big </em>more  <em>JT  讲堂</em>JJJ  <br><span class="g">home.focus.cn/msgview/1278/1/128860529.html 2012-2-10  </span>
<table cellpadding="0" cellspacing="0" class="result" id="4" ><tr>
<a onmousedown="return c({'fm':'as','F':'778717EA','F1':'9D73F1E4',
'F2':'4CA6BE6B','F3':'54E5243F','T':'1330258662','title':this.innerHTML,
'url':this.href,'p1':4,'y':'F9FDFEBF'})" href="http://home.focus.cn/msgview/1278/1/128860529.html"
target="_blank">cccccccc  <em></em>ddddd   </a>
<span class="numbs" style="margin-left:120px">找到相关结果约3,070,000个</span>
</body>
</html>
'''

d = pq(html)
#de = pq(etree.fromstring(html))
fp = open(r'e:/t1', 'ab')

def test(pag):
    if pag==0: return []
    elif pag==1: return 10
    else : return {}
    
if __name__=='__main__':    
    tt = test_dict_sogou_size()
              
