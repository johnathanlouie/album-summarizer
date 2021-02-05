from os import getcwd
from os.path import join, normpath
from typing import Any, List, Optional, Union

from core import modelbuilder
from core.dataset import DataSet, Predictions, PredictionsFactory
from jl import ImageDirectory, Url
from numpy import asarray, ndarray

from dataset.cc import CcDataFile


class AnimalCollection(ImageDirectory):
    """
    Represents a directory and its subdirectories containing images of animals.
    From ImageNet.
    http://www.image-net.org/
    """

    def __init__(self) -> None:
        super().__init__('data/animals')


class FoodCollection(ImageDirectory):
    """
    Represents a directory and its subdirectories containing images of food.
    From Food-101.
    https://www.vision.ee.ethz.ch/datasets_extra/food-101/
    """

    def __init__(self) -> None:
        super().__init__('data/food')


class CccafPredictions(Predictions):
    """
    """

    def human_readable(self) -> List[Any]:
        """
        """
        return CcDataFile().to_category_str(self._y)


class CccafPredictionsFactory(PredictionsFactory):
    """
    """

    def __init__(self):
        pass

    def predictions(self, x: ndarray, y: ndarray) -> Predictions:
        """
        Returns an instance of CccafPredictions.
        """
        return CccafPredictions(x, y)


class CccafDataSet(DataSet):
    """
    The CC dataset combined with a subsection of Animals and a subsection of Food-101.
    The CC dataset does not have enough animals and food photos.
    """

    NAME = 'cccaf'
    OUTPUT_NUM: int = 6

    def __init__(self, animals: Optional[int] = None, food: Optional[int] = 1300) -> None:
        if animals == None:
            animals = len(AnimalCollection().jpeg(True))
        if food == None:
            food = len(FoodCollection().jpeg(True))
        self._animal_num = animals
        self._food_num = food
        return

    def _relative_url(self, url: Url) -> str:
        """
        Returns the relative url of the image from the filename.
        """
        a = join(getcwd(), 'data', 'cc', url)
        return normpath(a)

    def _x(self) -> ndarray:
        """
        Returns an array of URLs to the images.
        Combines the 3 sources together.
        """
        data_file = CcDataFile()
        x = data_file.url()
        x = [self._relative_url(i) for i in x]
        x2 = AnimalCollection().jpeg(True, self._animal_num)
        x3 = FoodCollection().jpeg(True, self._food_num)
        x4 = x + x2 + x3
        return asarray(x4)

    def _y(self) -> ndarray:
        """
        Returns the Y.
        Combines the 3 sources together.
        """
        data_file = CcDataFile()
        animal_class = data_file.categories['animal']
        food_class = data_file.categories['food']
        y = data_file.category_as_int()
        y2 = [animal_class] * self._animal_num
        y3 = [food_class] * self._food_num
        y4 = asarray(y + y2 + y3)
        y4 = self.one_hot(y4, 6)
        return y4

    def prepare(self) -> None:
        """
        Prepares NumPy files for Keras training.
        """
        x = self._x()
        y = self._y()
        print('Generating data splits')
        for i in range(self.splits()):
            self.create_split(x, y, i)
        print('Prep complete')
        return

    def splits(self) -> int:
        """
        Returns the number of splits.
        """
        return 5

    def _predictions_factory(self) -> PredictionsFactory:
        """
        See base class.
        """
        return CccafPredictionsFactory()


modelbuilder.ModelBuilder.dataset(CccafDataSet())
