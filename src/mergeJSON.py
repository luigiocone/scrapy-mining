#! /usr/bin/python3

import sys
import re
list=[]
for line in sys.stdin:
    list.append(line.rstrip('\n'))

print("[")
flength=len(list)
for x in range(0, flength):
    line=list[x]
    if x<flength-1 and re.match("^\}\s*$",line): 
        line+=","
    print(line)
print("]")
