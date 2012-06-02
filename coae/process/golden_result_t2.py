# coding=gbk
'''COAE-T2的打分 按DOC匹配-> 短句匹配长句-> 倾向性; 要求文件为gold-res的格式'''
import os, re, shelve

class Task2Mask:
    def __init__(self,gpath):
        self.dict = {}      # gold-res 结构{docid:[sentence1,score1,  s2,score2,..],..]}
        self.total=0        # gold 搭配总数
        self.szie=0         # 被装载的数据的评价搭配总数
        self.hit=0          # result的正确搭配总数
        self.hit_td=0       # result的正确的搭配与倾向总数
        self.result=[]      # 匹配结果[docid,sent,score,Gsent,Gsocre]
        self.dict = self.load(gpath)
    def __clean(self):
        self.hit=0          # result的正确搭配总数
        self.hit_td=0       # result的正确的搭配与倾向总数
        self.result=[]      # 匹配结果[docid,sent,score,Gsent,Gsocre]        
    def load(self,path,sz_line=3):
        '''装载按gold-res的格式(每行有sz_line列)存储的文件'''
        f = file(path,'rb')
        tmp = {}
        for l in f:
            l=l.strip().split()
            if len(l)<sz_line: continue
            if len(l)>sz_line:              # 可能出现中间有多个空白字符把句子分割开，故合并之
                l = l[0:1]+[''.join(l[1:-1])]+l[-1:]
            if l[0] in tmp.keys():
                tmp[l[0]].append(l[1:3])
            else:
                tmp[l[0]]=[l[1:3]]
        f.close()
        print "!!!! FINISH::load() path: %s, doc-size: %d !!!!"%(path,len(tmp))
        return tmp
    def score(self,result,percent=0.5):
        '''打分：按短句匹配长句'''
        if not isinstance(result,dict) or result=={}:
            print "!!!! WARN::score() result unmatched !!!!"
            return False
        if self.hit!=0 or self.result!=[]:      # 清空前提条件
            self.load()
        gkeys = self.dict.keys()
        keys = [ did for did in result.keys() if did in gkeys] ; print keys
        for did in keys:
            for line in result[did]:
                l_res = len(line[0])
                Fhit=False
                for gl in self.dict[did]:
                    lenG=len(gl[0])
                    #if did=='D01384.txt' or did=='D01383.txt':
                    #    print "!!!! res: %s;\n gold: %s"%(line,gl)
                    if lenG>l_res and line[0] in gl[0]:
                        Fhit = True
                    elif gl[0] in line[0]:
                        Fhit = True
                    if Fhit:
                        #print '!!!! HIT-one !!!!', did, line
                        self.hit+=1
                        if line[-1]==gl[-1]:
                            self.hit_td+=1
                        self.result.append([did,line[0],line[1],gl[0],gl[1]])
                        break
        return self.result

if __name__=='__main__':
    t = Task2Mask(r'../gold_result/task2_d.txt')
    tmp = t.load(r'./test/R.txt')
    t.score(tmp)
                    
