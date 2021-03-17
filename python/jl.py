from csv import reader
from os import getcwd, makedirs, walk
from os.path import abspath, basename, dirname, isdir, isfile, join, normpath
from random import sample
from shutil import copy2
from time import time
from typing import Any, List, Optional, Tuple

import cv2 as cv
from numpy import asarray, load, ndarray, save, zeros

from typing2 import ArrayLike, Image, ImageArray, IntClass, OneHot, Url


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


def npsave(name: str, data: ArrayLike, verbose: bool = True) -> None:
    """
    Saves to a binary NumPy file.
    """
    url = "out/%s" % name
    mkdirname(url)
    if verbose:
        print('Saving %s.npy' % url)
    return save(url, data)


def npload(name: str, verbose: bool = True) -> ArrayLike:
    """
    Loads an array-like object from a binary NumPy file.
    """
    url = 'out/%s.npy' % name
    if verbose:
        print('Loading %s' % url)
    return load(url, allow_pickle=True)


def npexists(name: str) -> bool:
    """
    Returns true if the file exists.
    """
    return isfile("out/%s.npy" % name)


def read_image(image: Url) -> Image:
    return cv.imread(image, cv.IMREAD_COLOR)


def readimg2(images: List[Url]) -> List[Image]:
    """
    Loads a list of images.
    """
    return [read_image(i) for i in images]


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


def mkdirs(path: Url, verbose: bool = True) -> None:
    """
    Make all directories in a path including the child.
    """
    if verbose:
        print('Making %s' % path)
    makedirs(path, exist_ok=True)


def mkdirname(filename: Url, verbose: bool = True) -> None:
    """
    Makes directories leading up to a file.
    The child is not included.
    """
    path = dirname(filename)
    mkdirs(path, verbose)


class Resolution(object):
    """
    Image resolution data structure.
    """

    def __init__(self, h: int, w: Optional[int] = None, channels: int = 3):
        super().__init__()
        self._h = h
        self._w = w
        if w == None:
            self._w = h
        self._c = channels

    def hw(self) -> Tuple[int, int]:
        """
        Returns the resolution in height-weight format.
        """
        return (self._h, self._w)

    def wh(self) -> Tuple[int, int]:
        """
        Returns the resolution in weight-height format.
        """
        return (self._w, self._h)

    def hwc(self) -> Tuple[int, int, int]:
        """
        Returns the resolution in height-weight-channels format.
        """
        return (self._h, self._w, self._c)

    def array_hwc(self, n: int) -> Tuple[int, int, int, int]:
        """
        Returns the resolution in arraysize-height-weight-channels format.
        """
        return (n, self._h, self._w, self._c)


def resize_img(image: Url, res: Resolution) -> Image:
    """
    Returns a resized image.
    """
    if not isfile(image):
        raise FileNotFoundError(image)
    img = cv.imread(image, cv.IMREAD_COLOR)
    img2 = cv.resize(img, res.wh(), interpolation=cv.INTER_CUBIC)
    return img2


def read_images(images: List[Url], res: Resolution) -> ImageArray:
    """
    Loads an array of images.
    Images must be uniformly sized.
    """
    count = len(images)
    l = ndarray(res.array_hwc(count))
    for i, url in enumerate(images):
        print(url)
        l[i] = read_image(url)
    return l


def class_onehot(a: List[IntClass]) -> OneHot:
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


def resize_imgs(src: Url, dst: Url, res: Resolution) -> None:
    """
    Resizes the images based on the list of URLs found in the source file and outputs to the list of URLs found in the destination file.
    """
    urls1 = ListFile(src).read()
    urls2 = ListFile(dst).read()
    resize_imgs2(urls1, urls2, res)


def resize_imgs2(src_list: List[Url], dst_list: List[Url], res: Resolution) -> None:
    """
    Resizes a list of images.
    """
    for src, dst in zip(src_list, dst_list):
        print(src)
        print(dst)
        img2 = resize_img(src, res)
        mkdirname(dst)
        cv.imwrite(dst, img2)
    print('done')


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
    mkdirname(new_url)
    try:
        copy2(file_, new_url)
    except PermissionError:
        raise PermissionError("Copy \"%s\" to \"%s\"." % (file_, new_url))
    return
