# coding=gbk
''' @brief �������� Task-1--���۶�����չ ��ʵ��--��ʽ�з��Ӳ���ȥ��N  TODO:��ζ�̬��չ, ���ĵ������仯 '''
# TODO���۴�ʵ�֣�ʹ�� word:line_ID�ķ�ʽ�洢
import os, shelve
from util_file import Dir_File
from util_list import LineOperator, simplify

class Similary_Pku:
    def __init__(self, Pdir, words, codes='gbk'):
        ''' ¼���ļ�|�ļ��� �е����ݵ�list '''
        assert isinstance(Pdir,str) and len(words)>0, "ERROR: Paramater's type "
        self.dir    = Pdir
        self.list   = []                        # ����list: file->line->col
        self.files  = []                        # �����ļ���ʱ������ļ��б�
        self.freq   = {}                        # ��self.list��ŵ�freq��Ԫ{wrod:f}
        self.modify=False                    # list file ���ݱ��޸ı�ʶ
        #self.sentence = []                      # ����list,һ��list��ŷִʺ�ľ���
        self.size   = 0                         # �ܴ���
        self.data_size = 0                      # �ⲿ���ϵ�sum()
        self.PMIwords = list(set(words))        # �������ƶȵĴʼ���
        self.PMIfactors = {}                    # PMI�ʵķ�ĸ��δ����������
        self.content = {}                       # �ʵ�������(�ȵõ�list->����dict),��PMI����������
        self.simi   = {}                          # Ŀ��ʵ�
        self.window = 2                         # �����Ĵʴ��ڳ���
        self.decomp = True                      # ��־key�Ƿ���POS ��Ϊ����
        self.codes = codes
        #if len(data)!=0:            return None
        tdir = Dir_File(Pdir)
        if os.path.isdir(Pdir):
            temp = tdir.key_value(model='rb')       # ����dict����K-V�ֱ�ת��Ϊlist
            self.files = temp.keys()
            self.list = [ temp[f] for f in self.files ]  
        else:
            self.files = [Pdir]
            self.list = [tdir.oper_file(Pdir)]
        for i in range(len(self.list)):
            l = [ l for l in self.list[i] if len(l)>2 ]    # ����list,����>2
            self.list[i] = l
        # �������Ƿ�һ��; Ҫ��list�еĵ�һ����Ԫ�ǿ�
        assert words[0].decode(self.codes) and self.list[0][0][0].decode(self.codes), "init::ERROR: PMIwords or file's code-type different" 
    def add_data(self, ll, ff):
        ''' ������ͬ�ṹ�����ݼ� '''
        if not isinstance(ll,list) or not isinstance(ff,list) or (len(ll)==0 and len(ff)==0):
            return False
        self.files.extend(f)
        assert ll[0][0][0].decode(self.codes),"add::ERROR: different codes type! "
        self.list.extend(ll)
        self.modify = True          # ���ñ�ʶλ
    def count(self, decomp=True, sep='/', pos=0):
        ''' ͳ��list����ԭ�ӵ�freq; ����һ��list; Ĭ��ָ��decomp:�򻯼�Ϊ���� '''
        self.decomp = decomp                        # ��¼key����������
        temp = simplify(self.list)                  # list�ṹ��ά����һ��
        cnt = 0                                     # ����У��; @ADD:3/26 ��decomp=Trueʱ�����ܳ����쳣
        self.size = len(temp)
        for w in temp:
            if w not in self.freq.keys():           # ��ͳ��һ��
                key = w                
                if decomp:
                    try:                        key = w.split(sep)[pos]
                    except Exception,err_info:  print 'Key decomposition Error',err_info,w,key
                self.freq[key]=temp.count(w)                       # ʹ��list��count()
                cnt += int(self.freq[key])
        print "coun::CHECK: \nlist_size:%d =? count()_size:%d" % (len(temp),cnt)
        return 
    def context(self, decomp=True):
        ''' ͳ��Ŀ��ʵ����´�����|����POS,��Ŀ��� '''
        if len(self.PMIwords)==0 : return None
        pmiw = set(self.PMIwords)  #   ([ w for w in self.PMIwords if w in self.freq.keys() ])
        for w in pmiw:             # ��ʼ��
            self.content[w]=[]
        sentences = simplify(self.list,True,1)          # ���ĵ�����ά�����Ӽ�
        if decomp:                 # �ļ�����POS����Ҫ��ϴ
            for i in range(len(sentences)):             # ��ϴ��POS���֣�����������
                l = sentences[i]
                if len(l)>0:
                    sentences[i] = [ w.split('/')[0] for w in l if w.find('/')!=-1 ]
        #return sentences                            
        for line in sentences:
            for w in set(line).intersection(pmiw):      # ����
                wid = line.index(w)
                beg = wid-self.window
                if beg<0 : beg = 0
                end = wid+self.window+1                 # +1���������ʱ���
                if end>len(line) : end = len(line)
                self.content[w].extend(line[beg:end])   # ����������;ͳһ��������һ��list��
        return None
    def vector(self):
        ''' �������ļ���PMI,�γ���������;����C��W֮������ '''
        if len(self.content)==0:
            self.context()
        for w in self.content.keys():
            v = self.content[w] ;
            fw = self.freq[w]
            factor = 0
            temp = {}
            for cw in set(v):                              # ȡ�����ĵĴʣ�ȥ�أ��ڴʴ���Χ��freq
                #print "vector::PMI factor: content=%s; PMI_word=%s; \ntf(c,w)=%d, tot=%d, fc=%d, fw=%d" \
                #    % (cw,w,v.count(cw),self.size,self.freq[cw],fw)
                temp[cw]=float(v.count(cw))/(self.freq[cw]*fw) # PMI( C, Wi ) = Tf(C,Wi)/{ freq(C)*freq(Wi) }
                factor += temp[cw]**2
            factor -= temp[w]**2                               # ����context()�Ľ����Ŀ��ʵ�Ӱ��
            self.content[w] = temp                             # ����Ŀ���w���������γ���������Ŀ��ʵ� df=N/f_w
            self.PMIfactors[w] = factor                        # ��ĸ
    def similary(self,link=' '):
        ''' ����Ŀ���֮����������ƶ�; �ʼ����ַ���link���� '''
        if len(self.PMIfactors)==0:
            self.vector()
        totk = self.content.keys()
        for i in range(len(totk)):
            ki = totk[i]
            for j in range(i+1, len(totk)):               # ����simi[va,vb]=simi[vb,va] �򻯼���
                kj = totk[j]
                vi = self.content[ki]
                vj = self.content[kj]                          # self.simi
                vset = set(vj.keys()).intersection(set(vi.keys()))
                if len(vset)==0:                        # �������޽���
                    self.simi[link.join(vi,vj)]=0
                    continue 
                simi = 1                    
                for kv in vset:
                    simi = simi*(vi[kv]*vj[kv])         # �������ƶ�
                self.simi[link.join([ki,kj])]=float(simi)/(self.PMIfactors[ki]*self.PMIfactors[kj])
        return
    def save_vector(self,path,data,ope_type = 'write'):
        ''' ����м��� '''
        if not os.path.isfile(path) or not isinstance(data,dict): return None
        if ope_type == 'read':
            #TODO
            return True
        try:        # Ĭ��д
            sh = shelve.open(path)
            for k in data.keys():
                sh[k] = data[k]
            sh.close()
        except Exception,data:
            print " ����м������� ", data
            return False
    def monitor_parameter(self,data={}):
        ''' ��ز��������� '''
        pass

if __name__=='__main__':
    p = r'./test/R000011.txt'
    pmis = [ '��Ļ', '���' ]
    tt = Similary_Pku(p,pmis)
    tt.count()
    tt.context()
    tt.similary()  
                

                





