# coding=utf8
import os

class Task3Mask:
    ''' 对task3的结果打分 策略： 首先匹配docid,之后支持在gold-res中查找 评价词|对象|评价词组(基于答案中的评价关系是上下文)'''
    def __init__(self,pgold):
        self.dict = {}      # gold-res 结构{docid:[[obj1,trend1,score1,  obj2,trend2,..,sentence],..]}
        self.total=0        # gold 搭配总数
        self.szie=0         # 被装载的数据的评价搭配总数
        self.hit=0          # result的正确搭配总数
        self.hit_td=0       # result的正确的搭配与倾向总数
        self.result=[]      # 匹配结果[docid,wobj,wtrd,score_res,Gwobj,Gwtrd,Gsocre]
        self.dict = self.load(pgold)
    def __clean(self):
        '''计算前 清零结果集合'''
        self.hit=0          
        self.result={}
    def load(self,path,has_sent=True,atom_size=-3):
        ''' 装载清洗后的标准gold-res格式的文档'''
        tmp = {}
        f = file(path,'rb')
        for l in f:
            l = l.strip().split() ;
            if len(l)<4: continue            
            for i in range(len(l)-1,-1,atom_size):      # 逆序遍历找到第一个搭配 一个搭配单元的长度为3
                if l[i] not in ['-1','0','1']:  break
                    #print "!!!! TEST !!!! ",l[i]; break
            if has_sent:
                l[i] = ''.join(l[1:i+1])                   # 搭配前的内容视为句子
                l.append(l[i])
            #print i,l
            if l[0] in tmp.keys():
                tmp[l[0]].append(l[i+1:])
            else:
                tmp[l[0]] = [l[i+1:]]
        f.close()
        print "!!!! FINISH::load() path: %s, doc-size: %d !!!!"%(path,len(tmp))
        return tmp
    def score(self,result,check_sent=True):
        '''对与self.dict相同格式的result打分 返回匹配结果[docid,wobj,wtrd,score_res,Gwobj,Gwtrd,Gsocre]'''
        if not isinstance(result,dict) or result=={}:
            print "!!!! WARN::score() result unmatched !!!!"
            return False
        if self.hit!=0 or self.result!=[]:      # 清空前提条件
            self.__clean()
        gkeys = self.dict.keys()
        keys = [ did for did in result.keys() if did in gkeys] 
        for did in keys:
            #glines = self.dict[did]
            for line in result[did]:
                for ai in range(0,len(line),3):          # 从第一个原子开始遍历
                    for gl in self.dict[did]:            # 遍历gold-res的每个模式
                        # 按 评价词|评价对象分别在gold-res中出现为命中准则
                        t_hit = [ gi  for gi in range(0,len(gl)-2,3) \
                                  if line[ai] in gl[gi] and line[ai+1] in gl[gi+1] ]
                        if t_hit==[]: continue
                        if len(t_hit)!=1:                # 同一句子中出现多个命中结果，取第一个
                            print "!!!! WARN::score() multi-gold pattern is hit !!!!\n",line[ai:ai+3],gl[gi:gi+3]
                        if check_sent:                   # 要求句子级匹配
                            if ''.join(line[ai:ai+2]) in gl[-1]:    # 搭配在对应的句子中
                                self.hit+=1
                                if line[ai+2]==gl[gi+2]: # 倾向性匹配
                                    self.hit_td+=1
                        else:
                            self.hit+=1
                            if line[ai+2]==gl[gi+2]:     # 倾向性匹配
                                self.hit_td+=1
                        # 保存粗命中结果
                        tmp = [did]+line[ai:ai+3]+gl[gi:gi+2]
                        self.result.append(tmp)
                        break                    # 已在gold的doc的某个sent中命中，不再遍历剩余的sent 
        return self.result

if __name__=='__main__':
    tt=Task3Mask(r'../gold_result/task3_d.txt')
    test = tt.load(r'./test/R.txt',has_sent=False)
    
