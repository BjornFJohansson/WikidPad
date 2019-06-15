#!/usr/bin/env python
# -*- coding: utf-8 -*-

def expandtolist(content):
    __version__="001"
    import re,string,sys,itertools,math,pprint
    resultlist=[]
    for line in re.finditer("(?P<item>[^\(\)]*?)(?P<brack>\[.*?\])", content):
        text2rep = line.group("item")
        bracket =  line.group("brack")
        padding = max([len(str(x).strip()) for x in re.split("\.\.|,", bracket.strip("[ ]"))])
        inbracket = [item.strip("[ ]") for item in bracket.split(",")]        
        expanded = []
        
        for item in inbracket:
            if re.match("(\d+\.\.\d+)|([a-z]+\.\.[a-z]+)|([A-Z]+\.\.[A-Z]+)",item):
                low, high = item.split("..",)
                if low.isdigit() and high.isdigit():
                    r = ['{:{}d}'.format(x,padding) for x in range (int(low), 1+int(high))]
                if (low.islower() and high.islower()) or (low.isupper() and high.isupper()):
                    r = [chr(a) for a in range(ord(low),1+ord(high))]
                expanded.extend(r)
            else:
                expanded.append(item.strip())

        resultlist.append([text2rep+x for x in expanded])

    ml = max([len(x) for x in resultlist])
    
    norm = []
    for r in resultlist:
        mp = int(math.ceil(float(ml)/float(len(r))))
        norm.append(list(itertools.chain.from_iterable(list(zip(*(r,)*mp)))))

    #pprint.pprint(norm)
    rt=""
    for a in range(ml):
        rt +="".join([b[a] for b in norm])+"\n"
    return rt


if __name__=="__main__":
    content = "lane [1..10, 120] clone [1..11]"
    print(content)
    print(expandtolist(content))
#    lane [1..10, 120] clone [1..11]
#    lane   1 clone  1
#    lane   2 clone  2
#    lane   3 clone  3
#    lane   4 clone  4
#    lane   5 clone  5
#    lane   6 clone  6
#    lane   7 clone  7
#    lane   8 clone  8
#    lane   9 clone  9
#    lane  10 clone 10
#    lane 120 clone 11