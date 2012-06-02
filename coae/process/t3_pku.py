# coding=utf-8
import re, os
from util_file import Dir_File

# @brief 对file按sep分割 抽取tgt标志的列 空行为[]
def get_data( path,tgt=[],sep=None ):
    res = []
    if len(tgt)!=0:
        iid = tgt[0]        # 最大列号
        for i in tgt :
            if i>iid: iid=i;
    else: iid=False
    try:
        fp = open(path,'rb')
        for l in fp:
            tmp = l.strip().split(sep)
            if iid :
                if len(tmp)>=iid:
                    ll = [ tmp[i] for i in tgt ]
                else:
                    ll = []
            else: ll = tmp           # 保存完整的路径
            res.append( ll )
    except Exception:
        print "="*4," read file error! ","*"*4
    finally: fp.close()
    return res

class  PatternDrag:
    ''' PUK2011-T1实现，注意：self.split_sentences的列尾为简化的词性POS; 编码必须为code类型 '''
    def __init__(self, lines, pat_N=[], pat_A=[], code='gbk'):
        self.sentences = []           # 存放句子，无空句
        self.split_sentences = []     # 存放结构合并后的句子
        self.code_src = code          # src 文件的编码格式
        self.nword = [u'\u7684',u'\u4e4b',u'\u548c',u'\u4e0e']  #['的', '之', '和', '与' ]  # 编码问题
        self.adv_emo = [u'\u7684', r'\u5730', u'\u5f97']        #[的 地 得]
        if len(lines)==0 or not isinstance(lines,list):
            print '='*4,' empty data-set ', '='*4        
        else:
            self.__split_sent(lines)        # 对输入数据进行分句
        self.npattern = pat_N
        self.apattern = pat_A
        self.punc = ['wp']      # 标点符号的pos
        self.ude = ['u']        # 助词 的、得、地...
        self.verb = ['v']       # 动词
        self.adv = ['d']        # 副词
        self.ztai = ['z']       # 状态词，ICT特有标注
        self.guant = ['m'] # @ADD 4/24 数量词
        self.ppos = 1           # 词性POS 所在列
        # 所有待抽取的模式; N-n, A-a, V-v, U-ude, D-adv, B-begin, E-end, Z-z, #-其它  [ BVNA BVAE ]须单独考虑
        # ADD: v-n的v+  NVE  拓展*D*为*DD* ; 的 地 得 的模式单独实现
        self.emotpattern = ['ADDN', 'ADDVN', 'ADN', 'ADVN','ANE','DAN',
                            'NAE', 'NDA', 'NDDA', 'NDDVE', 'NDVE', 'NVAE', 'NVNA', 'NZAE',
                            'NAME','NVME',          # @ADD 4/24 conf置1的独特模式
                            'VAE', 'VDA', 'VDDA']
        self.emotmatch = []     # 匹配到模式的字序列
    def __split_sent(self, lines):
        ''' 将按列拆分的词组合成句子 '''
        if len(lines)==0 or not isinstance(lines,list):
            print "!!!! __split_sent::ERROR data unmatched !!!!", lines
            return []
        tmp = [] ;
        for l in lines:
            if len(l)<2:       # 新的分句
                if len(tmp)>2 :             # 开始记录新的一句前，原始句子长度>2则保存
                    self.sentences.append(tmp)
                tmp = []
                continue
            tmp.append(l)                   #一个原子单元
        return self.sentences
    def util_N(self, newl):
        '''@修正分词功能："的"+末尾词活用为N，合并词+标注 '''
        if len(newl)>3:                   # 至少3个词
            twds = [ w[0] for w in newl[:-1] ]
            #print '----', ' '.join(twds)
            try:
                u_twds = [ w.decode(self.code_src) for w in twds ] # 解码操作
                #print '~~~~ Decoded words: ', u_twds
                if u'\u7684' in u_twds :   # "的"字存在于句子中
                    u_twds.reverse()
                    de_id = u_twds.index(u'\u7684')
                    if 1<de_id and de_id<5:            # 规则：末尾词不是”的“,且最多连续3个词活用为N
                        de_words = u_twds[:de_id]
                        de_words.reverse()
                        utilN = ''.join(de_words).encode(self.code_src)   # 获得活用词组,更新词集
                        punc_tmp = newl[-1]         # 保存末尾标点
                        for i in range(de_id+1):
                            del newl[-1]
                        newl.append([utilN,'N','N'])# 插入新的词单元；句尾，无需更新flag
                        newl.append(punc_tmp)
                    #print '####',newl
            except Exception,data:
                print '!!!!  句尾词活用处理异常： ', data
        return newl
    def suffix_mark(self, atom, ppos):
        ''' 给词单元末尾添加V-E-U等之一的标记 '''
        if atom[ppos] in self.apattern or atom[ppos] in self.npattern:
            print "!!!! suffix_mark::WARN usefull word maybe droped!", atom[0],atom[1:]
            return atom
        if atom[ppos] in self.verb:     atom.extend('V')
        elif atom[ppos] in self.punc:   atom.extend('E')
        elif atom[ppos] in self.ude:    atom.extend('U')
        elif atom[ppos] in self.adv:    atom.extend('D')
        elif atom[ppos] in self.ztai:   atom.extend('Z')
        elif atom[ppos] in self.guant:  atom.extend('M')        # @ADD 4/24
        else :atom.extend('#')
        return atom
    def __process_head(self,atom,ppos):
        ''' 对子句的第一个词标注词性 '''
        if len(atom)<(ppos+1):
            print "!!!! __process_head::ERROR process data to short !!!!", atom
        flag = 0
        if atom[ppos] in self.apattern:
            atom.extend('A')
            flag = -1          # 刷新标志位
        elif atom[ppos] in self.npattern:
            atom.extend('N')
            flag = 1           # 刷新标志位
        else: atom = self.suffix_mark(atom,ppos)     # 打尾标注
        return [flag,atom]
    def pattern_succesive(self, ppos=1, wpos=0):
        '''识别分词后连续的词结构整合 eg:NN+的结构合并为N ; ppos为pos所在列索引 '''
        if len(self.sentences)==0:
            print '!!!! pattern_succesive::ERROR sentences-set is emtpy !!!!'
            return False
        for line in self.sentences : #range(len(self.sentences)):
            tmp = self.__process_head(line[0][:],ppos)          # 处理子句首字
            flag = tmp[0]           # 存放前一个词的词性 A:-1; N:1            
            newl = [tmp[1]]         # 存放各匹配子句
            #print flag,newl; return #'==== SENTENCE :',''.join( [w[0] for w in line] )
            for atom in line[1:]:     # 遍历句子中的词；保证newl中至少有一个词
                #print 'W: ',atom[0],
                if newl[-1][ppos] in self.punc: # 一个子句
                    newl = self.util_N(newl)    # 处理“末尾词活用为N
                    self.split_sentences.append(newl)                     
                    # 处理句首第一个词
                    tmp = self.__process_head(atom,ppos) # @MOD 20120410
                    flag = tmp[0]
                    newl = [tmp[1]]
                    continue                
                elif atom[ppos] in self.apattern:
                    atom.extend('A')                #; print 'a'*8,atom[wpos],flag
                    if flag==-1:  # 连续出现A; 合并，改善分词
                        newl[-1][wpos] = newl[-1][wpos]+atom[wpos] #; print 'A'*8,newl[-1][wpos]#,atom[wpos]
                        continue  # 无需再插入该词
                    # 模式 d+a 
                    elif newl[-1][ppos]==self.adv:
                        newl[-1][wpos] = newl[-1][wpos]+atom[wpos] #; print 'D'*8,newl[-1][wpos],atom[wpos]
                        newl[-1][ppos] = atom[ppos]
                        newl[-1][-1] = 'A'   # 更新尾标
                        flag = -1
                        continue
                    flag = -1                # 当前词的标志位
                elif atom[ppos] in self.npattern:
                    atom.extend('N')               # ; print 'n'*8,atom[wpos],flag
                    if flag==1:   # 连续出现N
                        if len(newl[-1][wpos])<4 or len(atom[wpos])<4: #仅对之一为单字的情况作合并，改善分词
                            newl[-1][wpos] = newl[-1][wpos]+atom[wpos] #; print 'N'*8,newl[-1][wpos],atom[wpos]
                            continue  # 无需再插入该词
                    elif len(newl)>1:
                        # 模式 N-de-N 
                        n_flag = False      # 标志位                    
                        try:      # 两个 try 主要是考虑编码问题
                            tword = newl[-1][wpos].decode(self.code_src) 
                            if tword in self.nword:  n_flag = True
                        except Exception:
                            print "="*4,' decode chinese word error:',newl[-1][wpos],'='*4                        
                        if n_flag and newl[-2][ppos] in self.npattern:                  # 满足 N-de-N 
                            newl[-2][wpos] = newl[-2][wpos]+newl[-1][wpos]+atom[wpos]
                            #print '-'*8,newl[-2][wpos],newl[-1][wpos],atom[wpos]       
                            del newl[-1]
                            flag = 1
                            continue
                    flag = 1
                else:
                    atom = self.suffix_mark(atom,ppos)      # 打尾标注
                    flag = 0            # 刷新标志位
                if atom[-1]=='V' and newl[-1][-1]=='V' and len(atom[wpos])<4 and len(newl[-1][wpos])<4:            # 对单字动词合并，改善分词
                    newl[-1][wpos] = ''.join([newl[-1][wpos],atom[wpos]])  #; print newl[-1][wpos],atom[wpos]
                else:                newl.append(atom)    # 不满足合并规则，插入该词
            newl = self.util_N(newl) #; print '---- END: ', ' '.join([w[0] for w in newl])
            self.split_sentences.append(newl)        # 刷新句子结构
        return True
    def emotion_adv(self,sent):
        ''' 抽取ADV(的|地|得)情感模式; 返回匹配模式表 '''
        if len(sent)<2:
            print "!!!! emotion_adv::ERROR  pattern's size<2 !!!!", sent
            return []
        patt_1 = self.adv_emo[0]    # 的
        patt_2 = self.adv_emo[1]    # 地
        patt_3 = self.adv_emo[2]    # 得
        res = []
        for i in range(1,len(sent)-1):              # 搜索整个句子的非首尾词
            w = sent[i][0]          
            w = w.decode(self.code_src)             
            if w==patt_1 and sent[i-1][-1] in 'AN':
                if sent[i+1][-1] in 'AN':
                    # print type(sent), sent
                    res.append(sent[i-1:i+2])
                elif len(sent[i:])>2 and sent[i+1][-1]=='V' and sent[i+2][-1]=='N':
                    res.append(sent[i-1:i+3])
            elif w==patt_2 and sent[i-1][-1]=='A':
                if sent[i+1][-1]=='V':
                    tmp_end = 2
                    if sent[i+2][-1]=='N': tmp_end += 1
                    res.append(sent[i-1:i+tmp_end])
            elif w==patt_3 and sent[i-1][-1]=='V' and sent[i+1][-1]=='A':
                res.append(sent[i-1:i+2])
            if len(res)>0 and len(res[-1])<2:
                #print "!!!! emotion_pattern::WARN drop useless-patt: ",res[-1]
                del res[-1]
        return res
    def emotion_pattern(self):
        ''' 抽取T-3模式，3级list '''
        if len(self.split_sentences)==0 :
            print "!!!! emotion_pattern::empty split_sentences, try it ===="            
            if not self.pattern_succesive(): return []
        for s in self.split_sentences:      # 遍历每个句子
            poss = ''.join([ w[-1] for w in s])
            if poss[0:3]=="VNA" or poss[0:3]=="VAE":    # 搜寻句首的模式
                self.emotmatch.append(s[0:3])
                #print '**** VNA|VAE: ',self.emotmatch[-1]
            for pp in self.emotpattern :                # 匹配模式列表
                lenpp = len(pp)
                bpp = 0
                for i in range(poss.count(pp)):     
                    bpp += poss[bpp:].index(pp)     # 获得匹配到的起点下标
                    self.emotmatch.append(s[bpp:bpp+lenpp])
                    #print '**** %s: '%pp,self.emotmatch[-1]
            emo_adv = self.emotion_adv(s)
            if len(emo_adv)>0 and len(emo_adv[0])>1: self.emotmatch.extend(emo_adv)
        return self.emotmatch
    def format_emo(self,data):
        ''' 将3级list插入[], 降为2级list'''
        if (not isinstance(data,list) or len(data)==0) or \
           (not isinstance(data[0],list) or len(data[0])==0) or \
            not isinstance(data[0][0],list) :
            return False
        res = []
        for l in data:
            res.extend(l)
            res.append([])              # 分割标志
        return res
    def get_emotmatch(self):
        return self.emotmatch
    def get_split_sent(self):
        return self.split_sentences
    def get_sent(self):
        return self.sentences
    def monitor_params(self,params={}):
        res = { 'npattern':self.npattern,
                'apattern':self.apattern,
                'nword':self.nword,
                'punc' :self.punc,
                'ude'  :self.ude,
                'verb' :self.verb,
                'adv'  :self.adv,
                'ztai' :self.ztai,
                'guant':self.guant,         # @ADD 4/24
                'emotpattern':self.emotpattern,
                'code_src':self.code_src
                }
        if len(params)==0 :  return res               # 查询参数
        else:                               # 修改参数
            if not isinstance(params,dict):
                return {}                   # 错误时返回的标志
            kres = res.keys()
            for k in params.keys():         
                if k in kres and type(res[k])==type(params[k]):
                    res[k] = params[k]
            self.npattern = res['npattern'] ; self.apattern = res['apattern'] ;
            self.nword = res['nword'] ; self.punc = res['punc']; self.ude = res['ude']
            self.verb = res['verb'];
            self.adv = res['adv'];self.adv=res['adv']; self.guant=res['guant'];     # @ADD 4/24
            self.emotpattern = res['emotpattern']; self.code_src = res['code_src']
            return None

def format_rev(data, sep='/'):
    ''' 将ICT的list转换为HIT格式: [ [s1_w1,s1p1],..[],[s2_w1,s2p1]...] '''
    if len(data)==0:
        return [[]]
    res = []
    for l in data:
        if len(l)!=0:
            l = [ w.split(sep) for w in l if len(w)>2 ]     # 处理一个句子
            l.append([])                                    # 句子结束标志
            res.extend(l)                  
    return res

def save(para={},match=False):
    ''' 保存结果，match指示是否直接匹配字典 '''
    src_fp = r'../COAE2011_Corpus_All_Text/'     # r'./test' # 
    kind = ['seg4_fin', 'seg4_ent', 'seg4_dig']  #  ['temp'] #
    suf_save = '_pku3'                           # 新目录的后缀
    union_format = lambda x:x                    # 默认不做格式转换
    if len(para)!=0:
        kind = ['ict_fin','ict_ent','ict_dig']   # 使用ict文件源
        suf_save = '_pku3_ict'
        union_format = format_rev
    pos_N = ['ns','nz','nh','ni','n','j','ws','nl','nt']
    pos_A = ['a','b']
    for f in kind:
        src_p = os.path.join(src_fp, f)        
        odif = Dir_File(src_p)         
        sentences = odif.key_value(model='rb')      #; return sentences        
        data = {}   #; return sentences
        # print '==== len: %d ====' % len(sentences), sentences
        # TODO 优化类 PatternDrag 的代码，将其实例的说明提到for循环外，循环增加数据时，再处理增加的内容
        for k in sentences.keys():
            v = union_format(sentences[k])           #;    return v
            # print '==== src_fPath: %s/%s, lines-sum: %d' % (src_p,k,len(v))   
            emotion = PatternDrag(v, pos_N, pos_A)
            emotion.monitor_params(para)      # 修改参数
            tmp = emotion.emotion_pattern()   #; return tmp
            data[k] = emotion.format_emo( tmp )  #; return data[k]
        dst_p = os.path.join(src_fp,''.join([f,suf_save]))       # 一个类别的结果存放一个文件
        print "==== save():: write back data, path: %s,\n==== data-size: %d" % (dst_p,len(data))
        odif.key_value(data, 'wb', dst_p)
    return
def save_one(data, pt=r'./test/aa'):
    fp = file(pt,'wb')
    tmp = []
    print '++++ DATA ++++\n',data
    for l in data:
        line = [ '\t'.join(j) for j in l ]
        tmp.append('\n'.join(line))  ;
        #print '==== TEST: ====\n', l,'\n',tmp #; return 
    fp.write('\n\n'.join(tmp))
    fp.close()
    
if __name__ == "__main__":
    tt = save()  # 抽取HIP的结果
    # 说明： N增加模式 nl ng; A增加模式 ad;ADV增加 u*; V增加 v*;
    ict_pos = { 'npattern':['n','nr','ns','nr1','nr2','vn','nrj','nrf','nsf','nt','nz','nl','ng'],
                'apattern':['a','an','ad'],  
                'punc' :['w','wj','ww','wt','wd','wf','wn','ws','wp'],
                'ude'  :['uzhe','ule','ude1','ude2','ude3','uyy','uls','uzhi','ulian'],
                'verb' :['v','vd','vi','vl','vf','vx'],
                'adv'  :['d','ulian','uyy','ule'],
                'guant': ['m','mq']
                }
    tt = save(ict_pos)  # 抽取ICTCLAS的结果
    '''t = r'./t_patterndrag'
    tt = r'E:\project\coae\COAE2011_Corpus_All_Text\ict_fin\F06874.txt'
    sentences = get_data(tt)
    sentences = format_rev(sentences)
    pos_N = ['ns','nz','nh','ni','n','j','ws',    'nl','nt']
    pos_A = ['a','b']
    et = PatternDrag(sentences,pos_N,pos_A)
    et.monitor_params(ict_pos)
    #sent_sp = et.get_sent()
    #save(r'./t_patterndrag',sent_sp)
    sent_split = et.pattern_succesive()
    #sent_split = et.get_split_sent()
    sent_emo = et.emotion_pattern()
    #save_one(sent_emo)
    '''
