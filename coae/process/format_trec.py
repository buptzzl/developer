# coding: utf-8
import os

# @brief  对文档原子插入 indri 建索引的标签 返回一个字符串 
def trec_fmt( dct_doc=[],zone='finance' ):
    if not dct_doc:        
        return
    result=['<DOC>\n', '']
    no=False
    #if isinstance(zone,str):
    #    result.append( '<TITLE>%s</TITLE>\n' % zone )
    for itm in dct_doc[:-1]:
        k=itm[0] ;   v=itm[1]        
        result.append( "<%s>%s</%s>\n" % (k,v,k) )
        #if 'docno' in k.lower():
        #    no=True
    result.append( "<%s>\n%s\n</%s>\n" % (dct_doc[-1][0],dct_doc[-1][1],dct_doc[-1][0]) )
    #if no:  # 插入对 docno 的检索
    #    result.append('<metadata> <forward>DOCNO</forward> \n<backward>DOCNO</backward> </metadata> \n')
    result.append( '</DOC>\n' )
    return ''.join(result)

# @brief  对文件夹中所有文档添加 indri 标签并写入一个文档中
def txt2trec( path,fp_sav,zone='finance' ):
    files=os.listdir( path )
    #if not os.path.exists( pth_sav ):
    #    os.makedirs( path_sav )
    result=[]
    for f in files:
        no=os.path.splitext( f )[0]
        fp=open( os.path.join(path,f),'rb' )
        cnt=''.join( fp.readlines() )
        #cnt.decode( 'gbk' ).encode( 'utf-8' )  # 进行 gbk 到 utf8 转码
        #except Exception :
        #    print cnt,'\n',f ; exit(1)
        fp.close()
        dct_doc=[ ['DOCNO',no],['TITLE',zone], ['TEXT',cnt] ]
        fmt=trec_fmt( dct_doc,zone )
        result.append( fmt )
        #fp=open( os.path.join(pth_sav,f),'wb' )
        #fp.write( fmt )
        #fp.close()
    fp=open(fp_sav,'wb')
    fp.write( '\n'.join(result) )
    fp.close()

if __name__=='__main__':
    #txt2trec( r'..\COAE2011_Corpus_All_Text\seg_dig',
    #          r'..\COAE2011_Corpus_All_Text\seg_dig_trec.tot','digital')
    #txt2trec( r'..\COAE2011_Corpus_All_Text\seg_fin',
    #          r'..\COAE2011_Corpus_All_Text\seg_fin_trec.tot','finance')
    txt2trec( r'..\COAE2011_Corpus_All_Text\seg_ent',
              r'..\COAE2011_Corpus_All_Text\seg_ent_trec.tot','entertainment')
    '''txt2trec( r'..\COAE2011_Corpus_All_Text\seg_fin',
              r'..\COAE2011_Corpus_All_Text\seg_fin_trec.tot')
 
    txt2trec( r'..\COAE2011_Corpus_All_Text\seg_ent',
              r'..\COAE2011_Corpus_All_Text\seg_ent_trec.tot')
    '''         
    
        
