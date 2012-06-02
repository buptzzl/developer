# coding=utf8
import os,re

def log_info(fp,func,errinfo,paras=None,model=None,time=None):
    if not isinstance(fp,file):
        print "!!!! ERROR::log_info file-handle isn't given !!!!"
        return None
    cont = '\t'.join([str(time),str(func),str(errinfo),str(paras),str(model),'\n'])
    fp.write(cont)
    fp.flush()

#转码，将code1码转为code2码，code1默认为UTF－8，code2默认为GB2312
def transcoding(content,code1="UTF-8",code2="GB2312"):
    #按换行符将输入内容切成列表
    List = content.splitlines()
    string = ""
    if len(List) != 0:
        for j in range(len(List)):
            try:
                #将code1码解码为unicode码
                scUnionCode = List[j].decode(code1)
                #将unicode码编码为code2码
                scNewCode = scUnionCode.encode(code2)
                List[j] = scNewCode
            except:
                continue
            #编码结束后将列表重新组合成字符串，并加上原有的换行符
            string = string + List[j] + "\n"
        content = string
    return content[:-1]

class Dir_File:
    def __init__(self,Pdir,new=False):
        if isinstance(Pdir,str):    self.dir = Pdir
        else:   self.dir = ""
        self.sep_col = None             # None默认支持空格|Tab两种分割
        self.sep_row = '\n'
        assert self.check_dir(),"check_dir() ERROR "
    def check_dir(self,pdir=None):
        ''' 检查(文件所在的)目录的存在,不存在时尝试生成 '''
        if not pdir: pdir=self.dir
        if os.path.isfile(pdir):
            self.dir = os.path.split(pdir)[0]
        elif not os.path.exists(pdir):
            try:
                os.makedirs(pdir)
                self.dir = pdir
            except Exception,data:
                print '!!!!!! Make dir:[%s] Error !!!!!! '%pdir
                return False
        return True
    def oper_file(self,fpath,model='rb',data=[],sep_col=None):
        ''' 操作单个文件 返回list; 写模式最多支持两级list '''
        try:
            fp = file(fpath,model)
            result = []
            if 'r' in model:
                result = [ l.strip().split(sep_col) for l in fp ]
            else:
                if not sep_col: sep_col = '\t'          # 列的默认分割符
                if len(data)!=0 and isinstance(data[0],list):
                    data = [ sep_col.join(l) for l in data ]
                fp.write( '\n'.join(data) )
        except Exception,ed:
            print "!!!! oper_file::ERROR file: %s,model: %s!!!!"%(fpath,model),ed
        finally:
            fp.close()
        return result
    def oper_dir(self,oper,params=None):
        ''' 对目录中文件进行指定操作oper 至少有两个参数 '''
        fpath = self.dir
        if not os.path.exists(fpath) or not os.path.isdir(fpath) or not isinstance(oper,str):
            return []
        for f in os.listdir(fpath):
            fp = os.path.join(fpath,f)
            eval(oper)(fp,params)           # 至少还有一个参数params
    def save_dict(self, data, fpath, sep_col='\t'):
        ''' @ADD:3/26 保存dict数据到文件, 一个key对应一行，d[key]最多为一级list '''
        if os.path.isdir(fpath) or not isinstance(data,dict) or len(data)==0:
            print "****** save Data to %s ERROR! *******" % fpath
        try:
            fp = file(fpath,'wb')           # 仅支持写操作
            for k in data.keys():
                v = data[k]
                if isinstance(v,list):
                    v = [ str(i) for i in v]# 必须为str    
                    v = sep_col.join(v)
                v = sep_col.join([str(k),v])
                fp.write("%s\n"%v)
            fp.close()
        except Exception,data:
            print "!!!!!! Save DICT data ERROR !!!!!!\nPATH: %s" % fpath, data
        finally:
            fp.close()
    def save_mul_dict(self,data,Ndir=None):
        ''' @ADD:3/26 存放两级dict到多个文件中,基于save_dict() '''
        if not isinstance(data,dict) or len(data)==0:
            return False
        if Ndir and isinstance(Ndir,str): p_dir = Ndir
        else:    p_dir = self.dir
        #files = self.key_value({},'rb',Ndir,None,dir_only=True)
        for k in data.keys():
            v = data[k] ; #print v
            if not isinstance(v,dict): continue
            self.save_dict(v,os.path.join(p_dir,str(k)))
        return True
    def key_value(self,data={},model='wb',Ndir=None,sep_col=None,dir_only=False):
        ''' 操作文件夹与{str_docid:[str_line1,str_line2..]}格式的数据：r|w|a[b+] '''
        if not isinstance(data,dict) or ('r' not in model and (len(data)==0 or not isinstance(data.keys()[0],str))):
            print '#'*8,' Operator:key-value save Paramater Error! ','#'*8
        if Ndir:
            self.dir=Ndir
            self.check_dir()
        if sep_col: self.sep_col = sep_col
        res = {}
        Fsets = os.listdir(self.dir)
        if dir_only:                                # 仅需要文件列表 @ADD:3/26
            files = [ os.path.join(self.dir, f) for f in Fsets]
            return files
        if 'r' in model:
            for l in Fsets:
                fp_p = os.path.join(self.dir,l)
                if os.path.isdir(fp_p): continue    # 跳过文件夹
                fp = file(fp_p,model)
                res[l]=[ i.strip().split(self.sep_col) for i in fp ]
                fp.close()
        else:
            if not sep_col: sep_col = '\t'          # 写时特殊处理
            for k in data.keys():
                v = data[k]
                if not isinstance(v,list) or len(v)==0:
                    continue
                if isinstance(v[0],list):            # 处理两级list
                    for i in range(len(v)-1,-1,-1):    
                        if isinstance(v[i],list):
                            v[i] = sep_col.join(v[i])
                        elif not isinstance(v[i],str):
                            del v[i]
                pf = os.path.join(self.dir,str(k))        # 基于key的文档存放路径
                Tmod = model
                #if not os.path.exists(pf) and 'a' in Tmod:  Tmod='wb'
                try:    
                    fp = file(pf, Tmod)
                    fp.write('\n'.join(v))
                    fp.close()
                except Exception,info_errors:              # @ADD:3/26      
                    print "!!!!!! save data to:%s ERROR !!!!!! " % fp,info_errors
                finally: fp.close()
        return res    
    def param_monitor(self,news=None):
        ''' 目录操作类的参数检控 '''
        pass    
                    
if __name__=='__main__':
    '''ope = 'split_sentence'
    r = [r'../COAE2011_Corpus_All_Text/ict_fin/',
         r'../COAE2011_Corpus_All_Text/ict_ent/',
         r'../COAE2011_Corpus_All_Text/ict_fin/']
    for i in range(3):
        d = r[i] 
        dt = Dir_File(d) 
        res = dt.key_value(model='rb')
        for i in res.keys():
            temp = [ l for l in res[i] if len(l)>3 ]
            res[i] = temp
        #tt = dt.key_value(res,'wb')
        #dt.oper_dir(ope)        # 分句子
    #dr = dt.key_value({'aa':['111','222']},'rb')
    #d = {'aa':{1:'111',2:'222'}}
    #tt = dt.save_mul_dict(d,r'./test/') '''
    
    
    
    
