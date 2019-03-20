import url2
import os
import cv2 as cv
import classifier
import rater
import analyzer
import numpy as np
import jl
from keras.models import load_model
from keras.applications.vgg16 import VGG16
import keras
from keras.callbacks import CSVLogger, ModelCheckpoint, Callback


def ccr_prep():
    return


def ccc_x(split, n):
    return 'calclarclass%d%sx' % (n, split)


def ccc_y(split, n):
    return 'calclarclass%d%sy' % (n, split)


def ccc_prep():
    print("Reading data file")
    x = jl.getcol(0)
    y = jl.getcol(2)
    y = jl.class_str_int(y)
    print('Generating data splits')
    tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
    print('Converting to one hot')
    ty = keras.utils.to_categorical(ty, num_classes=6, dtype='int32')
    vy = keras.utils.to_categorical(vy, num_classes=6, dtype='int32')
    ey = keras.utils.to_categorical(ey, num_classes=6, dtype='int32')
    print('Saving')
    jl.npsave(ccc_x('train', 1), tx)
    jl.npsave(ccc_x('valid', 1), vx)
    jl.npsave(ccc_x('test', 1), ex)
    jl.npsave(ccc_y('train', 1), ty)
    jl.npsave(ccc_y('valid', 1), vy)
    jl.npsave(ccc_y('test', 1), ey)
    print('Prep complete')
    return


def categ():
    """
    Rip classes from the data file.
    Change each class into an integer.
    Save as text file.
    """
    col = jl.getcol(2)
    num = jl.class_str_int(col)
    jl.writetxt(jl.TEXT_CLASSES, num)
    return


def src_url():
    """
    Rip the relative Unix style URLs from the data file.
    Format the URLS into absolute Windows style.
    Save as text file.
    """
    with open(jl.TEXT_URL_RAW, 'w') as f:
        for i in jl.getcol(0):
            url = i.strip()
            url = os.path.abspath(url)
            print(url, file=f)
    return


def dst_url():
    """
    Load raw URLs.
    Convert to resized URLS.
    Write to file.
    """
    a = jl.readtxt(jl.TEXT_URL_RAW)
    b = [jl.absurl2(i) for i in a]
    jl.writetxt(jl.TEXT_URL_PROCESSED, b)
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


def rateurl():
    src_url()
    dst_url()
    return


def rate_create_img_npy():
    txt = jl.readtxt(jl.TEXT_URL_PROCESSED)
    img = jl.readimg(txt)
    jl.npsave(jl.NPY_PHOTOS, img)
    return


def rate_create_rate_npy():
    strs = jl.getcol(1)
    ints = jl.intize(strs)
    ints = np.asarray(ints)
    jl.npsave(jl.NPY_RATE, ints)
    return


def resize_imgs(src_list, dst_list):
    urls1 = jl.readtxt(src_list)
    urls2 = jl.readtxt(dst_list)
    resize_imgs2(urls1, urls2)
    return


def resize_imgs2(src_list, dst_list):
    for src, dst in zip(src_list, dst_list):
        print(src)
        print(dst)
        img2 = jl.resize_img(src)
        jl.mkdirs(dst)
        cv.imwrite(dst, img2)
    print('done')
    return


def main():
    """
    Prepare data files, classify, and analyze pipeline.
    """
    categ()
    src_url()
    url2.main()
    dst_url()
    classesonehot()
    resize_imgs(jl.TEXT_URL_RAW, jl.TEXT_URL_PROCESSED)
    classifier.main()
    # train()
    predict()
    analyzer.main()
    return


def rater_filter():
    rate = jl.npload(jl.NPY_RATE)
    a = [i == 1 or i == 3 for i in rate]
    b = jl.npload(jl.NPY_PHOTOS)[a]
    c = rate[a]
    jl.npsave(jl.NPY_PHOTOS, b)
    jl.npsave(jl.NPY_RATE, c)
    return


def lamem_read(txt):
    filename = 'lamem/splits/%s.txt' % (txt)
    b = np.asarray([line.split(' ') for line in jl.readtxt(filename)])
    x = np.asarray(b[:, 0])
    y = np.asarray([float(x) for x in b[:, 1]])
    return x, y


def lamem_rel_url(url):
    a = os.path.join(os.getcwd(), 'lamem/images', url)
    return os.path.normpath(a)


def lamem_data_url(name, n):
    return '%s_%d' % (name, n)


def lamem_x_url(name, n):
    return '%d%sx' % (name, n)


def lamem_y_url(name, n):
    return '%d%sy' % (name, n)


def lamem_prep_txt(name, n):
    x, y = lamem_read(lamem_data_url(name, n))
    x = np.asarray([lamem_rel_url(url) for url in x])
    y = np.asarray(y)
    jl.npsave(lamem_x_url(name, n), x)
    jl.npsave(lamem_y_url(name, n), y)
    return


def lamem_prep_split(n):
    lamem_prep_txt('train', n)
    lamem_prep_txt('val', n)
    lamem_prep_txt('test', n)
    return


def lamem_prep_all():
    lamem_prep_split(1)
    lamem_prep_split(2)
    lamem_prep_split(3)
    lamem_prep_split(4)
    lamem_prep_split(5)
    return


def rater_prep():
    rateurl()
    rate_create_img_npy()
    rate_create_rate_npy()
    rater_filter()
    return


class Sequence1(keras.utils.Sequence):

    def __init__(self, x_set, y_set, batch_size):
        self.x = x_set
        self.y = y_set
        self.batch_size = batch_size

    def __len__(self):
        a = float(len(self.x)) / float(self.batch_size)
        a = int(np.ceil(a))
        return a

    def __getitem__(self, idx):
        a = idx * self.batch_size
        b = (idx + 1) * self.batch_size
        batch_x = self.x[a:b]
        batch_y = self.y[a:b]
        xx = np.asarray([jl.resize_img(filename) for filename in batch_x])
        yy = np.asarray(batch_y)
        return xx, yy


class TerminateOnDemand(Callback):
    """
    Callback that terminates training when a NaN loss is encountered.
    """

    def on_epoch_end(self, epoch, logs=None):
        with open('gen/terminate.txt', 'r') as f:
            a = f.read()
            if a == 'die':
                print('Manual early terminate command found in gen/terminate.txt')
                self.stopped_epoch = epoch
                self.model.stop_training = True


def train(modelfile, train_x, train_y, valid_x, valid_y, epochs, custom=None):
    print('Loading training X')
    x1 = jl.npload(train_x)
    print('Loading training Y')
    y1 = jl.npload(train_y)
    print('Loading validation X')
    x2 = jl.npload(valid_x)
    print('Loading validation Y')
    y2 = jl.npload(valid_y)
    print('Loading architecture')
    model = load_model(modelfile, custom_objects=custom)
    print('Training sequence')
    seq1 = Sequence1(x1, y1, 10)
    print('Validation sequence')
    seq2 = Sequence1(x2, y2, 10)
    print('Training starts')
    term = TerminateOnDemand()
    save = ModelCheckpoint(modelfile, verbose=1, period=1)
    csv = CSVLogger('gen/training.log', append=True)
    model.fit_generator(
        generator=seq1,
        epochs=epochs,
        verbose=1,
        validation_data=seq2,
        shuffle=False,
        initial_epoch=0,
        callbacks=[save, csv, term]
    )
    print('Training finished')
    return


def rater_valid():
    model = load_model(jl.H5_RATER, custom_objects={'rmse': rater.rmse})
    validx = jl.npload('train_1_13')
    validy = jl.npload('train_1_13_rates')
    test_loss = model.evaluate(validx, validy, batch_size=15)[0]
    print(test_loss)
    return


def rater_test():
    model = load_model(jl.H5_RATER, custom_objects={'rmse': rater.rmse})
    testx = jl.npload('train_1_14')
    testy = jl.npload('train_1_14_rates')
    test_loss = model.evaluate(testx, testy, batch_size=15)[0]
    print(test_loss)
    return


def rater_predict():
    """
    Predict using trained rater.
    """
    # x = jl.npload(jl.NPY_PHOTOS)
    x = jl.readimg(['test.jpg'])
    model = load_model(jl.H5_RATER)
    p = model.predict(x, batch_size=15)
    jl.npsave(jl.NPY_PREDRATE, p)
    jl.writetxt("singlepred.txt", p)
    return


# main()
# rater.main()
# classifier.main()
# rater_prep()
# trainrater()
# rater_train3()
# rater_valid()
# rater_test()
# rater_predict()
# calclar_class_prep()
train(jl.H5_CLASSIFIER, ccc_x('train', 1), ccc_y('train', 1), ccc_x('valid', 1), ccc_y('valid', 1), 10000)
# train(jl.H5_RATER, 'train1x', 'train1y', 'val1x', 'val1y', 10000, {'rmse': rater.rmse})
