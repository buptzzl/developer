# coding=gbk
from util_file import Dir_File
from util_list import LineOperator
''' TODO:考虑采用 docID-word:score 的数据结构打分 '''

class UtilWork:
    ''' 导入按COAE-gold-task1文件结构导入答案到list '''
    def __init__(self, fpath):
        self.path = fpath
        self.list = []
        self.content = Dir_File(self.path)  # 文件读写
        self.filter = LineOperator()
    def oper_file(self,model='rb'):
        ''' 读取文件，转换为两级list '''
        self.list = self.content.oper_file(self.path,model=model)
        #self.list = self.filter(data=self.list) # 得到两级list
    def oper_dir(self,pdir='',model='rb'):
        ''' 操作目录 '''
        pass
    def para_monitor(self,news=[]):
        pass

class Task1Mask:
    ''' 对COAE2011-任务1打分 '''
    def __init__(self,util_work):
        assert isinstance(util_work,UtilWork),"parameter error, must be instance of Class UtilWork"
        self.util = util_work
        self.util.oper_file()  
        self.list = self.util.list 
        self.dict = {}      # golden-result
        self.count = []     # score的结果统计
        self.cnt_words = 0
        self.sep_sent = '，。！'   # 注意编码格式
    def clean_list(self,data=None):
        ''' 清洗list；按{docId:[[word1,score1,wd2,sc2,..,sentence],..]} '''
        #self.dict = {}          # 清空仓库
        dict_temp = {}
        if not data or not isinstance(data,list):  # 对自身数据进行清理
            data = self.list; #print '='*10,len(self.list)
            self.dict.clear()          # 清空仓库
        for line in data:            
            lenl = len(line)
            # 清洗; 至少有一个标注对象word:val
            if lenl>3 and (line[-1] in ['1','0','-1']):   # '-1'不能识别为digit
                end = lenl
                while lenl>1 and (line[lenl-3] in ['1','0','-1']):  
                    lenl -= 2 # 迭代找出标注对
                temp = line[lenl-2:end]     # 插入标注对 组
                self.cnt_words += (end-lenl+2)/2        # 计算量加1
                temp.append(''.join(line[1:lenl-2]))    # 插入句子
                did = line[0]
                if did in dict_temp.keys():
                    dict_temp[did].append(temp)
                else:
                    dict_temp[did] = [temp]
        if len(self.dict)==0:    self.dict = dict_temp.copy() # 赋值时，默认进行引用传递；copy 则复制副本
        return dict_temp
    def score(self,result):
        ''' 对相同的dict结构的result打分：相同文档中，以句子为单元、词level-1、倾向值level-2 '''
        # 说明： 打分步骤， 首先 匹配docid,之后匹配word, 再检验两个句子中len_sent的1/4前缀是否相同，相同则Succ
        if not isinstance(result,dict) or len(result)==0:  return None
        if len(self.dict)==0:
            self.clean_list()
        hit_wd = 0                  # 情感词命中数
        hit_wd_trend = 0            # 词+分数命中数
        gold_keys = self.dict.keys()
        # 首先匹配出文档交集
        keys = [ did for did in result.keys() if did in gold_keys ] #; print keys
        for k in keys:
            lines = self.dict[k] #;print 'key:',k   # gold-result
            for line in lines:       # 以句子为单元进行匹配
                gwords = line[:-1] #;print 'G'*4,gwords   # 标注对 组
                gsent = line[-1]     # 句子源
                pos0 = len(gsent)    # 句子0的长度
                #lines = self.dict[k]
                #cnt_sent = len(lines)
                for sent in result[k]:     # 对结果，同样以句子为单元 打分
                    res_sent = sent[-1]    #; print '='*4,sent
                    pos1 = len(res_sent)   # 长度
                    slen= min(pos0,pos1)/4        # 用于句子位置[wd_pos-slen,wpos]内容验证的长度
                    print '#'*4,k,'test: ',sent[:-1],'golden: ',gwords      # TEST：验证两个词集合
                    for i in range(0,len(sent)-1,2):  # 对结果，遍历其中的每个词
                        swd = sent[i]  #;print '='*4,swd,'='*4,gwords,k                        
                        if swd in gwords:             # 词匹配，判断句子片段是否匹配                             
                            id_res = res_sent.find(swd) # 获取句子片段的区间
                            beg = 0                   # 片段默认从首字开始,否则取1/4的长度
                            if id_res>slen:
                                beg = id_res - slen ;
                            print '='*4,swd,'\n','test: ',res_sent,'golden: ',gsent; 
                            if res_sent[beg:id_res] in gsent:
                                hit_wd += 1    
                                print 'hit_wd+1',swd,gwords,'\n\t',res_sent[beg:id_res] # 词所在的句子匹配
                                gscore_id = gwords.index(swd)+1     # 验证分值匹配
                                if sent[i+1] == gwords[gscore_id]:
                                    hit_wd_trend += 1    
                                    #print 'hit_wd_trend+1',[swd,sent[i+1]],gwords      # 分值相等
        return [hit_wd,hit_wd_trend]
#    def

if __name__ == '__main__':
    uw = UtilWork(r'../gold_result/task1_d.txt')
    t_uw = UtilWork(r'./test/t.gold')
    t_uw.oper_file()
    task1 = Task1Mask(uw)
    tt = task1.clean_list(t_uw.list)
    dtot = task1.clean_list()
    res = task1.score(tt)
    

        
        
        

        
