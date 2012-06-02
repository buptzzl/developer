# coding=utf8
''' 实现pku任务1中提到的使用词典直接匹配分词结果 '''
# TODO 优化： 对两字词的匹配，按POS值过滤
import os
from util_file import Dir_File
from util_dict import update_value

class SegmentFilter:
    ''' 基于单极性n|p的词典（支持长度过滤），2gram匹配分词结果，存放格式[pre1,pre2,term,suf1,suf2]末尾插入Docid '''
    def __init__(self,dict_path,save_pt,line=None,params=None):        
        para={'dict_type':'n','code':'gbk','num':3,'wpos':0,'mpos':1,'len':2,'npos':['n'],'vpos':['v']}    # 默认的初始化参数
        if params: para = update_value(para,params,True)                    # 更新初始化参数
        self.codes = para['code']   # 文件的编码方式        
        self.num = para['num']      # 命中词的前后词数量
        self.wpos = para['wpos']    # list中字的pos
        self.mpos = para['mpos']    # list中POS的pos
        self.len_dict=para['len']   # 字典原子的字节数下限
        self.npos = para['npos']              # 字典命中词的名词POS列表
        self.vpos = para['vpos']              # 动词POS列表
        self.dict_type=para['dict_type']      # 字典的极性
        self.spath = save_pt        # 命中结果的保存文件地址
        self.line = line            # 待分析的句子
        if self.line:   self.__normal()
        self.dict = []              # 字典的内容
        self.hit = []               # 命中结果        
        self.oper = Dir_File(os.path.dirname(save_pt))  # 提供文件操作，目录默认为字典的上级目录        
        if line:        # 编码检测
            self.line[0][wpos].decode(self.codes)        
        if isinstance(dict_path,list):
            fps = [ file(i,'rb') for i in dict_path ]
        else: fps = [ file(dict_path,'rb') ]
        for l in fps:
            tlines = [ one.strip() for one in l.readlines() if len(one.strip())>self.len_dict] # 过滤单字
            l.close()
            assert tlines[0].decode(self.codes),"!!!! init::ERROR try decode failed !!!! "
            self.dict.extend(tlines)
    def update(self,line,save=None):
        if not isinstance(line,list) or len(line)==0:
            print "!!!! update::WARN date's size too small !!!!"
        line[0][self.wpos].decode(self.codes)    # 编码检验
        self.line = line
        self.__normal()
        if save and isinstance(save,str): self.spath = save
    def save(self,path=None,mode='ab'):
        ''' 两级list存储 '''
        if len(self.hit)==0:
            print "!!!! save::WARN hit-data is empty !!!!"
            return
        self.hit.append(['',''])          # 插入空白原子，ab模式写文件时实现换行
        if path:self.oper.oper_file(path,mode,self.hit) 
        else:   self.oper.oper_file(self.spath,mode,self.hit)
        self.hit = []   # 清空数据
    def __normal(self):
        ''' 数据规划化：删除长度<2的单元 '''
        if len(self.line)==0: return False
        self.line = [ l for  l in self.line if len(l)>1 ]
        return True
    def __pos_filter(self,atom):
        ''' 对N,V词集等做过滤 TODO:计算各类别的置信度 '''
        if len(self.npos)==0 or len(self.vpos)==0:
            print "!!!! __pos_filter::ERROR POS-values is un-initialed !!!!"
            return False                             # 不进行POS合法性检验
        if len(atom)>self.mpos and atom[self.mpos] in self.npos or atom[self.mpos] in self.vpos:
            if self.dict_type=="p":                     # 对V|N 过滤掉正极性
                return True
        return False
    def __segment_combine(self,wid,sz,size=6,punc='w',apos='a'):
        ''' 对长度(非字数)<size的词进行前合并|修改POS值， 再进行匹配 '''
        if wid==0 or sz==1 or \
           punc in self.line[wid-1][self.mpos]  or\
           len(self.line[wid][self.wpos])>size: return False
        tword = ''.join([self.line[wid-1][self.wpos],self.line[wid][self.wpos]])
        if tword in self.dict:
            self.line[wid][self.wpos] = tword ; self.line[wid][self.mpos]=apos
            return True
        return False        
    def match(self,punc='w',fname=''):
        ''' 匹配两级list的句子，查找是否有命中 mpos为list中POS的pos；命中时在此处插入fname'''
        if len(self.line)==0:
            print "!!!! match::ERROR data is empty !!!!",fname
            return False
        assert self.__normal(),"!!!! normal::ERROR !!!!"
        sz = len(self.line)
        hit_pos = -1                              # 记录前一次匹配的词id
        for i in range(sz):
            atom = self.line[i][:] #; print atom[self.wpos],atom; return
            if self.__pos_filter(atom): continue # 过滤
            if atom[self.wpos] in self.dict:
                hit_pos = i                             
                self.line[i].append(fname)            # 插入源文件名
                beg = 0
                if i>self.num: beg = i-self.num
                # 搜索标点符号的位置
                tmp = [l for l in range(beg,i) if punc in self.line[l][self.mpos] ]
                if len(tmp)!=0: beg = tmp[-1]+1       # 子句的句首
                end = i+self.num 
                if end>sz: end = sz
                tmp = [l for l in range(i+1,end) if punc in self.line[l][self.mpos] ]
                if len(tmp)!=0: end = tmp[0]          # 子句的句尾
                self.hit.extend(self.line[beg:end]) ;
                #print "hit get one, beg: %d, end: %d" % (beg,end),atom,self.line[beg:end]
                self.hit.append([])         # 插入空行
            # 分词优化： 仅在前2个词都没命中词典时，引入合并词命中, 且仅合并前后最多各一词
            elif i and (i-hit_pos)>2 and self.__segment_combine(i,sz,size=6,punc=punc):
                hit_pos = i  ; print "combine hit ONE: %d, "%i,self.line[i],
                beg = i-2
                if punc in self.line[beg][self.mpos]: tmp = [self.line[i]]
                else:   tmp = [ self.line[beg],self.line[i] ]
                end = i+1
                if end<sz and punc not in self.line[end][self.mpos]: tmp.append(self.line[end])
                self.hit.extend(tmp) 
                self.hit.append([])                 
        print "++++ match::OVER file: %s, hit-result words: %d ++++"%(fname,len(self.hit))
        return True                 
    def multi_match(self,data=[],punc='w',fname=''):
        ''' match() 的多句子版本 '''
        if len(data)==0 :
            print "!!!! multi_match::WARN data is empty !!!!"
            return False
        pos = -1
        for i in range(len(data)):          #  找到第一个非空原子，用于判断是否非3级list
            if len(data[i])!=0:
                pos = i;
                break
        if pos == -1: return False          # 数据为空
        if not isinstance(data[pos][0],list):
            self.line = data[pos:]
        else:                               # 句子级的list降维
            tmp = [ ]
            for l in data[pos:]: tmp.extend(l)
            self.line = tmp
        self.match(punc,fname)

def save(ictF=False):
    ''' 直接匹配字典，保存结果 '''
    from util_file import Dir_File
    from t3_pku import format_rev
    # 装载词典； 设置存储文件名
    rneg = [r'./test/remark_neg.txt',r'./test/feel_neg.txt'] ;
    wneg = 'hit_neg.txt'; 
    rpos = [r'./test/remark_pos.txt',r'./test/feel_pos.txt'] ;
    wpos = 'hit_pos.txt';
    para={'code':'gbk','num':3,'wpos':0,'mpos':1,'len':2,'dict_type':'',
          'npos':['n','nd','nh','ni','nl','ns','nt','nz'],'vpos':['v']}
    mpos=1; punc='w';  # multi_match()函数的参数
    src_fp = r'../COAE2011_Corpus_All_Text/'     # r'./test' # 
    kind = ['seg4_fin', 'seg4_ent', 'seg4_dig']  #  ['temp'] #
    union_format = lambda x:x                    # 默认不做格式转换
    if ictF:
        kind = ['ict_dig','ict_fin','ict_ent']   # 使用ict文件源
        wneg = 'hit_neg_hit.txt'
        wpos = 'hit_pos_hit.txt'
        para['npos']=['n','nr','nr1','nr2','nrj','nrf','ns','nsf','nt','nz','nl','ng']
        para['vpos']=['v','vn','vf','vx','vi','vl','vg']
        union_format = format_rev 
    #pos_N = ['ns','nz','nh','ni','n','j','ws','nl','nt']
    #pos_A = ['a','b']
    for f in kind:
        src_p = os.path.join(src_fp, f)
        saveN = os.path.join(src_fp,'_'.join([f,wneg]))
        saveP = os.path.join(src_fp,'_'.join([f,wpos])) #; print src_p, saveN, saveP; return
        para['dict_type']='n'
        m_neg = SegmentFilter(rneg,saveN,None,para)
        para['dict_type']='p'
        m_pos = SegmentFilter(rpos,saveP,None,para)        
        odif = Dir_File(src_p)         
        sentences = odif.key_value(model='rb')       #; return sentences        
        data = {}   #; return sentences
        for k in sentences.keys():
            v = union_format(sentences[k])  #; print k         #;    return v
            m_neg.multi_match(v,punc,fname=k)
            m_pos.multi_match(v,punc,fname=k)   ;
            #if k=="D08934.txt":return [m_pos,sentences[k]]
            m_neg.save()
            print "---- save: %s,data-size: %d ----"%(m_pos.spath,len(m_pos.hit))
            m_pos.save()
            #return m_neg

if __name__ == '__main__':
    #s = save()
    s1 = save(True)
    '''dr = [r'./test/remark_neg.txt',r'./test/feel_pos.txt']
    sv = r'./test/hit_segment.txt'
    tt = SegmentFilter(dr,sv)
    dr = r'../COAE2011_Corpus_All_Text/ict_dig/D08934.txt'
    #dr = r'./test/R000011.txt'
    f = file(dr,'rb')
    l = [ i.strip().split() for i in f.readlines() ]
    f.close()
    for i in range(len(l)):        
        l[i] = [ j.split('/') for j in l[i] ]
    tt.multi_match(l,fname=dr)
    #for i in range(len(l)):
    #    line = l[i]
    #    l[i] = [ j.split('/') for j in line]    
    #    tt.update(l[i])
    #    tt.match(fname='R000011.txt')
    tt.save()
    '''
