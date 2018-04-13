import sys

binNum = 'NA'

input = int(sys.argv[1])

for i in range(0,4400,20):
    thislow = i
    thishigh = i+20

    if input < thishigh and input >= thislow:
        binNum = thislow


if binNum!='NA':
    low = binNum
    high = binNum+20
    print "%d_%d" % (low,high)
else:
    print binNum
