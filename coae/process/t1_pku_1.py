# coding=gbk
from random import randint,choice
import urllib,re,time,os,shelve 

from util_list import LineOperator
from util_file import Dir_File
#from dzhdp_2 import get_html
# @brief ��ȡBaiduHIT�Ľ��

# TODO: �ο�CRF�г���֧��ģʽƥ��
def get_pos(lst, pos=0, tgt=[0], pos_type=['N']):
    ''' ��ȡ����list��ָ���к�ָ�� pos_type, ��������list:[[a],[b]] '''
    res = []
    if not isinstance(lst,list) or len(lst)==0:
        return res
    for l in lst:
        if len(l)>pos and len(l)>tgt[-1]:  # Ĭ��tgt��PosID��������
            for p in pos_type :
                if p in l[pos]:
                    tmp = [ l[i] for i in tgt ]
                    res.append(tmp) ; continue      
    return res

def result_list(html, host=None):
    ''' ��ȡ<.. class="nums"> ..N..</..> ��N, ���Ʒ�����ȡ result�е�URL��Title '''
    nums = html('.nums').text()
    if not nums or len(nums)==0:
        print '!'*20, ' ERROR ', '!'*20; return []      # Hits=0
    nums = re.findall('[0-9,]',nums)[0].replace(',','')
    res = [''.join(nums)]           # Hits = nums
    for r in html('.result'):       # ������ҳ�� class="result"
        Rurl = r('a').attr('href')
        Title = r('a').text()
        segment = r('font').text()
        res.append([Rurl,Title,segment])
    return res
def content_re(html,patt,re_sum=None,re_res=None):
    ''' ����[patt,sum,res1,res2,...] '''
    if not html or len(html)==0 or (not isinstance(html,str) and not isinstance(html,unicode)):
        print '!'*20, ' ERROR ', '!'*20; return []
    result = [patt]
    if re_sum:
        re_sum = re.compile(re_sum,re.M)
        try:
            ss = re_sum.findall(html)[0]
            ssc = re.findall('[0-9,]+',ss)[0] ;
            ss = ssc.replace(',','') ; print '\nResultSum=%s \n'%ss
            assert int(ss)>200, "HIT-SUM less than 3, drop it"
            result.append( ss )            # ���ȴ�Ž����SUM
        except Exception,data:
            print '!'*20, data, '!'*20;            # �޽��
            return []
    if re_res:
        re_res = re.compile(re_res,re.S)
        re_clean = re.compile('<.*?>')#('[<>a-zA-Z0-9!"#$%&\'(),-/:;<=>\@?\+\*\.\[\]\\^_`{|}~\s]',re.S)
        temp = re_res.findall(html)
        #if len(result)==0: result.append( str(len(temp)) )             # ����HIT��
        for i in temp:
            result.append( re_clean.sub('',i) )    
    return result
def content_bd(html,patt):
    ''' ��ȡBaidu���ؽ���е� Num+���� '''
    re_sum = '<span class="nums".*?>(.*?)<'
    re_res = '<font size=-1>(.*?)<br><span class="g">'
    return content_re(html,patt,re_sum,re_res)
def content_ss(html,patt):
    ''' ��ȡSoSo���ؽ���е� Num+���� '''
    re_sum = '<div id="sInfo">(.*?)</div>'
    re_res = '<li loc="\d+">(.*?)<div class="result_summary">'
    return content_re(html,patt,re_sum,re_res)

def codeType(ss,code='gbk'):
    try:
        ss.decode(code) ; return True
    except Exception,data:
        print '#'*8,' Error in CodeType TEST ', data,'#'*8 ;
        return False

def get_html(prefix,query,suffix):
    if not isinstance(query,dict): # or not isinstance(prefix,str) or not isinstance(suffix,str):
        return []  # �ٶ�URLĬ�϶�GBK���б���
    query_url=urllib.urlencode({query.keys()[0]:query[query.keys()[0]]}) # ��URL�� �����ַ� ���б��룬���ͷ����q=������ɾ��
    url = prefix+query_url+suffix ;  print 'URL: \t%s' % url
    fp_url = urllib.urlopen(url)
    #html = get_html(url_bd)
    html = fp_url.read()
    fp_url.close()
    return html#result_list(html) 
def getBaiduHit(query=''):
    ''' ��ȡBaidu-Hit ��ǰ10������+URL '''
    if not codeType(query,'gbk'): return []  # �ٶ�URLĬ�϶�GBK���б���
    ssuf = '&rsv_bp='+str(randint(0,9))+'&rsv_spt='+str(randint(0,9))
    spre = 'http://www.baidu.com/s?'        # +query_url+ssuf
    query = {'wd':query}
    return get_html(spre,query,ssuf)
def getSosoHit(query=''):
    if not codeType(query,'gbk'): return []  # URLĬ�϶�GBK���б���
    query={'w':query}
    spre1 = 'http://soso.com/q?sc=web&ch=w.uf&num='+str(randint(8,10))+'&'
    spre2 = 'http://soso.com/q?pid=s.idx&cid=s.idx.se&'
    spre = choice([spre1,spre2])            # ���ӿ�ѡ��
    ssuf = ''
    return get_html(spre,query,ssuf)

def hit_pattern(words=[]):
    ''' ������Ĵʣ����� 48��ģʽ; ע����˫���� '''
    patterns = {'midle':['�е�', '��Щ'], 'tail':[' ��ô��', '�˵�']}#, 'head':['��']}
    PosA = [ '��', '��', '��', '��', '��', '��', 'ǿ', '��', '��', '��']
    NegA = [ 'С', '��', '��', '��', 'ǳ', '��', '��', 'խ', '��', 'ϸ']
    PosPat = []
    NegPat = []
    for w in patterns['tail']:                  # A+TailWord �ṹ
        PosPat.extend([ ''.join([i,w]) for i in PosA])
        NegPat.extend([ ''.join([i,w]) for i in NegA])
    for w in patterns['midle']:                 # MidWord+A �ṹ
        PosPat.extend([ ''.join([w,i]) for i in PosA])
        NegPat.extend([ ''.join([w,i]) for i in NegA])
    patt_full = []
    for w in words:
        posPw = [ '"'+w+i+'"' for i in PosPat ]
        negPw = [ '"'+w+i+'"' for i in NegPat ]
        patt_full.append([posPw,negPw])            # ��ƥ���ģʽ����ΪPos,Neg
    return patt_full

def hit_save(lst,fp,ss_sep='@@@'):
    ''' �����HIT������ļ� ·������: pos|neg_source_modelID eg: pos_baidu_1 '''
    if not isinstance(lst,list) or len(lst)==0 or not isinstance(fp,file):
        return False    
    fp.write( ss_sep.join(lst)+'\n' )
    fp.flush()
    return True

def word_search(dictP,shp):  
    ''' ���ֵ��еĴʣ�����������������ļ�(ע��total.dict�ļ���gbk����)  '''
    fp = file(dictP,'rb')
    words = [ l.strip().split() for l in fp ]       #; print words[0:5]
    fp.close()                          #; return words
    #words = cfp.key_value(model='rb')  # ��ȡ�ֵ� resources\dict\sogou_dic_10W ��һλ��Ϊ��
    wlist = get_pos(words, 2, [0], ['N','V','A'])   # ����ȡ N V A ����
    wlist = [ w[0] for w in wlist ]     # ɾ��һ��list
    wpatt =  hit_pattern(wlist)
    #print wpatt[0][0],'size of DICT:%d'%len(wpatt); exit(1)
    #try: wpatt = [ w.decode('utf8').encode('gbk') for w in dictP if isinstance(w,str)]
    #wpatt = dictP ; print len(wpatt[0][0])
    sh_keys = shp.keys()
    files = [r'./dianping/pos_bd_',r'./dianping/pos_ss_',r'./dianping/neg_bd_',r'./dianping/neg_ss_']
    for i in range(len(wpatt[0][0])):   # ����ģʽ�� �ɺ���hit_pattern ֪��Pon-Neg����80����-ģʽ
        print '='*5, ' Finish:%d ID=%d patter %s HIT '%(len(sh_keys),i,wpatt[0][0][i]), '='*5
        fs = [ f+str(i) for f in files ]
        fps = [ file(f,'ab') for f in fs ]      # ���������
        size = len(wpatt)
        for j in range(size):     # ����ÿ����
            neg_qw = wpatt[j][0][i]     #; print neg_qw
            pos_qw = wpatt[j][1][i]
            if neg_qw in sh_keys or pos_qw in sh_keys:   # ȥ��
                continue
            time.sleep(randint(0,5))    # ����ȴ�
            pos_res_bd = content_bd(getBaiduHit(pos_qw),pos_qw)
            pos_res_ss = []#content_ss(getSosoHit(pos_qw),pos_qw) 
            neg_res_bd = content_bd(getBaiduHit(neg_qw),neg_qw)
            neg_res_ss = []#content_ss(getSosoHit(neg_qw),neg_qw)
            conts = [ pos_res_bd,pos_res_ss,neg_res_bd,neg_res_ss]
            [ hit_save(conts[i],fps[i]) for i in range(4) ]    # ���δ洢HIT���
            shp[neg_qw]=None                                   # ��ȷд�ļ����ٱ��Ϊ�Դ���
            shp[pos_qw]=None
            sh_keys.extend([neg_qw, pos_qw])                   # ˢ��Key-list
            print '='*5,' Query-Neg:%s; Pos:%s; Fininsh:%d; Total:%d ' % (neg_qw,pos_qw,len(sh_keys),size*2), '='*5
        shp.sync()                      # ����״̬
        [ f.close() for f in fps ]      # �ر��ļ�
    return 
    #for nn in wpatt[1]:

if __name__ == "__main__":
    shp = shelve.open(r'./temp_hit.dat',writeback=True)
    tt = word_search(r'../resources/dict/sogou_dic_10W/total.dic',shp)    
    #html = get_html(url)
    #html = urllib.urlopen(url).read()
    #lst = result_list(html)
    '''tbd = <br> 
<table cellpadding="0" cellspacing="0" class="result" id="4" ><tr><td class=f><h3 class="t"><a onmousedown="return c({'fm':'as','F':'778717EA','F1':'9D73F1E4','F2':'4CA6BE6B','F3':'54E5243F','T':'1330872133','title':this.innerHTML,'url':this.href,'p1':4,'y':'7FDD2AF5'})" href="http://club.360buy.com/Repay/1000337760_c609f7a5-3092-4f73-9401-88e6e0cee3b5_1.html"target="_blank">...JS11054156 130--�·���Ư�������ǵȴ��·���<em>�����е㳤</em>--��Ʒ...</a> 
</h3><font size=-1>  ���㣺 ���ǵȴ��·���<em>���ӳ�</em>�˵㲻��һ��Ҳ�͵��ˣ����Ȳ������ش򿪺��ӣ��·���Ư����Ҳ����û�׵��ˡ� �����۶�������(0)û��(0)�ظ� ����д�ظ�...<br><span class="g">club.360buy.com/Repay/1000337760_c609f7a5 ... 2012-2-13  </span> - <a href="http://cache.baidu.com/c?m=9f65cb4a8c8507ed4fece76310478921494380143dd3d245389f8448e435061e5a06b4f974690d07d1c77e6600aa4c58e8e73106660722bccfcddb4dcabbe4292d832723706a801517d20eafbd4d23c323875a9fa513b0bea730c2f985d28f5344cd27066d8087d11c5f4ade2aad5467ecb1e842022917ad9b357289586028ef3436b7508fe2256f779686da4b3bc23dd11106e7ae22c338&p=8c798e15d9c04bb30be293605341&user=baidu&fm=sc&query=%A1%B0%C8%D5%D7%D3%D3%D0%B5%E3%B3%A4%A1%B1&qid=964edd40196d62d3&p1=4" target="_blank" class="m">�ٶȿ���</a><span class="liketip"id="like_4637840456762492430"></span> 
<br></font></td></tr></table><br> 
<table cellpadding="0" cellspacing="0" class="result" id="5" ><tr><td class=f><h3 class="t"><a onmousedown="return c({'fm':'as','F':'F78717EA','F1':'9D73F1E4','F2':'4CA6FE6B','F3':'54E5243F','T':'1330872133','title':this.innerHTML,'url':this.href,'p1':5,'y':'76CAF7FD'})" href="http://mcyao.blog.sohu.com/95544218.html"target="_blank">û�и��µ�<em>�����е�</em>��Զ</a> 
</h3><font size=-1> �������� ���ķ籩������������ ���鲻�õ�ʱ����õ��滺���� ����ȥ�Ⱦ� ����ȥ���衣��������һ����д�ռǡ����� ����� ��Ȼ��д...<br><span class="g">mcyao.blog.sohu.com/95544218.html 2008-7-25  </span> - <a href="http://cache.baidu.com/c?m=9f65cb4a8c8507ed4fece7631049862d4a0997634b878e482ac3933fd2390106506694ea7a7d0d0fd4c27a6101ac434bea876c34685d34f2c688de45caca983f598f3042750bf04005d269b8bd4732b722875b99b869e0ad873384afa2c4af5544b955&p=9c6e8e16d9c342ff57ec9138160782&user=baidu&fm=sc&query=%A1%B0%C8%D5%D7%D3%D3%D0%B5%E3%B3%A4%A1%B1&qid=964edd40196d62d3&p1=5" target="_blank" class="m">�ٶȿ���</a><span class="liketip"id="like_7904846776507953656"></span> 
<br></font></td></tr></table> <span class="nums" style="margin-left:120px">�ҵ���ؽ��Լ4,050��</span></p>

    tss=<div id="sInfo">������Լ694��������ʱ0.001��</div><li loc="3"><div id='box_0_2' class="selected boxGoogleList" ><h3><a href="http://bbs.city.tianya.cn/tianyacity/content/5158/1/42257.shtml"  class="tt tu" onClick="reportUrl(this,'1','3');st_get(this,'w.r',3,0,2);" target="_blank">
�޻���<em> ����</em><em>�е�</em><em>��</em>_���ǽ���_��������</a></h3><p class="ds">�޻���<em>����</em><em>�е�</em><em>��</em>_���ǽ���_��������...η��������֮�乹���ķ��飬�Ͼ���Զ�볾�����н���������������ʵ��˿�����ζ���δ��д�����ģ��ѳ��ζ�����ֻ��ͽ�Ͷ�����...</p>
<div class="result_summary"><div class="url"><cite>bbs.city.tianya.cn/tianyacity/content/51...&nbsp;2011-06-08</cite>-<a href="http://snapshot.soso.com/snap.cgi?d=3182047034122948132&w=%22%C8%D5%D7%D3%D3%D0%B5%E3%B3%A4&u=http://bbs.city.tianya.cn/tianyacity/content/5158/1/42257.shtml" target="_blank" onClick="st_get(this,'w.r.cache',3);">����</a></div><div class="sp"><span class="line">-</span>
<span class="summaryshare" id="sws_0_2"><span class="yl1" onFocus="blur();">����</span></span><span class="line2">-</span><span class="preview" id="pws_0_2">
<span class="iPre" onFocus="blur();">Ԥ��</span></span></div></div><div class="highLight"></div></div>                              </li>
<li loc="4"><div id='box_0_3' class="selected boxGoogleList" ><h3><a href="http://thomas199112.blog.163.com/blog/static/118652493201132642429337/"  class="tt tu" onClick="reportUrl(this,'1','4');st_get(this,'w.r',4,0,2);" target="_blank"><em>����</em>
<em>�е�</em><em>��</em>-Thomas����־-���ײ���</a></h3><p class="ds"><em>����</em><em>�е�</em><em>��</em>,thomas�����ײ���,�� �� ��,... ��ǰ��������ӹ��úܿ죬���ڿ�ʼ�����е㳤�ˡ����ܶ���һ����Ӧ�Ĺ��̡�Ը���ĵ�ƽ�����úöɹ�������ӡ�...</p>
<div class="result_summary"><div class="url"><cite>thomas199112.blog.163.com/blog/static/11...&nbsp;2011-04-26</cite>-<a href="http://snapshot.soso.com/snap.cgi?d=18413761986596144596&w=%22%C8%D5%D7%D3%D3%D0%B5%E3%B3%A4&u=http://thomas199112.blog.163.com/blog/static/118652493201132642429337/" target="_blank" onClick="st_get(this,'w.r.cache',4);">����</a></div><div class="sp"><span class="line">-</span><span class="summaryshare" id="sws_0_3"><span class="yl1" onFocus="blur();">����</span></span><span class="line2">-</span><span class="preview" id="pws_0_3"><span class="iPre" onFocus="blur();">Ԥ��</span></span></div></div><div class="highLight"></div></div>                              </li>
    '''
    #dwg = [[['"\xd6\xd0\xb9\xfa\xb6\xe0 \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xb8\xdf \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xba\xf1 \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xc9\xee \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xd6\xd8 \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xc7\xbf \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xbf\xed \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xb3\xa4 \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xb4\xd6 \xd4\xf5\xc3\xb4\xb0\xec"', '"\xd6\xd0\xb9\xfa\xb4\xf3\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xb6\xe0\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xb8\xdf\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xba\xf1\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xc9\xee\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xd6\xd8\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xc7\xbf\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xbf\xed\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xb3\xa4\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xb4\xd6\xc1\xcb\xb5\xe3"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xb4\xf3"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xb6\xe0"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xb8\xdf"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xba\xf1"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xc9\xee"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xd6\xd8"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xc7\xbf"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xbf\xed"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xb3\xa4"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xb5\xe3\xb4\xd6"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xb4\xf3"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xb6\xe0"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xb8\xdf"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xba\xf1"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xc9\xee"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xd6\xd8"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xc7\xbf"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xbf\xed"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xb3\xa4"', '"\xd6\xd0\xb9\xfa\xd3\xd0\xd0\xa9\xb4\xd6"']]]
    #word_search(dwg)
    shp.close()

