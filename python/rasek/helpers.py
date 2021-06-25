import os

from rasek.typing2 import Url
from typing import Any, List, Optional
import random


def is_image(filepath: Url) -> bool:
    """
    Returns true if the file extension is of an image.
    """
    _, ext = os.path.splitext(filepath)
    return ext.lower() in [
        '.jpeg',
        '.jpg',
        '.png',
    ]


def list_files(directory: Url, recursive: bool = False, absolute: bool = True) -> List[Url]:
    """
    Returns the URLs of all the files in the directory and its subdirectories.
    """
    files = list()
    for path, _, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(path, filename)
            if absolute:
                filepath = os.path.abspath(filepath)
            files.append(filepath)
        if not recursive:
            break
    return files


def sample(population: List[Any], k: Optional[int] = None, strict: bool = True) -> List[Any]:
    if k == None:
        return population
    if k < 0:
        raise ValueError
    if k > len(population):
        if strict:
            raise ValueError
        else:
            return population
    return random.sample(population, k)
