# coding=utf-8
import re

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

def simplify(data, del_atom=False, level=-1):
    ''' 将多级list降维到一级list，默认不保存高级list中的atom; level控制迭代次数(-1为无限次) '''
    if not isinstance(data,list) or len(data)==0: return None
    #temp = data
    res = []
    sz = len(data)
    pos = [i for i in range(sz) if isinstance(data[i],list)]
    if len(pos)!=0 and level:                  # 仅处理2级以上list 且level非0
        for i in range(len(data)-1,-1,-1):
            tcol = data[i]
            if i in pos and len(tcol)!=0:
                res.extend(simplify(tcol,del_atom,level-1)) # 递归
            elif not del_atom:       # 保留高级list中的atom
                res.append(tcol)
    else:
        res = data
    return res

def drop_empty(data,level=-1):
    ''' 删除list 中上方level层的空白list '''
    pass
    tmp = []
    while level!=0 : # and isinstance(data,list):
        for l in data :
            tmp.append(drop_empty(l,level-1))
    return tmp

class LineOperator:
    def __init__(self, data=None, dataS=""):
        if isinstance(data,list):   # 将一级list去尾部空白字符，转换为二级list[[line0],..]
            #data = [ strQ2B(l) for l in data ]     # 将各行字符做 Q2B 转换
            self.data_list = [ l.split() for l in data ]
        else:    self.data_list = [[]]# 两级list,分别对应 行、列
        self.data_str = dataS # 字符串格式
        self.sep_col = ' '    # 列的分割符
        self.sep_line = '\n'
        self.filter_col = []  # 列清洗后的结果
        self.dict_col = {}    # 按字典格式保存的列结果
    def list2str(self,sepCol=None,sepLine=None,data=None):
        """ 将两级list格式的字符串序列转换为str eg:[['a','b'],['c']]->'ab\nc' """
        if data: self.data_list=data
        if not sepCol or not isinstance(sepCol,str): sepCol=self.sep_col
        if not sepLine or not isinstance(sepLine,str): sepLine= self.sep_line
        tmp = []
        for l in self.data_list:
            tmp.append(sepCol.join(l))
        self.data_str = sepLine.join(tmp)
        return self.data_str
    def str2list(self,sepCol=None,sepLine=None,data=None):
        ''' 将str转换为两级list '''
        if data: self.data_str=data
        if not sepCol or not isinstance(sepCol,str):
            sepCol=self.sep_col  
            tmp = self.data_str.split(sepLine)
        else:       # 参数中无sepCol则默认数据已为一级list
            tmp = self.data_str
        if not sepLine or not isinstance(sepLine,str): sepLine= self.sep_line        
        self.data_list = [ l.split(sepCol) for l in tmp ]
        return self.data_list    
    def list_col(self,tgt=[0],fEmpty=False):
        """ 对list抽取目标列 tgt """
        maxl = tgt[0]   
        for i in tgt:
            if i>maxl: maxl=i
        for l in self.data_list:
            if len(l)>maxl:     # 保证不溢出
                self.filter_col.append( [ l[i] for i in tgt] )
            elif fEmpty:        # 需要保留空行，则插入[]
                self.filter_col.append([]) 
        return self.filter_col
    def dict_col(self,key=0,tgt=[1]):
        ''' 对list 抽取key列为键, tgt列为值的dict '''
        maxl = tgt[0]   
        for i in tgt:
            if i>maxl: maxl=i
        for l in self.data_list:
            if len(l)>maxl:             # 保证不溢出
                dkey = self.dict_col.keys()
                if l[key] in dkey:      # 用 extend 合并两个list
                    self.dict_col[l[key]].extend( [l[i] for i in tgt] )
                else:
                    self.dict_col[l[key]]= [l[i] for i in tgt]
        return {} #self.dict_col
    def format_emo(self,data):
        ''' 将3级list插入[], 降为2级list'''
        if not isinstance(data[0],list) or not isinstance(data[0][0],list):
            return False
        res = []
        for l in data:
            res.extend(l)
            res.append([])              # 分割标志
        return res
    def mintor_params(self,news=None):
        res = { 'data_str': self.data_str,
                'data_list':self.data_list,
                'sep_col' : self.sep_col,
                'sep_line': self.sep_line,
                'filter_col':self.filter_col,
                'dict_col':self.dict_col
                }
        if not news: return res
        else:
            if not isinstance(news,dict):  return None  # 错误时返回的标志
            kr = res.keys()
            for k in news.keys():           # 类型不同时无处理
                if k in kr and type(res[k])==type(news[k]): res[k]=news[k]
            self.data_str=res['data_str'] ; self.data_list=res['data_list']
            self.sep_col=res['sep_col'] ;   self.sep_line=res['sep_line']
            elf.filter_col=res['filter_col'];self.dict_col=res['dict_col']
            return {}  # 很2的返回结果
    #def str2Q(self):
    def func_handler(self, func=None):
        ''' 提供对列进行操作的外部函数func接口  '''
        if func and isinstance(func,function):
            return func(self.data_list)
        else:
            return None
        


if __name__=="__main__":
    tts = ['我爱 北京 天安门 \n', [1,[2,[]]],'我家 在湖南 \n']
    res = simplify(tts,False,-1)
    '''tt = LineOperator(tts)
    ts = tt.list2str()
    tl = tt.str2list()
    tlc = tt.list_col([0,1])
    tlc2 = tt.list_col([0,2])
    #td = tt.dict_col()       # ？？？ TypeError: 'dict' object is not callable
    tm = tt.mintor_params()
    '''
