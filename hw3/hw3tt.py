import numpy as np

s = 0
n = 0
o = 0
c_tloc = []


def turn(s1, a, s2):
    x, y = s1
    xx, yy = s2
    if s1 == s2 == [0, 0]:
        if a in [0, 3]:
            return 0.8
        else:
            return 0.2
    if s1 == s2 == [s - 1, 0]:
        if a in [0, 2]:
            return 0.8
        else:
            return 0.2
    if s1 == s2 == [0, s - 1]:
        if a in [1, 3]:
            return 0.8
        else:
            return 0.2
    if s1 == s2 == [s - 1, s - 1]:
        if a in [1, 2]:
            return 0.8
        else:
            return 0.2
    if y in range(1, s - 1):
        if x == 0 and a == 3:
            if s1 == s2:
                return 0.7
            else:
                return 0.1
        if x == (s - 1) and a == 2:
            if s1 == s2:
                return 0.7
            else:
                return 0.1
    if x in range(1, s - 1):
        if y == 0 and a == 0:
            if s1 == s2:
                return 0.7
            else:
                return 0.1
        if y == (s - 1) and a == 1:
            if s1 == s2:
                return 0.7
            else:
                return 0.1

    if (a == 0 and (x == xx and y - 1 == yy)) \
            or (a == 1 and (x == xx and y + 1 == yy)) \
            or (a == 2 and (x + 1 == xx and y == yy)) \
            or (a == 3 and (x - 1 == xx and y == yy)):
        return 0.7

    return 0.1


def create_states(s1, term):
    x, y = s1
    if s1 == term:
        return []
    if s1 == [0, 0]:
        return [[0, 0], [0, 1], [1, 0]]
    if s1 == [s - 1, 0]:
        return [[s - 1, 0], [s - 2, 0], [s - 1, 1]]
    if s1 == [0, s - 1]:
        return [[0, s - 1], [0, s - 2], [1, s - 1]]
    if s1 == [s - 1, s - 1]:
        return [[s - 1, s - 1], [s - 2, s - 1], [s - 1, s - 2]]
    if y in range(1, s - 1):
        if x == 0:
            return [[x, y], [x, y - 1], [x, y + 1], [x + 1, y]]
        if x == s - 1:
            return [[x, y], [x, y - 1], [x, y + 1], [x - 1, y]]

    if x in range(1, s - 1):
        if y == 0:
            return [[x, y], [x - 1, y], [x + 1, y], [x, y + 1]]
        if y == s - 1:
            return [[x, y], [x - 1, y], [x + 1, y], [x, y - 1]]

    return [[x - 1, y], [x, y + 1], [x + 1, y], [x, y - 1]]


def main():
    global s, n, o, c_tloc
    f = open('input.txt', 'r')
    s = int(f.readline())
    n = int(f.readline())
    o = int(f.readline())

    o_loc = []
    for _ in range(o):
        a, b = ([int(x) for x in f.readline().split(',')])
        o_loc.append([a, b])

    c_sloc = []
    for _ in range(n):
        a, b = ([int(x) for x in f.readline().split(',')])
        c_sloc.append([a, b])

    c_tloc = []
    for _ in range(n):
        a, b = ([int(x) for x in f.readline().split(',')])
        c_tloc.append([a, b])

    f.close()
    policy = {}
    for term in c_tloc:
        try:
            test = policy[str(term)]
            continue
        except:
            pass
        r = [[-1 for _ in xrange(s)] for _ in xrange(s)]
        for i in range(s):
            for j in range(s):
                if [i, j] in o_loc:
                    r[i][j] = -101
                if [i, j] == term:
                    r[i][j] = 99

        v = [[0 for _ in xrange(s)] for _ in xrange(s)]
        p = [[0 for _ in xrange(s)] for _ in xrange(s)]
        change = True

        iteration = 0
        while change:
            iteration += 1
            if iteration % 10 == 0:
                change = False
            vk = [row[:] for row in v]
            for i in range(s):
                for j in range(s):
                    states = create_states([i, j], term)
                    vk[i][j] = r[i][j] + (0.9 * sum([turn([i, j], p[i][j], x) * v[x[0]][x[1]] for x in states]))
            v = [row[:] for row in vk]

            for i in range(s):
                for j in range(s):
                    states = create_states([i, j], term)
                    maxi = -1000000
                    arg_max = p[i][j]
                    for k in [0, 1, 2, 3]:
                        arg_max_sum = sum([turn([i, j], k, x) * v[x[0]][x[1]] for x in states])
                        if maxi < arg_max_sum:
                            maxi = arg_max_sum
                            arg_max = k
                    if arg_max != p[i][j]:
                        change = True
                        p[i][j] = arg_max
        policy[str(term)] = p[:]
    r = [[-1 for _ in xrange(s)] for _ in xrange(s)]

    for i in range(s):
        for j in range(s):
            if [i, j] in o_loc:
                r[i][j] = -101

    move_left = [3, 2, 0, 1]
    move_opp = [1, 0, 3, 2]
    move_right = [2, 3, 1, 0]

    result = ""

    for i in range(n):
        avg_sum = 0
        for j in range(10):
            start = c_sloc[i][:]
            pos = start[:]
            np.random.seed(j)
            swerve = np.random.random_sample(1000000)
            k = 0
            this_policy = policy[str(c_tloc[i])]
            r_sum = 0

            while True:
                if pos == c_tloc[i]:
                    r_sum = 1
                    break
                x, y = pos
                move = this_policy[x][y]
                if swerve[k] > 0.7:
                    if swerve[k] > 0.8:
                        if swerve[k] > 0.9:
                            move = move_opp[move]
                        else:
                            move = move_right[move]
                    else:
                        move = move_left[move]
                k += 1
                if move == 0:
                    x1 = x
                    y1 = y - 1
                if move == 1:
                    x1 = x
                    y1 = y + 1
                if move == 2:
                    x1 = x + 1
                    y1 = y
                if move == 3:
                    x1 = x - 1
                    y1 = y
                if x1 < 0 or x1 >= s or y1 < 0 or y1 >= s:
                    pass
                else:
                    x = x1
                    y = y1
                    pos = [x, y]
                if pos != c_tloc[i]:
                    r_sum += r[x][y]
                else:
                    break

            avg_sum += r_sum + 99
        result += str(avg_sum / 10) + "\n"

    f = open("output.txt", 'w')
    f.write(result)
    f.close()


if __name__ == "__main__":
    main()