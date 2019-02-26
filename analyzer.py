import jl
import numpy as np


def onenumber(onehot):
    p1 = np.argmax(onehot, 1)
    return p1


def oneup(a):
    b = list()
    for i in a:
        b.append(i+1)
    return b


def main():
    # col = jl.getcol(2)
    # truth = jl.numberize(col)
    # pred = jl.readtxt('cpred.txt')
    pred = jl.npload(jl.NPY_PRED)
    truth = jl.npload(jl.NPY_CLASSES)
    pred = onenumber(pred)
    truth = onenumber(truth)
    jl.writetxt(jl.TEXT_PRED, oneup(pred))
    cm = np.zeros((7, 7))
    for t, p in zip(truth, pred):
        p1 = p+1
        t1 = t+1
        cm[t1][0] = cm[t1][0] + 1
        cm[t1][p1] = cm[t1][p1] + 1
    label = "%11s %4s %3s%% | %4s %4s %4s %4s %4s %4s" % (
        '', '', '', 'env', 'peop', 'obj', 'hybr', 'anim', 'food')
    print(label)
    for i in range(1, 7):
        asd = "%11s %4d %3d%% | %4d %4d %4d %4d %4d %4d" % (
            jl.classdict2[i], cm[i][0], cm[i][i]/cm[i][0]*100, cm[i][1], cm[i][2], cm[i][3], cm[i][4], cm[i][5], cm[i][6])
        print(asd)
    return


# main()
