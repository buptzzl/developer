# coding=utf-8

import os

path_d = r'../COAE2011_Corpus_All_Text/seg4_dig'
path_e = r'../COAE2011_Corpus_All_Text/seg4_ent'
path_f = r'../COAE2011_Corpus_All_Text/seg4_fin'
str_sep_sent = '\r\n'
str_sep_doc = '\r\n'

# @brief 对进行分词（gbk转码正常）的文件合并
def get_sentence(path):
    try:
        fp = open(path,'rb')
        res = []
        for l in fp:
            l = l.strip().split()
            if len(l):
                res.append(l[0])
            else:
                res.append( str_sep_sent )
        fp.close()
    except :
        return None
    return ''.join(res)

# @brief 对一个类别的所有文档分句，句子写文件，返回文件错误列表
def topic_process(path, save=None):
    file_set = os.listdir( path )
    count_err = []
    if save :
        # print save
        sfp = open(save,'wb')
    else :
        sfp = open(''.join([path,'_sent_sep']),'wb')    # 默认的结果路径
    for f in file_set:
        path_f = os.path.join(path,f)
        res_f = get_sentence(path_f) ; # print '-'*20,'\r\n',res_f ; exit ;
        if res_f:
            sfp.write( res_f )
            sfp.write(str_sep_doc)
            sfp.flush()
        else :
            count_err.append(path_f)
    sfp.close()
    return count_err

if __name__=='__main__':
    # err_file = []
    #err_d = topic_process(path_d)
    #err_e = topic_process(path_e)
    err_f = topic_process(path_f)
    print err_f,#err_d,'\r\n',err_e,'\r\n',

    
        
            
        
