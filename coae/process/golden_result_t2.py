# coding=gbk
'''COAE-T2�Ĵ�� ��DOCƥ��-> �̾�ƥ�䳤��-> ������; Ҫ���ļ�Ϊgold-res�ĸ�ʽ'''
import os, re, shelve

class Task2Mask:
    def __init__(self,gpath):
        self.dict = {}      # gold-res �ṹ{docid:[sentence1,score1,  s2,score2,..],..]}
        self.total=0        # gold ��������
        self.szie=0         # ��װ�ص����ݵ����۴�������
        self.hit=0          # result����ȷ��������
        self.hit_td=0       # result����ȷ�Ĵ�������������
        self.result=[]      # ƥ����[docid,sent,score,Gsent,Gsocre]
        self.dict = self.load(gpath)
    def __clean(self):
        self.hit=0          # result����ȷ��������
        self.hit_td=0       # result����ȷ�Ĵ�������������
        self.result=[]      # ƥ����[docid,sent,score,Gsent,Gsocre]        
    def load(self,path,sz_line=3):
        '''װ�ذ�gold-res�ĸ�ʽ(ÿ����sz_line��)�洢���ļ�'''
        f = file(path,'rb')
        tmp = {}
        for l in f:
            l=l.strip().split()
            if len(l)<sz_line: continue
            if len(l)>sz_line:              # ���ܳ����м��ж���հ��ַ��Ѿ��ӷָ���ʺϲ�֮
                l = l[0:1]+[''.join(l[1:-1])]+l[-1:]
            if l[0] in tmp.keys():
                tmp[l[0]].append(l[1:3])
            else:
                tmp[l[0]]=[l[1:3]]
        f.close()
        print "!!!! FINISH::load() path: %s, doc-size: %d !!!!"%(path,len(tmp))
        return tmp
    def score(self,result,percent=0.5):
        '''��֣����̾�ƥ�䳤��'''
        if not isinstance(result,dict) or result=={}:
            print "!!!! WARN::score() result unmatched !!!!"
            return False
        if self.hit!=0 or self.result!=[]:      # ���ǰ������
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
                    
