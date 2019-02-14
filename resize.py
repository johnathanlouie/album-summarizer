import cv2
import numpy as np
import jl
import os


def originurl():
    a = list()
    for i in jl.getcol(0):
        x = i.strip()
        x = jl.winslash(i)
        x = jl.absurl(x)
        a.append(x)
    return a


def mkdirs(filename):
    b = filename.rfind('\\')
    name = filename[0:b]
    os.makedirs(name, exist_ok=True)
    return


def main():
    # urls1 = originurl()
    urls1 = jl.readtxt(jl.TEXT_URL_RAW)
    urls2 = jl.readtxt(jl.TEXT_URL_PROCESSED)
    arrdim = jl.res3(len(urls1))
    a = np.ndarray(arrdim)
    res = (jl.w, jl.h)
    for idx, (src, dst) in enumerate(zip(urls1, urls2)):
        print(src)
        print(dst)
        img = cv2.imread(src, cv2.IMREAD_COLOR)
        print(img.shape)
        img2 = cv2.resize(img, res, interpolation=cv2.INTER_CUBIC)
        print(img2.shape)
        a[idx] = img2
        mkdirs(dst)
        cv2.imwrite(dst, img2)
    jl.npsave(jl.NPY_PHOTOS, a)
    print('done')
    return


main()
