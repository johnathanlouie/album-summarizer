import cv2
import numpy as np
import os


def ordertest():
    a = cv2.imread('C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\calvin\\Calvin Lee-[01_15] Guilin pt1_files\\14346_10204632819193796_7631239845068726471_n.jpg')
    print(a.shape)
    h = 640
    w = 960
    b = cv2.resize(a, (w, h))
    print(b.shape)
    cv2.imwrite('C:\\Users\\Johnathan Louie\\Downloads\\qqq.jpg', b)


def photo():
    photos = np.load('photos.npy')
    b = photos[0]
    cv2.imwrite('C:\\Users\\Johnathan Louie\\Downloads\\qqq.jpg', b)


def mkdirs():
    name = 'C:\\Users\\Johnathan Louie\\Downloads\\summarizer\\output\\calvin\\Calvin Lee-December 2014 pt1_files\\10007255_10204519525721530_1524391031638505687_n.jpg'
    b = name.rfind('\\')
    print(b)
    c = len(name)
    print(c)
    a = name[0:b]
    print(a)
    exit()
    os.makedirs(name, exist_ok=True)


def emptylist():
    a = [-1, 2]
    print(type(a))
    print(a*50)
    return


def osjoin():
    a = os.path.join('c:/', 'sadf', 'asdf/asfn')
    a = os.path.normpath(a)
    print(a)
    return


def numpyaddition():
    a = np.ones((2, 3))
    b = a + 50
    print(b)
    return


def osabspath():
    b = r'C:\albumsummarizer\calvin\Calvin Lee-December 2014 pt1_files\10437688_10204519506761056_1744003276057380254_n.jpg'
    a = os.path.abspath(b)
    c = os.path.abspath(a)
    print(c)
    return


def osnormpath():
    print(os.path.normpath('/ddgdg/sdfgsdh'))
    return


def array1():
    a = list(150)
    a[123] = 0
    print(a)
    return


def lenarray():
    a = np.zeros((5, 5, 5))
    print(a.shape)
    print(len(a))
    return


def chaincompare():
    a = 0
    b = a is 3 or 0
    print(b)
    return


def typecheck():
    x = 0.1 != None
    print(x)
    return


def openfile():
    with open('hrsdg.hihh') as i:
        print(i)
    return


openfile()
