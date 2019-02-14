import url2
import resize
import classifier
import analyzer
import numpy as np
import jl
from keras.models import load_model
from keras.applications.vgg16 import VGG16


def categ():
    col = jl.getcol(2)
    num = jl.numberize(col)
    jl.writetxt(jl.TEXT_CLASSES, num)
    # oh = jl.onehot(num)
    # np.save('categ', oh)
    return


def url():
    with open(jl.TEXT_URL_RAW, 'w') as f:
        for i in jl.getcol(0):
            url = i.strip()
            url = jl.winslash(url)
            url = jl.absurl(url)
            print(url, file=f)
    return


def prep():
    a = jl.readtxt(jl.TEXT_URL_RAW)
    b = list(map(jl.absurl2, a))
    jl.writetxt(jl.TEXT_URL_PROCESSED, b)
    d = jl.readtxt(jl.TEXT_CLASSES)
    d = jl.intize(d)
    oh = jl.onehot(d)
    jl.npsave(jl.NPY_CLASSES, oh)
    return


def vggweights():
    vg = VGG16()
    for i in jl.layers:
        w = vg.get_layer(i).get_weights()
        np.save(i, w)
    return


def train():
    x = jl.npload(jl.NPY_PHOTOS)
    y = jl.npload(jl.NPY_CLASSES)
    model = load_model(jl.H5_CLASSIFIER)
    model.fit(x, y, shuffle=True, epochs=9, batch_size=15)
    model.save(jl.H5_CLASSIFIER)
    return


def predict():
    x = jl.npload(jl.NPY_PHOTOS)
    model = load_model(jl.H5_CLASSIFIER)
    p = model.predict(x, batch_size=15)
    jl.npsave(jl.NPY_PRED, p)
    return


def main():
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


main()
