# coding=utf-8
import os,sys 

# @brief  drop the unrecognized code's string
def unrecognize_drop( line,src='gbk',dst='utf-8',change=False ):
    while line.find('\xa1X')!=-1:
        line=line.replace('\xa1X',' ')              # drop 全角空格
    tmp = '' ;
    flag = True                  # 标志转码校验继续，去除可能的多个乱码
    while flag:
        try:
            tmp=line.decode(src)
            tmp=tmp.encode(dst)
            flag = False         # 转码成功，复位标志符
        except (UnicodeDecodeError, UnicodeEncodeError),data:
            err=sys.exc_info() ; #print "content decoded from GBK error! path: %s" % path
            err_pos=err[1][2:4]; # get the decode error position
            line=line[:err_pos[0]]+line[err_pos[1]:] 
            print "!!!! INFO::unrecognize_drop() code-chansfer-error: %s!!!!\nbeg=%d, end=%d,\n%s"%(
                data,err_pos[0],err_pos[1],line[err_pos[0]:err_pos[1]])
    if change: line=tmp
    return line

# @brief  对文件夹按编码转换是否能够正常进行， 删除对应的异常码字 可进行gbk->utf8转换 
def clean_doc( path,src='gbk',dst='utf-8',change=False ):
    #files=os.listdir(path)
    #for f in files:
    #    p=os.path.join(path,f)
        p = path
        fp=open( p,'rb' )
        cnt=''.join(fp.readlines())
        fp.close()
        cnt=unrecognize_drop(cnt,src,dst,change)          # change code to utf-8 
        fp=open(p,'wb')
        fp.write(cnt)
        fp.close()
        
def strQ2B(ustring):  
    """ 把字符串全角转半角 """  
    rstring = ""  
    for uchar in ustring:  
        inside_code=ord(uchar)  
        if inside_code==0x3000:  
            inside_code=0x0020  
        else:  
            inside_code-=0xfee0  
        if inside_code<0x0020 or inside_code>0x7e:      #转完之后不是半角字符则返回原来的字符  
            rstring += uchar #;  print '#%s-%s*' % (inside_code,uchar)
        else:
            rstring += unichr(inside_code)  
    return rstring

def strB2Q(ustring):  
    """把字符串半角转全角"""  
    rstring = ""  
    for uchar in ustring:  
        inside_code=ord(uchar)  
        if inside_code<0x0020 or inside_code>0x7e:      #不是半角字符则返回原来的字符  
            rstring += uchar  
        if inside_code==0x0020: #除了空格其他的全角半角的公式为:半角=全角-0xfee0  
            inside_code=0x3000  
        else:  
            inside_code+=0xfee0  
        rstring += unichr(inside_code)  
    return rstring  

def fill( prefix,suffix,size,stuff ):
    pass 

# 对给定的文档执行给定的操作 oper  如果没指定 save 则写入原文件
def doc_conv( path,oper,save=None,utf8=True ):
    fp=open( path,'rb' )
    cont=''.join( fp.readlines() )
    fp.close()
    f_cod=False
    while (utf8 or f_cod):
        try:
            line=line.decode('gbk').encode('utf-8')
            utf8=False ; f_cod=False
        except UnicodeDecodeError:
            err=sys.exc_info() ; #print "content decoded from GBK error! path: %s" % path
            err_pos=err[1][2:4]; # get the decode error position
            line=line[:err_pos[0]]+line[err_pos[1]+1:]
            f_cod=True
    cont=eval(oper)(cont)
    if save:
        fp=open( save,'wb' )
    else:
        fp=open( path,'wb' )
    fp.write(cont)
    fp.close()

# @brief 分割 trec 格式的大文件为多个小文件, 文件名以 word 打头
def separa_doc( path,pth_sav,word='D' ):
    fp=open( path,'rb' )
    i=1 ;
    sfp=open( pth_sav+word+str(i),'wb' )
    for l in fp:
        sfp.write( l )
        if '</DOC>' in l or '</doc>' in l :
            sfp.close()
            i+=1
            sfp=open( pth_sav+word+str(i),'wb' )
    sfp.close()
    fp.close()

# @brief  对给定的文件、 按分隔符sep_tg抽取各列 分为两个文件存储 
def mark_sp( path,fir_sv,sec_sv ,sep_tg=' ',col_fir=[0]):
    fp=open( path,'rb' )
    fsp=open( fir_sv,'wb' )
    ssp=open( sec_sv,'wb' )
    for l in fp:
        l=[ i.strip() for i in l.split(sep_tg)]
        cn=len(l) ; tmp1=[] ; tmp2=[]
        if cn<col_fir[-1]:
            print "range beyond the limit. break!"; return -1
        for i in range(cn):
            if i in col_fir: tmp1.append(l[i])
            else:            tmp2.append(l[i])
        fsp.write( sep_tg.join(tmp1)+' \n' ) ; fsp.flush()
        ssp.write( sep_tg.join(tmp2)+' \n' ) ; ssp.flush()
    ssp.close()
    fsp.close()
    fp.close()
    return 0
            
def split_sentence(fpath, spath=None, sep=['。','！','？','：','　','.',';'], code='gbk'):
    ''' 对gbk的中文文档分句（忽略段落） pos标志指附带上分词后的标注结果 '''
    res = []            # 分句结果
    sep = [s.decode('utf8').encode(code) for s in sep ]
    try:
        fp = file(fpath,'rb')
        cont = fp.readlines()
        fp.close()          #; print cont ; return
        for l in cont:
            sents = [ i for i in sep if i in l ]
            if sents==[]:
                res.append(l)             # 仅有一个句子
                continue
            pos = [0]                     # 记录句尾的pos, 0 为哨兵
            for i in sents:
                stepi = len(i)
                for j in range(l.count(i)):
                    begi = pos[-1]
                    pos.append( (l[begi:].find(i)+begi+stepi) )
            pos.sort()
            if len(pos)==1:  print "!!!! ERROR::split_sentence() 至少应该有2个子句 !!!!"
            tmp = [] ;
            endi = -1       # 设置哨兵
            for i in pos[-1::-1]:
                tmp.append(l[i:endi].strip())     # 从后先前获得各子句，清洗空白字符
                endi = i
                del pos[-1]
            tmp.reverse()
            res.extend(tmp)
        if spath==None:
            spath = fpath        
        fp = file(spath,'wb')
        fp.write('\n'.join(res)) #; print 'write'
        fp.close()
    except Exception,data:
        print "!!!! split_sentence ERROR !!!! \nPATH: %s" % fpath, data
    finally:fp.close()
    return res

def split_goodbad(fpath,code='utf8',svpG=None,svpB=None,svpA=None):
    '''按句子中的good|bad字符分割句子中的内容 svpA为剩余未知内容的保存地址; 要求：其它内容仅在行首出现'''
    resG = []       # 存放good的句子
    resB = []
    resA = []
    gend = '优点：'.decode('utf8').encode(code)    # 模式; python文件的编码为utf8
    bend = '缺点：'.decode('utf8').encode(code)
    step = len(gend)
    f = file(fpath,'rb')
    lines = f.readlines()
    f.close() # ; print "====", gend,bend,lines[1]; return 
    for l in lines:
        l = l.strip()
        gcnt = l.count(gend)
        bcnt = l.count(bend)
        if gcnt==0 and bcnt==0:         # 1.无明显标志词，判为其他 other
            resA.append(l)      
        elif bcnt==0:                   # 2.无bad评价
            eid=l.find(gend)
            resA.append(l[:eid])        # 默认行首部分为other评价类型
            resG.append(l[eid:])
        elif gcnt==0:                   # 3.无good评价
            eid=l.find(bend)
            resA.append(l[:eid])
            resB.append(l[eid:])
        else:                           # 4.所有类别都存在
            glist=[(-1*step)] ; gtmp='' # gtmp存放 good 评论的片段; 注意空白起点用负数表示
            blist=[(-1*step)] ; btmp='' #; print '-----',glist, blist
            for i in range(gcnt):       # 统计所有 good 标志的pos
                ibeg = glist[-1]+step   # ;print 'good: \t',l[ibeg:].find(gend),ibeg,glist[-1],step
                glist.append( l[ibeg:].find(gend)+ibeg )
            for i in range(bcnt):
                ibeg = blist[-1]+step   # ;print 'bad : \t',l[ibeg:].find(bend),ibeg,blist[-1],step
                blist.append( l[ibeg:].find(bend)+ibeg )
            #print '====',gcnt,glist,bcnt,blist,len(bend),l.decode(code); return l
            if glist[1]>blist[1]:       
                resA.append(l[:blist[1]])
            else:
                resA.append(l[:glist[1]])
            last = -1                   # 记录上一次处理的最后POS
            for i in glist[-1:0:-1]:
                if blist[-1]>i:         # 需先处理 bad 评论
                    btmp=' '.join([l[blist[-1]:last],btmp])
                    last = blist[-1]
                    del  blist[-1]
                    gtmp=' '.join([l[i:last],gtmp])
                    last=i
                    del glist[-1]
                else:
                    gtmp=' '.join([l[i:last],gtmp])
                    last=i
                    del glist[-1]
                    if blist[-1]<0 : continue
                    btmp=' '.join([l[blist[-1]:last],btmp])
                    last = blist[-1]
                    del blist[-1]
            if glist[-1]>0 and blist[-1]>0:
                print "!!!! ERROR 至少两者有一个以被清空，请检查代码逻辑 !!!! \n",l,glist,blist
            if glist[-1]>0:
                gtmp=' '.join([l[glist[-1]:last],gtmp])
            elif blist[-1]>0:
                btmp=' '.join([l[blist[-1]:last],btmp])
            resG.append(gtmp)
            resB.append(btmp)
    tot = [resG, resB, resA]
    if svpG and svpB and svpA:      # 一个保存则全部都保存
        fs= [file(f,'wb') for f in [svpG,svpB,svpA] ]
        [ fs[i].write('\n'.join(tot[i])) for i in [0,1,2] ]
        [ f.close() for f in fs]
    return tot

if __name__=='__main__':
    for p in [r'../COAE2011_Corpus_All_Text/remarks_google/goo_bad_sp_uq',
              r'../COAE2011_Corpus_All_Text/remarks_google/goo_good_sp_uq',
              r'../COAE2011_Corpus_All_Text/remarks_google/goo_other_sp_uq']:
        clean_doc(p,'utf-8','gbk',change=True)
    '''doc_conv(r'..\COAE2011_Corpus_All_Text\seg_fin_trec.tot_clean',
    #         strQ2B,r'..\COAE2011_Corpus_All_Text\seg_fin_trec_clean')
    #separa_doc(r'..\COAE2011_Corpus_All_Text\seg_dig_trec.tot',
    #       r'..\COAE2011_Corpus_All_Text\temp\\','F')
    #clean_doc(r'..\task2\sentences_mark\split',False)
    #mark_sp( r'..\task2\full_label_data.txt',r'..\task2\sentence_mark',
    #         r'..\task2\words_mark','\t',[0])
    tt=split_goodbad(r'../resources/goo_remarks_nokia_iphone_ipad', code='utf8',
                     svpG=r'../resources/goo_good',
                     svpB=r'../resources/goo_bad',
                     svpA=r'../resources/goo_other')'''
    #tt = split_sentence(r'../resources/remarks_google/goo_other_u0',
    #               r'../resources/remarks_google/goo_other_sp',code='utf8')    
