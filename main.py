import os
import cv2 as cv
import numpy as np
import jl
from keras.models import load_model
import keras
from keras.callbacks import CSVLogger, ModelCheckpoint, Callback
import model


def ccc_x(split, n):
    return 'ccc%d%sx' % (n, split)


def ccc_y(split, n):
    return 'ccc%d%sy' % (n, split)


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
    jl.npsave(ccc_y('train', 1), ty)
    jl.npsave(ccc_x('val', 1), vx)
    jl.npsave(ccc_y('val', 1), vy)
    jl.npsave(ccc_x('test', 1), ex)
    jl.npsave(ccc_y('test', 1), ey)
    print('Prep complete')
    return


def ccr_x(split, n):
    return 'ccr%d%sx' % (n, split)


def ccr_y(split, n):
    return 'ccr%d%sy' % (n, split)


def ccr_prep():
    print("Reading data file")
    x = jl.getcol(0)
    y = jl.getcol(1)
    y = jl.intize(y)
    print('Generating data splits')
    tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
    print('Saving')
    jl.npsave(ccr_x('train', 1), tx)
    jl.npsave(ccr_y('train', 1), ty)
    jl.npsave(ccr_x('val', 1), vx)
    jl.npsave(ccr_y('val', 1), vy)
    jl.npsave(ccr_x('test', 1), ex)
    jl.npsave(ccr_y('test', 1), ey)
    print('Prep complete')
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


def lamem_read(name, n):
    filename = 'lamem/splits/%s_%d.txt' % (name, n)
    b = np.asarray([line.split(' ') for line in jl.readtxt(filename)])
    x = np.asarray(b[:, 0])
    y = np.asarray([float(x) for x in b[:, 1]])
    return x, y


def lamem_rel_url(url):
    a = os.path.join(os.getcwd(), 'lamem/images', url)
    return os.path.normpath(a)


def lamem_x(name, n):
    return 'lamem%d%sx' % (name, n)


def lamem_y(name, n):
    return 'lamem%d%sy' % (name, n)


def lamem_prep_txt(name, n):
    x, y = lamem_read(name, n)
    x = np.asarray([lamem_rel_url(url) for url in x])
    y = np.asarray(y)
    jl.npsave(lamem_x(name, n), x)
    jl.npsave(lamem_y(name, n), y)
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
    csv = CSVLogger('gen/training.csv', append=True)
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


def test(modelfile, test_x, test_y, custom=None):
    print('Loading test X')
    x = jl.npload(test_x)
    print('Loading test Y')
    y = jl.npload(test_y)
    print('Loading architecture')
    model = load_model(modelfile, custom_objects=custom)
    print('Testing sequence')
    seq = Sequence1(x, y, 10)
    print('Testing starts')
    results = model.evaluate_generator(generator=seq, verbose=1)
    print('Testing finished')
    if type(results) != list:
        results = [results]
    for metric, scalar in zip(model.metrics_names, results):
        print('%s: %f' % (metric, scalar))
    return


def predict(modelfile, test_x, test_y, custom=None):
    print('Loading test X')
    x = jl.npload(test_x)
    print('Loading test Y')
    y = jl.npload(test_y)
    print('Loading architecture')
    model = load_model(modelfile, custom_objects=custom)
    print('Prediction sequence')
    seq = Sequence1(x, y, 10)
    print('Prediction starts')
    results = model.predict_generator(generator=seq, verbose=1)
    print('Prediction finished')
    print(results.shape)
    print(results)
    return


# ccc_prep()
# model.ccc()
# train('gen/ccc.h5', ccc_x('train', 1), ccc_y('train', 1), ccc_x('val', 1), ccc_y('val', 1), 10000)
# test('gen/ccc.h5', ccc_x('test', 1), ccc_y('test', 1))
# predict('gen/ccc.h5', ccc_x('test', 1), ccc_y('test', 1))

# ccc_prep()
# model.ccc2()
# train('gen/ccc2.h5', ccc_x('train', 1), ccc_y('train', 1), ccc_x('val', 1), ccc_y('val', 1), 10000)
# test('gen/ccc2.h5', ccc_x('test', 1), ccc_y('test', 1))
# predict('gen/ccc2.h5', ccc_x('test', 1), ccc_y('test', 1))

# ccc_prep()
# model.ccc3()
# train('gen/ccc3.h5', ccc_x('train', 1), ccc_y('train', 1), ccc_x('val', 1), ccc_y('val', 1), 10000)
# test('gen/ccc3.h5', ccc_x('test', 1), ccc_y('test', 1))
# predict('gen/ccc3.h5', ccc_x('test', 1), ccc_y('test', 1))

# ccr_prep()
# model.ccr()
# train('gen/ccr.h5', ccr_x('train', 1), ccr_y('train', 1), ccr_x('val', 1), ccr_y('val', 1), 10000, {'rmse': model.rmse})
# test('gen/ccr.h5', ccr_x('test', 1), ccr_y('test', 1))
# predict('gen/ccr.h5', ccr_x('test', 1), ccr_y('test', 1))

# lamem_prep_all()
# model.lamem()
# train('gen/lamem.h5', lamem_x('train', 1), lamem_y('train', 1), lamem_x('val', 1), lamem_y('val', 1), 10000, {'rmse': model.rmse})
# test('gen/lamem.h5', lamem_x('test', 1), lamem_y('test', 1))
# predict('gen/lamem.h5', lamem_x('test', 1), lamem_y('test', 1))
