import os
import cv2 as cv
import numpy as np
import jl
from keras.models import load_model
import keras
from keras.callbacks import CSVLogger, ModelCheckpoint, Callback
import model


def datafile_x(dataset, phase, split):
    return '%s%d%sx' % (dataset, split, phase)


def datafile_y(dataset, phase, split):
    return '%s%d%sy' % (dataset, split, phase)


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
    jl.npsave(datafile_x('ccc', 'train', 1), tx)
    jl.npsave(datafile_y('ccc', 'train', 1), ty)
    jl.npsave(datafile_x('ccc', 'val', 1), vx)
    jl.npsave(datafile_y('ccc', 'val', 1), vy)
    jl.npsave(datafile_x('ccc', 'test', 1), ex)
    jl.npsave(datafile_y('ccc', 'test', 1), ey)
    print('Prep complete')
    return


def ccr_prep():
    print("Reading data file")
    x = jl.getcol(0)
    y = jl.getcol(1)
    y = jl.intize(y)
    print('Generating data splits')
    tx, ty, vx, vy, ex, ey = jl.train_valid_test_split(x, y, test_size=0.1, valid_size=0.1)
    print('Saving')
    jl.npsave(datafile_x('ccr', 'train', 1), tx)
    jl.npsave(datafile_y('ccr', 'train', 1), ty)
    jl.npsave(datafile_x('ccr', 'val', 1), vx)
    jl.npsave(datafile_y('ccr', 'val', 1), vy)
    jl.npsave(datafile_x('ccr', 'test', 1), ex)
    jl.npsave(datafile_y('ccr', 'test', 1), ey)
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


def lamem_prep_txt(phase, split):
    x, y = lamem_read(phase, split)
    x = np.asarray([lamem_rel_url(url) for url in x])
    y = np.asarray(y)
    jl.npsave(datafile_x('lamem', phase, split), x)
    jl.npsave(datafile_y('lamem', phase, split), y)
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


def train(model, dataset, split, initial_epoch=0, epochs=10000, custom=None):
    print('Loading training X')
    x1 = jl.npload(datafile_x(dataset, 'train', split))
    print('Loading training Y')
    y1 = jl.npload(datafile_y(dataset, 'train', split))
    print('Loading validation X')
    x2 = jl.npload(datafile_x(dataset, 'val', split))
    print('Loading validation Y')
    y2 = jl.npload(datafile_y(dataset, 'val', split))
    print('Loading architecture')
    train_name = model.filename_training(model, dataset)
    best_name = model.filename(model, dataset)
    modelx = load_model(best_name, custom_objects=custom)
    print('Training sequence')
    seq1 = Sequence1(x1, y1, 10)
    print('Validation sequence')
    seq2 = Sequence1(x2, y2, 10)
    print('Training starts')
    term = TerminateOnDemand()
    save = ModelCheckpoint(train_name, verbose=1, period=1)
    best = ModelCheckpoint(best_name, verbose=1, save_best_only=True)
    csv = CSVLogger('gen/training.csv', append=True)
    modelx.fit_generator(
        generator=seq1,
        epochs=epochs,
        verbose=1,
        validation_data=seq2,
        shuffle=False,
        initial_epoch=initial_epoch,
        callbacks=[best, save, csv, term]
    )
    print('Training finished')
    return


def test(model, dataset, split, custom=None):
    print('Loading test X')
    x = jl.npload(datafile_x(dataset, 'test', split))
    print('Loading test Y')
    y = jl.npload(datafile_y(dataset, 'test', split))
    print('Loading architecture')
    modelx = load_model(model.filename(model, dataset), custom_objects=custom)
    print('Testing sequence')
    seq = Sequence1(x, y, 10)
    print('Testing starts')
    results = modelx.evaluate_generator(generator=seq, verbose=1)
    print('Testing finished')
    if type(results) != list:
        results = [results]
    for metric, scalar in zip(modelx.metrics_names, results):
        print('%s: %f' % (metric, scalar))
    return


def predict(model, dataset, split, custom=None):
    print('Loading test X')
    x = jl.npload(datafile_x(dataset, 'test', split))
    print('Loading test Y')
    y = jl.npload(datafile_y(dataset, 'test', split))
    print('Loading architecture')
    modelx = load_model(model.filename(model, dataset), custom_objects=custom)
    print('Prediction sequence')
    seq = Sequence1(x, y, 10)
    print('Prediction starts')
    results = modelx.predict_generator(generator=seq, verbose=1)
    print('Prediction finished')
    print(results.shape)
    print(results)
    return


ccc_prep()
model.ccc()
train('vgg16', 'ccc', 1)
test('vgg16', 'ccc', 1)
predict('vgg16', 'ccc', 1)

ccc_prep()
model.ccc2()
train('vgg16a', 'ccc', 1)
test('vgg16a', 'ccc', 1)
predict('vgg16a', 'ccc', 1)

ccc_prep()
model.ccc3()
train('vgg16b', 'ccc', 1)
test('vgg16b', 'ccc', 1)
predict('vgg16b', 'ccc', 1)

ccr_prep()
model.ccr()
train('kcnn', 'ccr', 1, custom=model.custom_rmse)
test('kcnn', 'ccr', 1, custom=model.custom_rmse)
predict('kcnn', 'ccr', 1, custom=model.custom_rmse)

lamem_prep_all()
model.lamem()
train('kcnn', 'lamem', 1, custom=model.custom_rmse)
test('kcnn', 'lamem', 1, custom=model.custom_rmse)
predict('kcnn', 'lamem', 1, custom=model.custom_rmse)
