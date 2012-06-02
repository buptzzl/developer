# coding=gbk
from util_file import Dir_File
from util_list import LineOperator
''' TODO:���ǲ��� docID-word:score �����ݽṹ��� '''

class UtilWork:
    ''' ���밴COAE-gold-task1�ļ��ṹ����𰸵�list '''
    def __init__(self, fpath):
        self.path = fpath
        self.list = []
        self.content = Dir_File(self.path)  # �ļ���д
        self.filter = LineOperator()
    def oper_file(self,model='rb'):
        ''' ��ȡ�ļ���ת��Ϊ����list '''
        self.list = self.content.oper_file(self.path,model=model)
        #self.list = self.filter(data=self.list) # �õ�����list
    def oper_dir(self,pdir='',model='rb'):
        ''' ����Ŀ¼ '''
        pass
    def para_monitor(self,news=[]):
        pass

class Task1Mask:
    ''' ��COAE2011-����1��� '''
    def __init__(self,util_work):
        assert isinstance(util_work,UtilWork),"parameter error, must be instance of Class UtilWork"
        self.util = util_work
        self.util.oper_file()  
        self.list = self.util.list 
        self.dict = {}      # golden-result
        self.count = []     # score�Ľ��ͳ��
        self.cnt_words = 0
        self.sep_sent = '������'   # ע������ʽ
    def clean_list(self,data=None):
        ''' ��ϴlist����{docId:[[word1,score1,wd2,sc2,..,sentence],..]} '''
        #self.dict = {}          # ��ղֿ�
        dict_temp = {}
        if not data or not isinstance(data,list):  # ���������ݽ�������
            data = self.list; #print '='*10,len(self.list)
            self.dict.clear()          # ��ղֿ�
        for line in data:            
            lenl = len(line)
            # ��ϴ; ������һ����ע����word:val
            if lenl>3 and (line[-1] in ['1','0','-1']):   # '-1'����ʶ��Ϊdigit
                end = lenl
                while lenl>1 and (line[lenl-3] in ['1','0','-1']):  
                    lenl -= 2 # �����ҳ���ע��
                temp = line[lenl-2:end]     # �����ע�� ��
                self.cnt_words += (end-lenl+2)/2        # ��������1
                temp.append(''.join(line[1:lenl-2]))    # �������
                did = line[0]
                if did in dict_temp.keys():
                    dict_temp[did].append(temp)
                else:
                    dict_temp[did] = [temp]
        if len(self.dict)==0:    self.dict = dict_temp.copy() # ��ֵʱ��Ĭ�Ͻ������ô��ݣ�copy ���Ƹ���
        return dict_temp
    def score(self,result):
        ''' ����ͬ��dict�ṹ��result��֣���ͬ�ĵ��У��Ծ���Ϊ��Ԫ����level-1������ֵlevel-2 '''
        # ˵���� ��ֲ��裬 ���� ƥ��docid,֮��ƥ��word, �ټ�������������len_sent��1/4ǰ׺�Ƿ���ͬ����ͬ��Succ
        if not isinstance(result,dict) or len(result)==0:  return None
        if len(self.dict)==0:
            self.clean_list()
        hit_wd = 0                  # ��д�������
        hit_wd_trend = 0            # ��+����������
        gold_keys = self.dict.keys()
        # ����ƥ����ĵ�����
        keys = [ did for did in result.keys() if did in gold_keys ] #; print keys
        for k in keys:
            lines = self.dict[k] #;print 'key:',k   # gold-result
            for line in lines:       # �Ծ���Ϊ��Ԫ����ƥ��
                gwords = line[:-1] #;print 'G'*4,gwords   # ��ע�� ��
                gsent = line[-1]     # ����Դ
                pos0 = len(gsent)    # ����0�ĳ���
                #lines = self.dict[k]
                #cnt_sent = len(lines)
                for sent in result[k]:     # �Խ����ͬ���Ծ���Ϊ��Ԫ ���
                    res_sent = sent[-1]    #; print '='*4,sent
                    pos1 = len(res_sent)   # ����
                    slen= min(pos0,pos1)/4        # ���ھ���λ��[wd_pos-slen,wpos]������֤�ĳ���
                    print '#'*4,k,'test: ',sent[:-1],'golden: ',gwords      # TEST����֤�����ʼ���
                    for i in range(0,len(sent)-1,2):  # �Խ�����������е�ÿ����
                        swd = sent[i]  #;print '='*4,swd,'='*4,gwords,k                        
                        if swd in gwords:             # ��ƥ�䣬�жϾ���Ƭ���Ƿ�ƥ��                             
                            id_res = res_sent.find(swd) # ��ȡ����Ƭ�ε�����
                            beg = 0                   # Ƭ��Ĭ�ϴ����ֿ�ʼ,����ȡ1/4�ĳ���
                            if id_res>slen:
                                beg = id_res - slen ;
                            print '='*4,swd,'\n','test: ',res_sent,'golden: ',gsent; 
                            if res_sent[beg:id_res] in gsent:
                                hit_wd += 1    
                                print 'hit_wd+1',swd,gwords,'\n\t',res_sent[beg:id_res] # �����ڵľ���ƥ��
                                gscore_id = gwords.index(swd)+1     # ��֤��ֵƥ��
                                if sent[i+1] == gwords[gscore_id]:
                                    hit_wd_trend += 1    
                                    #print 'hit_wd_trend+1',[swd,sent[i+1]],gwords      # ��ֵ���
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
    

        
        
        

        
