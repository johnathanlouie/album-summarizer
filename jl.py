import numpy as np
import cv2
import os
import csv
import time


TEXT_CLASSES = 'gen\\categ.txt'
TEXT_URL_RAW = 'gen\\url.txt'
TEXT_URL_PROCESSED = 'gen\\url2.txt'
TEXT_URL_ALBUM = 'gen\\url3.txt'
TEXT_PRED = 'gen\\pred.txt'
TEXT_RATE = 'gen\\rate.txt'

TEXT_CLUSTER_SIFT = 'gen\\cl1.txt'
TEXT_CLUSTER_HISTOGRAM = 'gen\\cl2.txt'
TEXT_CLUSTER_COMBINED = 'gen\\cl3.txt'
TEXT_CLUSTER_COMBINED2 = 'gen\\cl4.txt'

NPY_CLASSES = 'categ'
NPY_PHOTOS = 'photos'
NPY_PHOTOS2 = 'photos2'
NPY_PRED = 'pred'
NPY_PREDRATE = 'predrate'
NPY_DESC = 'desc'
NPY_RATE = 'rate'

H5_CLASSIFIER = 'gen\\classifier.h5'
H5_RATER = 'gen\\rater.h5'

JSON_SIMILARITYMATRIX = 'gen\\sim.json'


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
    """Returns dimensions of an array of images."""
    return (n, h, w, 3)


def npsave(name, data):
    return np.save("gen\\%s" % name, data)


def npload(name):
    return np.load("gen\\%s.npy" % name)


def readtxt(filename):
    """
    Load a newline separated value file.
    """
    with open(filename, 'r') as f:
        a = f.read()
        a = a.split('\n')
        a = list(filter(len, a))
    return a


def readimg(imglist):
    """
    Load an array of images.

    :param list<str> imglist: List of URLs of images.
    :returns ndarray: Array of images.
    """
    size = len(imglist)
    l = np.ndarray(res3(size))
    for i, v in enumerate(imglist):
        l[i] = cv2.imread(v, cv2.IMREAD_COLOR)
    return l


def readimg2(imglist):
    """
    Load a list of images.

    :param list<str> imglist: List of URLs of images.
    :returns list<ndarray>: List of images.
    """
    l = list()
    for v in imglist:
        l.append(cv2.imread(v, cv2.IMREAD_COLOR))
    return l


def hsv(img):
    """
    Convert an image from BGR to HSV.

    :param ndarray img: BGR image
    :returns ndarray: HSV image
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


def hsvlist(imglist):
    """
    Convert a list of images from BGR to HSV.

    :param list<ndarray> imglist: list of BGR images
    :returns list<ndarray>: list of HSV images
    """
    return list(map(hsv, imglist))


def getcol(n):
    """
    Get column from data file.

    :param int n: Index (zero based) of column to extract.
    :returns ndarray: column of data
    """
    csv = readcsv()
    csv = np.asarray(csv)
    return csv[:, n]


def winslash(s):
    """
    Convert all forward slashes to backward slashes.
    """
    return s.replace('/', '\\')


def absurl(url):
    """
    Get absolute URL from relative URL.
    """
    cwd = os.getcwd()
    return "%s\\%s" % (cwd, url)


def absurl2(url):
    """
    Add output to URL.
    """
    # cwd = os.getcwd()
    # return "%s\\%s\\%s" % (cwd, 'output', url)
    return url.replace('summarizer', 'summarizer\\output')


def readcsv():
    """
    Read data file.
    """
    with open('data.csv', 'r') as f:
        reader = csv.reader(f)
        your_list = list(reader)
    return your_list


def numberize(col):
    """
    Convert class string to integer representation.
    """
    a = list()
    for i in col:
        x = str(i).strip()
        a.append(classdict[x])
    return a


def intize(txtarray):
    """
    Convert a list of string numbers to integers.
    """
    return list(map(int, txtarray))


def onehot(a):
    """
    Convert integer representation to one hot representation.
    """
    size = (len(a), 6)
    b = np.zeros(size)
    for i, v in enumerate(a):
        b[i][v-1] = 1
    return b


def writetxt(filename, array):
    """
    Save in newline separated value format.
    """
    with open(filename, 'w') as f:
        for i in array:
            print(i, file=f)
    return


def appendtxt(filename, array):
    """
    Append to newline separated value format.
    """
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
