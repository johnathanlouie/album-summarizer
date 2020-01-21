from numpy import argmax, zeros

from cc import CcDataFile
from jl import NPY_CLASSES, NPY_PRED, TEXT_PRED, ListFile, npload


def onenumber(onehot):
    p1 = argmax(onehot, 1)
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
    pred = npload(NPY_PRED)
    truth = npload(NPY_CLASSES)
    pred = onenumber(pred)
    truth = onenumber(truth)
    ListFile(TEXT_PRED).write(oneup(pred))
    cm = zeros((7, 7))
    for t, p in zip(truth, pred):
        p1 = p+1
        t1 = t+1
        cm[t1][0] = cm[t1][0] + 1
        cm[t1][p1] = cm[t1][p1] + 1
    label = "%11s %4s %3s%% | %4s %4s %4s %4s %4s %4s" % (
        '', '', '', 'env', 'peop', 'obj', 'hybr', 'anim', 'food')
    print(label)
    ccdf = CcDataFile()
    for i in range(1, 7):
        asd = "%11s %4d %3d%% | %4d %4d %4d %4d %4d %4d" % (
            ccdf._to_category_str(i - 1), cm[i][0], cm[i][i]/cm[i][0]*100, cm[i][1], cm[i][2], cm[i][3], cm[i][4], cm[i][5], cm[i][6])
        print(asd)
    return


# main()
