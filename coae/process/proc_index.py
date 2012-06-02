# coding=utf-8
import os,shutil

# @brief  get content of indri res_file, tagList express the usefull col_id, the first id is key
# return format: {'id':[[res1],..]
def get_res( path,tagList=[0,2] ):
    result={}
    for i in range(1,21):       #init the contianer 
        result[str(i)]=[]
    f=open( path,'rb' )
    for l in f:
        l=l.strip().split()
        tmp=[ l[i] for i in tagList[1:] ] 
        result[l[tagList[0]]].append( tmp )
    f.close()
    return result

# @brief  get the file of [indri_res] in [pt_row], save to [pt_sv] order by indri_id
# require :  [pr_row]中必须有所有indri的检索结果文件,文件名的首字母为[pt_row]的键
def bd_file( pt_indri_res,pt_sv,fill_pt='',pt_row={'D':'','F':'','E':''} ):
    #fs_row={}                       # save the full_path of files in [pt_row]
    #for k,i in pt_row.items():
    #    fs_row[k]=[ os.path.join(i,j) for j in os.listdir(i) ]
    indri_res=get_res(pt_indri_res,[0,2])
    if not isinstance(indri_res,dict): return -1
    if not os.path.exists(pt_sv): os.mkdir(pt_sv)
    for k,fs in indri_res.items():
        pt_par=pt_sv+'\\'+k ;# print fill_pt,fs[0:5]       # build the category
        if not os.path.exists(pt_par):
            os.mkdir(pt_par)
        for f in fs:
            f=f[0]
            fl=f+fill_pt #; print fl          # build the complete file name
            fp_src=pt_row[fl[0].upper()]+'\\'+fl
            fp_dst=pt_par+'\\'+fl ; #print 'src: ',fp_src,'dst: ',fp_dst,'tot: ',pt_row ; return 0
            shutil.copyfile(fp_src,fp_dst)

if __name__=='__main__':
    bd_file(r'..\COAE2011_Corpus_All_Text\res_tk4',
            r'..\COAE2011_Corpus_All_Text\res_index','.txt',
            {'D':r'..\COAE2011_Corpus_All_Text\seg4_dig',
             'F':'..\COAE2011_Corpus_All_Text\seg4_fin',
             'E':'..\COAE2011_Corpus_All_Text\seg4_ent'})
            
        
