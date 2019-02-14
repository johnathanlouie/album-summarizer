import numpy as np
import cv2
import os
import csv
import time


TEXT_CLASSES = 'categ.txt'
TEXT_URL_RAW = 'url.txt'
TEXT_URL_PROCESSED = 'url2.txt'
TEXT_URL_ALBUM = 'url3.txt'
TEXT_PRED = 'pred.txt'

TEXT_CLUSTER_SIFT = 'cl1.txt'
TEXT_CLUSTER_HISTOGRAM = 'cl2.txt'
TEXT_CLUSTER_COMBINED = 'cl3.txt'
TEXT_CLUSTER_COMBINED2 = 'cl4.txt'

NPY_CLASSES = 'categ'
NPY_PHOTOS = 'photos'
NPY_PRED = 'pred'
NPY_DESC = 'desc'

H5_CLASSIFIER = 'classifier.h5'
H5_RATER = 'rater.h5'

JSON_SIMILARITYMATRIX = 'sim.json'


h = int(640 * 1 / 4)
w = int(960 * 1 / 4)
res = (h, w)
res2 = (h, w, 3)

classdict = {
    'environment': 1,
    'people': 2,
    'object': 3,
    'hybrid': 4,
    'animal': 5,
    'food': 6
}

classdict2 = [
    None,
    'environment',
    'people',
    'object',
    'hybrid',
    'animal',
    'food'
]

layers = ['block1_conv1', 'block1_conv2', 'block2_conv1', 'block2_conv2', 'block3_conv1', 'block3_conv2',
          'block3_conv3', 'block4_conv1', 'block4_conv2', 'block4_conv3', 'block5_conv1', 'block5_conv2', 'block5_conv3']


def res3(n):
    return (n, h, w, 3)


def npsave(name, data):
    return np.save(name, data)


def npload(name):
    return np.load("%s.npy" % name)


def readtxt(filename):
    with open(filename, 'r') as f:
        a = f.read()
        a = a.split('\n')
        a = list(filter(len, a))
    return a


def readimg(imglist):
    size = len(imglist)
    l = np.ndarray((size, h, w, 3))
    for i, v in enumerate(imglist):
        l[i] = cv2.imread(v, cv2.IMREAD_COLOR)
    return l


def readimg2(imglist):
    l = list()
    for v in imglist:
        l.append(cv2.imread(v, cv2.IMREAD_COLOR))
    return l


def hsv(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


def hsvlist(imglist):
    return list(map(hsv, imglist))


def getcol(n):
    csv = readcsv()
    csv = np.asarray(csv)
    return csv[:, n]


def winslash(s):
    return s.replace('/', '\\')


def absurl(url):
    cwd = os.getcwd()
    return "%s\\%s" % (cwd, url)


def absurl2(url):
    # cwd = os.getcwd()
    # return "%s\\%s\\%s" % (cwd, 'output', url)
    return url.replace('summarizer', 'summarizer\\output')


def readcsv():
    with open('data.csv', 'r') as f:
        reader = csv.reader(f)
        your_list = list(reader)
    return your_list


def numberize(col):
    a = list()
    for i in col:
        x = str(i).strip()
        a.append(classdict[x])
    return a


def intize(txtarray):
    return list(map(int, txtarray))


def onehot(a):
    size = (len(a), 6)
    b = np.zeros(size)
    for i, v in enumerate(a):
        b[i][v-1] = 1
    return b


def writetxt(filename, array):
    with open(filename, 'w') as f:
        for i in array:
            print(i, file=f)
    return


def appendtxt(filename, array):
    with open(filename, 'a') as f:
        for i in array:
            print(i, file=f)
    return


class Stopwatch:
    def __init__(self):
        self.start = time.time()

    def elapsed(self):
        return time.time() - self.start

    def print(self):
        minutes, sec = divmod(self.elapsed(), 60)
        print('time: %d:%02d' % (minutes, sec))
