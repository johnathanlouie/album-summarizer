import csv
import os
import time
from typing import Any, Dict, List, Tuple, Union

from numpy import asarray, load, ndarray, save, zeros

import cv2 as cv

Url = str
ArrayLike = Union[ndarray, List[Any]]
Image = ndarray

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


def res3(n: int):
    """
    Returns dimensions of an array of images.
    """
    return (n, h, w, 3)


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


def npsave(name: str, data: ArrayLike) -> None:
    """
    Saves to a binary NumPy file.
    """
    url = "gen/%s" % name
    mkdirs(url)
    return save(url, data)


def npload(name: str) -> ArrayLike:
    """
    Loads an array-like object from a binary NumPy file.
    """
    return load("gen/%s.npy" % name)


def readimg(imglist: List[Url]) -> ndarray:
    """
    Loads an array of images.

    :param list<str> imglist: List of URLs of images.
    :returns ndarray: Array of images.
    """
    size = len(imglist)
    l = ndarray(res3(size))
    for i, v in enumerate(imglist):
        print(v)
        l[i] = cv.imread(v, cv.IMREAD_COLOR)
    return l


def readimg2(imglist: List[Url]) -> List[Image]:
    """
    Loads a list of images.

    :param list<str> imglist: List of URLs of images.
    :returns list<ndarray>: List of images.
    """
    l = list()
    for v in imglist:
        l.append(cv.imread(v, cv.IMREAD_COLOR))
    return l


def hsv(img: Image) -> Image:
    """
    Converts an image from BGR to HSV.

    :param ndarray img: BGR image
    :returns ndarray: HSV image
    """
    return cv.cvtColor(img, cv.COLOR_BGR2HSV)


def hsvlist(imglist: List[Image]) -> List[Image]:
    """
    Converts a list of images from BGR to HSV.

    :param list<ndarray> imglist: list of BGR images
    :returns list<ndarray>: list of HSV images
    """
    return list(map(hsv, imglist))


def absurl2(url: Url) -> Url:
    """
    Creates a URL for resized photos.
    """
    cwd = os.getcwd()
    url = os.path.abspath(url)
    url = url.replace(cwd, '')
    url = os.path.join('resize', url)
    url = os.path.abspath(url)
    return url


def mkdirs(filename: Url) -> None:
    """
    Makes directories given Windows style path.
    """
    name = os.path.dirname(filename)
    os.makedirs(name, exist_ok=True)
    return


def resize_img(filename: Url) -> Image:
    """
    Returns a resized image.
    """
    img = cv.imread(filename, cv.IMREAD_COLOR)
    img2 = cv.resize(img, res_resize, interpolation=cv.INTER_CUBIC)
    return img2


def class_onehot(a: List[int]) -> ndarray:
    """
    Converts integer representation to one hot representation.
    """
    size = (len(a), 6)
    b = zeros(size)
    for i, v in enumerate(a):
        b[i][v] = 1
    return b


def intize(txtarray: List[str]) -> List[int]:
    """
    Converts a list of strings to integers.
    """
    return [int(i) for i in txtarray]


def floatize(txtarray: List[str]) -> List[float]:
    """
    Converts a list of strings to floats.
    """
    return [float(i) for i in txtarray]


class ListFile(object):
    """
    Represents a text file. Each line represents an item.
    """

    def __init__(self, url: Url) -> None:
        self._url = url
        return

    def read(self) -> List[str]:
        """
        Loads a newline separated value file as strings.
        """
        with open(self._url, 'r') as f:
            a = f.read()
            a = a.split('\n')
            a = list(filter(len, a))
        return a

    def read_as_int(self) -> List[int]:
        """
        Loads a newline separated value file as integers.
        """
        return intize(self.read())

    def read_as_floats(self) -> List[float]:
        """
        Loads a newline separated value file as floating point numbers.
        """
        return floatize(self.read())

    def write(self, array: List[Any]) -> None:
        """
        Saves in newline separated value format.
        """
        with open(self._url, 'w') as f:
            for i in array:
                print(i, file=f)
        return

    def append(self, array: List[Any]) -> None:
        """
        Appends to newline separated value format.
        """
        with open(self._url, 'a') as f:
            for i in array:
                print(i, file=f)
        return


class Stopwatch(object):
    """
    Keeps track of time elapsed.
    """

    def __init__(self):
        self._start = time.time()

    def elapsed(self) -> float:
        """
        Returns the time since instance creation in seconds.
        """
        return time.time() - self._start

    def print(self) -> None:
        """
        Prints the time elapsed in minutes and seconds.
        """
        minutes, sec = divmod(self.elapsed(), 60)
        print('time: %d:%02d' % (minutes, sec))
        return

    def reset(self) -> None:
        """
        Resets the elapsed time.
        """
        self._start = time.time()
        return


class Csv(object):
    """
    Represents a comma separated value file.
    """

    def __init__(self, url: Url):
        self._url = url

    def as_list(self) -> List[List[str]]:
        """
        Reads CSV file to a list.
        """
        with open(self._url, 'r') as f:
            reader = csv.reader(f)
            your_list = list(reader)
        return your_list

    def get_col(self, n: int) -> List[str]:
        """
        Gets a column from the CSV file. All elements are strings.
        """
        csv = self.as_list()
        csv = asarray(csv)
        return csv[:, n].tolist()

    def get_col_int(self, n: int) -> List[int]:
        """
        Gets a column from the CSV file. All elements are integers.
        """
        return intize(self.get_col(n))


def resize_imgs(src: Url, dst: Url) -> None:
    """
    Resizes the images based on the list of URLs found in the source file and outputs to the list of URLs found in the destination file.
    """
    urls1 = ListFile(src).read()
    urls2 = ListFile(dst).read()
    resize_imgs2(urls1, urls2)
    return


def resize_imgs2(src_list: List[Url], dst_list: List[Url]) -> None:
    """
    Resizes a list of images.
    """
    for src, dst in zip(src_list, dst_list):
        print(src)
        print(dst)
        img2 = resize_img(src)
        mkdirs(dst)
        cv.imwrite(dst, img2)
    print('done')
    return
