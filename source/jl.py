from csv import reader
from os import getcwd, makedirs, walk
from os.path import abspath, basename, dirname, isdir, isfile, join, normpath
from random import sample
from shutil import copy2
from time import time
from typing import Any, Dict, List, Optional, Tuple, Union

from numpy import asarray, load, ndarray, save, zeros

import cv2 as cv


"""Type aliases"""
Url = str
ArrayLike = Union[ndarray, List[Any]]
Image = ndarray
Number = Union[int, float]

TEXT_CLASSES = 'out/categ.txt'
TEXT_PRED = 'out/pred.txt'
TEXT_RATE = 'out/rate.txt'

TEXT_CLUSTER_SIFT = 'out/cl1.txt'
TEXT_CLUSTER_HISTOGRAM = 'out/cl2.txt'
TEXT_CLUSTER_COMBINED = 'out/cl3.txt'
TEXT_CLUSTER_COMBINED2 = 'out/cl4.txt'

NPY_CLASSES = 'categ'
NPY_PHOTOS = 'photos'
NPY_PHOTOS2 = 'photos2'
NPY_PRED = 'pred'
NPY_PREDRATE = 'predrate'
NPY_DESC = 'desc'
NPY_RATE = 'rate'

JSON_SIMILARITYMATRIX = 'out/sim.json'


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
    url = "out/%s" % name
    mkdirs(url)
    return save(url, data)


def npload(name: str) -> ArrayLike:
    """
    Loads an array-like object from a binary NumPy file.
    """
    return load("out/%s.npy" % name, allow_pickle=True)


def npexists(name: str) -> bool:
    """
    Returns true if the file exists.
    """
    return isfile("out/%s.npy" % name)


def read_image(url: Url) -> Image:
    return cv.imread(url, cv.IMREAD_COLOR)


def readimg(urls: List[Url]) -> ndarray:
    """
    Loads an array of images.
    Images must be uniformly sized.
    """
    count = len(urls)
    l = ndarray(res3(count))
    for i, url in enumerate(urls):
        print(url)
        l[i] = read_image(url)
    return l


def readimg2(urls: List[Url]) -> List[Image]:
    """
    Loads a list of images.
    """
    return [read_image(i) for i in urls]


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
    cwd = getcwd()
    url = abspath(url)
    url = url.replace(cwd, '')
    url = join('resize', url)
    url = abspath(url)
    return url


def mkdirs(filename: Url) -> None:
    """
    Makes directories leading up to a file.
    The child is not included.
    """
    name = dirname(filename)
    makedirs(name, exist_ok=True)
    return


def mkdirs2(path: Url) -> None:
    """
    Make all directories in a path including the child.
    """
    makedirs(path, exist_ok=True)
    return


def resize_img(filename: Url) -> Image:
    """
    Returns a resized image.
    """
    if not isfile(filename):
        raise FileNotFoundError(filename)
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
        self._start = time()

    def elapsed(self) -> float:
        """
        Returns the time since instance creation in seconds.
        """
        return time() - self._start

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
        self._start = time()
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
            r = reader(f)
            your_list = list(r)
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


def list_files(directory: Url, recursive: bool) -> List[Url]:
    """
    Returns the URLs of all the files in the directory and its subdirectories.
    """
    a = list()
    for path, _, filenames in walk(directory):
        for f in filenames:
            a.append(abspath(join(path, f)))
        if not recursive:
            break
    return a


def random_sample(population: List[Any], k: Optional[int] = None) -> List[Any]:
    if k == None:
        return population
    if k > len(population) or k < 0:
        raise ValueError
    return sample(population, k)


class ImageDirectory(object):
    """
    Represents a directory and its subdirectories containing image files.
    """

    def __init__(self, url: Url) -> None:
        if not isdir(url):
            raise NotADirectoryError
        self._url = url

    @staticmethod
    def jpeg_filter(url: Url) -> bool:
        """
        Returns true if a URL is a JPEG.
        """
        url = url.lower()
        return url.endswith('.jpg') or url.endswith('.jpeg')

    def jpeg(self, recursive: bool, k: Optional[int] = None) -> List[Url]:
        """
        Returns a list of JPEG files from this directory.
        """
        files = list_files(self._url, recursive)
        images = list(filter(self.jpeg_filter, files))
        images = random_sample(images, k)
        return images


class ProgressBar(object):
    """
    A progress bar for loops.
    """

    def __init__(self, count: int) -> None:
        self._iteration = 0
        self._total = count
        self._print(0, count)
        return

    @staticmethod
    def _print(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, length=100, fill='\u2588', print_end='\r') -> None:
        """
        Prints the progress bar.
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print("\r%s |%s| %s%% %s" % (prefix, bar, percent, suffix), end=print_end)
        if iteration == total:
            print()
        return

    def update(self) -> None:
        """
        Updates the progress bar and then prints.
        """
        self._iteration = self._iteration + 1
        self._print(self._iteration, self._total)
        return


def parent_directory(url: Url) -> Url:
    """
    Returns the name of the immediate parent.
    """
    return basename(dirname(url))


def copy_file(file_: Url, directory: Url, ancestors: int = 0) -> None:
    """
    Copies a file, optionally including any ancestors, to a new directory.
    """
    directory = normpath(directory)
    file_ = normpath(file_)
    new_url = basename(file_)
    path = dirname(file_)
    for _ in range(ancestors):
        parent = basename(path)
        new_url = join(parent, new_url)
        path = dirname(path)
    new_url = join(directory, new_url)
    mkdirs(new_url)
    try:
        copy2(file_, new_url)
    except PermissionError:
        raise PermissionError("Copy \"%s\" to \"%s\"." % (file_, new_url))
    return
