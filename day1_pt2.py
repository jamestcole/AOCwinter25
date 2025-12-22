filename='day1input.txt'
with open(filename) as file:
    lines = [line.rstrip() for line in file]

p = 50
pinit = 50
pmax = 100
lngth = 0
numofzero = 0
triggered = 0
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
            print(f'p // pmax is : {p//pmax}')
            numofzero += ((p//pmax))
            p = p%pmax
            print(f'triggered pmax p is now {p}')
        print(f' R number is {pos}')
        print(f' position of p is now {p}')
    elif n[0] == 'L':

        steps = int(n[1:])   # everything after the first char is the number
        start = p  # position before this rotation

        # Count how many times we land on 0 during this left rotation
        if start > 0:
            if steps >= start:
                # First time we hit 0 is after 'start' steps,
                # then every full turn (every pmax steps) after that.
                numofzero += 1 + (steps - start) // pmax
        else:  # start == 0
            # Starting at 0: we only land on 0 every full turn.
            numofzero += steps // pmax

        # Update final position of the dial
        p = (p - steps) % pmax

        print(f' L number is {steps}')
        print(f' position of p is now {p}')


print(f'final position of p : {p}, final pzero : {numofzero}')