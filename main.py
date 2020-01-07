from __future__ import annotations

import os
from os.path import isfile
from typing import Any, Dict, List, Tuple, Union

import dill
import keras
import numpy as np
from keras.callbacks import (Callback, CSVLogger, ModelCheckpoint,
                             ReduceLROnPlateau)
from keras.models import load_model

import cv2 as cv
from cc import Ccr
from dataset import DataSet, DataSetSplit
from jl import ListFile, Url, mkdirs, resize_img
from model import LOSS, METRIC, OPTIMIZER, Architecture
from rater import Smi13

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# ccr = Ccr()
# # ccr.prepare()
# smi13_1 = Architecture(Smi13(), LOSS[14], OPTIMIZER[0], METRIC[0])
# ccr1 = ArchitectureSet(smi13_1, ccr)
# ccr1_1 = ccr1.split(1)
# # ccr1_1.reset()
# ccr1_1.train()

# ccc_prep()
# model.ccc()
# train('vgg16', 'ccc', 1)
# test('vgg16', 'ccc', 1)
# predict('vgg16', 'ccc', 1)

# ccc_prep()
# model.ccc2()
# train('vgg16a', 'ccc', 1)
# test('vgg16a', 'ccc', 1)
# predict('vgg16a', 'ccc', 1)

# ccc_prep()
# model.ccc3()
# train('vgg16b', 'ccc', 1)
# test('vgg16b', 'ccc', 1)
# predict('vgg16b', 'ccc', 1)

# ccr_prep()
# model.ccr()
# train('kcnn', 'ccr', 1, custom=model.custom_rmse)
# test('kcnn', 'ccr', 1, custom=model.custom_rmse)
# predict('kcnn', 'ccr', 1, custom=model.custom_rmse)

# lamem_prep_all()
# model.lamem()
# train('kcnn', 'lamem', 1, custom=model.custom_rmse)
# test('kcnn', 'lamem', 1, custom=model.custom_rmse)
# predict('kcnn', 'lamem', 1, custom=model.custom_rmse)
