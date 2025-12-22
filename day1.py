filename='day1input.txt'
with open(filename) as file:
    lines = [line.rstrip() for line in file]

p = 50
pinit = 50
pmax = 100
lngth = 0
numofzero = 0
for n in lines:
    lngth = len(n)
    pos = 1
    num = ''
    print(f'len of n : {lngth}')
    if n[0] == 'R':
        while pos != lngth :
            num += n[pos]
            pos += 1
        if int(p) == 100 or int(p) == 0:
            numofzero += 1
        p += int(num)
        if p > pmax:
            print(f'triggered pmax p is currently {p}')
            p = p%pmax
            print(f'triggered pmax p is now {p}')
        print(f' R number is {pos}')
        print(f' position of p is now {p}')
    elif n[0] == 'L':
        while pos != lngth :
            num += n[pos]
            pos += 1
        if int(p) == 100 or int(p) == 0:
            numofzero += 1
        p -= int(num)
        if p < 0:
            print(f'triggerd pmin , p is currently {p}')
            print(p%pmax)
            p = p%pmax
            print(f'triggered pmin p is now {p}')
        print(f' R number is {pos}')
        print(f' position of p is now {p}')

print(f'final position of p : {p}, final pzero : {numofzero}')