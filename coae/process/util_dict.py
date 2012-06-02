# coding=utf8
'''操作字典数据类型'''

def update_value(dst,src,check=False,insF=False):
    ''' 按dst的键（可比src中多），用src的值更新dst的值;check-是否需类型匹配 insF-是否插入 '''
    sks = set(src.keys())
    dks = set(dst.keys())
    for k in dks:
        # 支持check功能
        if k in sks and (not check or type(dst[k])==type(src[k])): 
            dst[k] = src[k]
    if insF :
        newk = sks.difference(dks)
        for k in newk: dst[k] = src[k]
    return dst

if __name__=='__main__':
    d = {1:3, 2:[2,3], "a":"b"}
    s = {1:[],2:[],"a":2,3:3}
    update_value(d,s,True,True)
