from typing import Any, Dict, List, Tuple
import numpy as np
import cv2 as cv
import os
import csv
import time
import sklearn.model_selection as sklms

CSV_CCDATA = 'data.csv'

TEXT_CLASSES = 'gen/categ.txt'
TEXT_URL_RAW = 'gen/url.txt'
TEXT_URL_PROCESSED = 'gen/url2.txt'
TEXT_URL_ALBUM = 'gen/url3.txt'
TEXT_PRED = 'gen/pred.txt'
TEXT_RATE = 'gen/rate.txt'

TEXT_CLUSTER_SIFT = 'gen/cl1.txt'
TEXT_CLUSTER_HISTOGRAM = 'gen/cl2.txt'
TEXT_CLUSTER_COMBINED = 'gen/cl3.txt'
TEXT_CLUSTER_COMBINED2 = 'gen/cl4.txt'

NPY_CLASSES = 'categ'
NPY_PHOTOS = 'photos'
NPY_PHOTOS2 = 'photos2'
NPY_PRED = 'pred'
NPY_PREDRATE = 'predrate'
NPY_DESC = 'desc'
NPY_RATE = 'rate'

H5_CLASSIFIER = 'gen/classifier.h5'
H5_RATER = 'gen/rater.h5'

JSON_SIMILARITYMATRIX = 'gen/sim.json'


# h = int(640 * 1 / 4)
# w = int(960 * 1 / 4)
h = 190
w = h
res_resize = (w, h)
res = (h, w)
res2 = (h, w, 3)


def res3(n):
    """Returns dimensions of an array of images."""
    return (n, h, w, 3)


classdict = {
    'environment': 0,
    'people': 1,
    'object': 2,
    'hybrid': 3,
    'animal': 4,
    'food': 5
}

classdict2 = [
    'environment',
    'people',
    'object',
    'hybrid',
    'animal',
    'food'
]

layers = [
    'block1_conv1',
    'block1_conv2',
    'block2_conv1',
    'block2_conv2',
    'block3_conv1',
    'block3_conv2',
    'block3_conv3',
    'block4_conv1',
    'block4_conv2',
    'block4_conv3',
    'block5_conv1',
    'block5_conv2',
    'block5_conv3'
]


def train_valid_test_split(x, y, test_size=0.1, valid_size=0.1, train_size=None, random_state=None, shuffle=True, stratify=None):
    if test_size != None:
        dx, ex, dy, ey = sklms.train_test_split(x, y, test_size=test_size, train_size=None, random_state=random_state, shuffle=shuffle, stratify=None)
        tx, vx, ty, vy = sklms.train_test_split(dx, dy, test_size=valid_size, train_size=train_size, random_state=random_state, shuffle=shuffle, stratify=None)
    else:
        dx, vx, vy, vy = sklms.train_test_split(x, y, test_size=valid_size, train_size=None, random_state=random_state, shuffle=shuffle, stratify=None)
        tx, ex, ty, ey = sklms.train_test_split(dx, dy, test_size=test_size, train_size=train_size, random_state=random_state, shuffle=shuffle, stratify=None)
    return tx, ty, vx, vy, ex, ey


def npsave(name, data):
    return np.save("gen/%s" % name, data)


def npload(name):
    return np.load("gen/%s.npy" % name)


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
        print(v)
        l[i] = cv.imread(v, cv.IMREAD_COLOR)
    return l


def readimg2(imglist):
    """
    Load a list of images.

    :param list<str> imglist: List of URLs of images.
    :returns list<ndarray>: List of images.
    """
    l = list()
    for v in imglist:
        l.append(cv.imread(v, cv.IMREAD_COLOR))
    return l


def hsv(img):
    """
    Convert an image from BGR to HSV.

    :param ndarray img: BGR image
    :returns ndarray: HSV image
    """
    return cv.cvtColor(img, cv.COLOR_BGR2HSV)


def hsvlist(imglist):
    """
    Convert a list of images from BGR to HSV.

    :param list<ndarray> imglist: list of BGR images
    :returns list<ndarray>: list of HSV images
    """
    return list(map(hsv, imglist))


def absurl2(url):
    """
    Create a URL for resized photos.
    """
    cwd = os.getcwd()
    url = os.path.abspath(url)
    url = url.replace(cwd, '')
    url = os.path.join('resize', url)
    url = os.path.abspath(url)
    return url


def mkdirs(filename):
    """Make directories given Windows style path."""
    name = os.path.dirname(filename)
    os.makedirs(name, exist_ok=True)
    return


def resize_img(filename):
    img = cv.imread(filename, cv.IMREAD_COLOR)
    img2 = cv.resize(img, res_resize, interpolation=cv.INTER_CUBIC)
    return img2


class Csv(object):
    def __init__(self, url: str):
        self._url = url

    def as_list(self) -> List[List[Any]]:
        """
        Reads CSV file to a list.
        """
        with open(self._url, 'r') as f:
            reader = csv.reader(f)
            your_list = list(reader)
        return your_list

    def get_col(self, n: int) -> np.ndarray[str]:
        """
        Get column from data file.

        :param int n: Index (zero based) of column to extract.
        :returns ndarray: column of data
        """
        csv = self.as_list()
        csv = np.asarray(csv)
        return csv[:, n]

    def get_col_int(self, n: int) -> np.ndarray[int]:
        return intize(self.get_col(n))


def class_str_int(a):
    """
    Convert class string to integer representation.
    """
    return [classdict[i] for i in a]


def class_int_str(a):
    """
    Convert class string to integer representation.
    """
    return [classdict2[i] for i in a]


def class_onehot(a):
    """
    Convert integer representation to one hot representation.
    """
    size = (len(a), 6)
    b = np.zeros(size)
    for i, v in enumerate(a):
        b[i][v] = 1
    return b


def intize(txtarray):
    """
    Convert a list of strings to integers.
    """
    return [int(i) for i in txtarray]


def floatize(txtarray):
    """
    Convert a list of strings to floats.
    """
    return [float(i) for i in txtarray]


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
