import url2
import resize
import classifier
import analyzer
import numpy as np
import jl
from keras.models import load_model
from keras.applications.vgg16 import VGG16


def categ():
    """
    Rip classes from the data file.
    Change each class into an integer.
    Save as text file.
    """
    col = jl.getcol(2)
    num = jl.numberize(col)
    jl.writetxt(jl.TEXT_CLASSES, num)
    return


def url():
    """
    Rip the relative Unix style URLs from the data file.
    Format the URLS into absolute Windows style.
    Save as text file.
    """
    with open(jl.TEXT_URL_RAW, 'w') as f:
        for i in jl.getcol(0):
            url = i.strip()
            url = jl.winslash(url)
            url = jl.absurl(url)
            print(url, file=f)
    return


def prep():
    """
    Load raw URLs.
    Convert to resized URLS.
    Write to file.
    Load classes. String integers.
    Change to int type.
    Change to one hot type.
    Save to file.
    """
    a = jl.readtxt(jl.TEXT_URL_RAW)
    b = list(map(jl.absurl2, a))
    jl.writetxt(jl.TEXT_URL_PROCESSED, b)
    d = jl.readtxt(jl.TEXT_CLASSES)
    d = jl.intize(d)
    oh = jl.onehot(d)
    jl.npsave(jl.NPY_CLASSES, oh)
    return


def vggweights():
    """
    Save pretrained VGG16 weights by layer.
    """
    vg = VGG16()
    for i in jl.layers:
        w = vg.get_layer(i).get_weights()
        np.save(i, w)
    return


def train():
    """
    Train classifier.
    """
    x = jl.npload(jl.NPY_PHOTOS)
    y = jl.npload(jl.NPY_CLASSES)
    model = load_model(jl.H5_CLASSIFIER)
    model.fit(x, y, shuffle=True, epochs=9, batch_size=15)
    model.save(jl.H5_CLASSIFIER)
    return


def predict():
    """
    Predict using trained classifier.
    """
    x = jl.npload(jl.NPY_PHOTOS)
    model = load_model(jl.H5_CLASSIFIER)
    p = model.predict(x, batch_size=15)
    jl.npsave(jl.NPY_PRED, p)
    return


def main():
    """
    Prepare data files, classify, and analyze pipeline.
    """
    categ()
    url()
    url2.main()
    prep()
    resize.main()
    classifier.main()
    train()
    predict()
    analyzer.main()
    return


def trainrater():
    rate = jl.getcol(1)
    # jl.writetxt(jl.TEXT_RATE, rate)
    # jl.npsave(jl.NPY_RATE, rate)
    x = jl.readtxt(jl.TEXT_URL_PROCESSED)
    for i in x:
        print(i)
    # x = np.asarray(x)
    # x = jl.readimg(x)
    # jl.npsave(jl.NPY_PHOTOS2, x)
    # x = jl.npload(jl.NPY_PHOTOS)
    # y = jl.npload(jl.NPY_CLASSES)
    # model = load_model(jl.H5_RATER)
    # model.fit(x, rate, shuffle=True, epochs=9, batch_size=15)
    # model.save(jl.H5_RATER)
    return


# main()
trainrater()
