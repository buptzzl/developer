# coding=gbk
''' @brief 北大论文 Task-1--评价对象拓展 的实现--公式中分子部分去除N  TODO:如何动态拓展, 随文档集而变化 '''
# TODO评价词实现：使用 word:line_ID的方式存储
import os, shelve
from util_file import Dir_File
from util_list import LineOperator, simplify

class Similary_Pku:
    def __init__(self, Pdir, words, codes='gbk'):
        ''' 录入文件|文件夹 中的内容到list '''
        assert isinstance(Pdir,str) and len(words)>0, "ERROR: Paramater's type "
        self.dir    = Pdir
        self.list   = []                        # 三级list: file->line->col
        self.files  = []                        # 遍历文件夹时，存放文件列表
        self.freq   = {}                        # 按self.list存放的freq单元{wrod:f}
        self.modify=False                    # list file 数据被修改标识
        #self.sentence = []                      # 两级list,一级list存放分词后的句子
        self.size   = 0                         # 总词数
        self.data_size = 0                      # 外部集合的sum()
        self.PMIwords = list(set(words))        # 计算相似度的词集合
        self.PMIfactors = {}                    # PMI词的分母，未做开方运算
        self.content = {}                       # 词的上下文(先得到list->再有dict),按PMI得特征向量
        self.simi   = {}                          # 目标词的
        self.window = 2                         # 上下文词窗口长度
        self.decomp = True                      # 标志key是否无POS 仅为汉字
        self.codes = codes
        #if len(data)!=0:            return None
        tdir = Dir_File(Pdir)
        if os.path.isdir(Pdir):
            temp = tdir.key_value(model='rb')       # 返回dict，将K-V分别转换为list
            self.files = temp.keys()
            self.list = [ temp[f] for f in self.files ]  
        else:
            self.files = [Pdir]
            self.list = [tdir.oper_file(Pdir)]
        for i in range(len(self.list)):
            l = [ l for l in self.list[i] if len(l)>2 ]    # 过滤list,长度>2
            self.list[i] = l
        # 检查编码是否一致; 要求list中的第一个单元非空
        assert words[0].decode(self.codes) and self.list[0][0][0].decode(self.codes), "init::ERROR: PMIwords or file's code-type different" 
    def add_data(self, ll, ff):
        ''' 扩充相同结构的数据集 '''
        if not isinstance(ll,list) or not isinstance(ff,list) or (len(ll)==0 and len(ff)==0):
            return False
        self.files.extend(f)
        assert ll[0][0][0].decode(self.codes),"add::ERROR: different codes type! "
        self.list.extend(ll)
        self.modify = True          # 设置标识位
    def count(self, decomp=True, sep='/', pos=0):
        ''' 统计list各个原子的freq; 返回一级list; 默认指定decomp:简化键为汉字 '''
        self.decomp = decomp                        # 记录key的索引特征
        temp = simplify(self.list)                  # list结构降维至词一级
        cnt = 0                                     # 数量校验; @ADD:3/26 当decomp=True时，可能出现异常
        self.size = len(temp)
        for w in temp:
            if w not in self.freq.keys():           # 仅统计一次
                key = w                
                if decomp:
                    try:                        key = w.split(sep)[pos]
                    except Exception,err_info:  print 'Key decomposition Error',err_info,w,key
                self.freq[key]=temp.count(w)                       # 使用list的count()
                cnt += int(self.freq[key])
        print "coun::CHECK: \nlist_size:%d =? count()_size:%d" % (len(temp),cnt)
        return 
    def context(self, decomp=True):
        ''' 统计目标词的上下词序列|不含POS,含目标词 '''
        if len(self.PMIwords)==0 : return None
        pmiw = set(self.PMIwords)  #   ([ w for w in self.PMIwords if w in self.freq.keys() ])
        for w in pmiw:             # 初始化
            self.content[w]=[]
        sentences = simplify(self.list,True,1)          # 将文档集降维至句子集
        if decomp:                 # 文件中有POS，需要清洗
            for i in range(len(sentences)):             # 清洗掉POS部分，仅保留汉字
                l = sentences[i]
                if len(l)>0:
                    sentences[i] = [ w.split('/')[0] for w in l if w.find('/')!=-1 ]
        #return sentences                            
        for line in sentences:
            for w in set(line).intersection(pmiw):      # 交集
                wid = line.index(w)
                beg = wid-self.window
                if beg<0 : beg = 0
                end = wid+self.window+1                 # +1：不包含词本身
                if end>len(line) : end = len(line)
                self.content[w].extend(line[beg:end])   # 加入上下文;统一放在置于一个list中
        return None
    def vector(self):
        ''' 由上下文计算PMI,形成特征向量;假设C、W之间无序 '''
        if len(self.content)==0:
            self.context()
        for w in self.content.keys():
            v = self.content[w] ;
            fw = self.freq[w]
            factor = 0
            temp = {}
            for cw in set(v):                              # 取上下文的词，去重，在词窗范围求freq
                #print "vector::PMI factor: content=%s; PMI_word=%s; \ntf(c,w)=%d, tot=%d, fc=%d, fw=%d" \
                #    % (cw,w,v.count(cw),self.size,self.freq[cw],fw)
                temp[cw]=float(v.count(cw))/(self.freq[cw]*fw) # PMI( C, Wi ) = Tf(C,Wi)/{ freq(C)*freq(Wi) }
                factor += temp[cw]**2
            factor -= temp[w]**2                               # 消除context()的结果中目标词的影响
            self.content[w] = temp                             # 更新目标词w的特征，形成向量；含目标词的 df=N/f_w
            self.PMIfactors[w] = factor                        # 分母
    def similary(self,link=' '):
        ''' 计算目标词之间的余弦相似度; 词间用字符串link连接 '''
        if len(self.PMIfactors)==0:
            self.vector()
        totk = self.content.keys()
        for i in range(len(totk)):
            ki = totk[i]
            for j in range(i+1, len(totk)):               # 由于simi[va,vb]=simi[vb,va] 简化计算
                kj = totk[j]
                vi = self.content[ki]
                vj = self.content[kj]                          # self.simi
                vset = set(vj.keys()).intersection(set(vi.keys()))
                if len(vset)==0:                        # 上下文无交集
                    self.simi[link.join(vi,vj)]=0
                    continue 
                simi = 1                    
                for kv in vset:
                    simi = simi*(vi[kv]*vj[kv])         # 叠加相似度
                self.simi[link.join([ki,kj])]=float(simi)/(self.PMIfactors[ki]*self.PMIfactors[kj])
        return
    def save_vector(self,path,data,ope_type = 'write'):
        ''' 存放中间结果 '''
        if not os.path.isfile(path) or not isinstance(data,dict): return None
        if ope_type == 'read':
            #TODO
            return True
        try:        # 默认写
            sh = shelve.open(path)
            for k in data.keys():
                sh[k] = data[k]
            sh.close()
        except Exception,data:
            print " 存放中间结果错误 ", data
            return False
    def monitor_parameter(self,data={}):
        ''' 监控参数与结果集 '''
        pass

if __name__=='__main__':
    p = r'./test/R000011.txt'
    pmis = [ '屏幕', '外观' ]
    tt = Similary_Pku(p,pmis)
    tt.count()
    tt.context()
    tt.similary()  
                

                





