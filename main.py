import url2
import os
import cv2
import classifier
import rater
import analyzer
import numpy as np
import jl
from keras.models import load_model
from keras.applications.vgg16 import VGG16
from sklearn.model_selection import train_test_split


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


def src_url():
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


def dst_url():
    """
    Load raw URLs.
    Convert to resized URLS.
    Write to file.
    """
    a = jl.readtxt(jl.TEXT_URL_RAW)
    b = list(map(jl.absurl2, a))
    jl.writetxt(jl.TEXT_URL_PROCESSED, b)
    return


def classesonehot():
    """
    Load classes. String integers.
    Change to int type.
    Change to one hot type.
    Save to file.
    """
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
    res = (jl.w, jl.h)
    for src, dst in zip(urls1, urls2):
        print(src)
        print(dst)
        img = cv2.imread(src, cv2.IMREAD_COLOR)
        print(img.shape)
        img2 = cv2.resize(img, res, interpolation=cv2.INTER_CUBIC)
        print(img2.shape)
        jl.mkdirs(dst)
        cv2.imwrite(dst, img2)
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
    train()
    predict()
    analyzer.main()
    return


def rater_filter():
    a = []
    rate = jl.npload(jl.NPY_RATE)
    for i in rate:
        if i == 1 or i == 3:
            a.append(True)
        else:
            a.append(False)
    b = jl.npload(jl.NPY_PHOTOS)[a]
    c = rate[a]
    jl.npsave(jl.NPY_PHOTOS, b)
    jl.npsave(jl.NPY_RATE, c)
    return


def lamem_read(txt):
    c = 'lamem/splits/%s.txt' % (txt)
    a = jl.readtxt(c)
    for i, v in enumerate(a):
        a[i] = v.split(' ')
    b = np.asarray(a)
    return b


def lamem_src_url(url):
    a = os.path.join(os.getcwd(), 'lamem/images', url)
    return os.path.normpath(a)


def lamem_dst_url(url):
    a = os.path.join(os.getcwd(), 'resize/lamem', url)
    return os.path.normpath(a)


def lamem_urls(urls, name):
    src = list(map(lamem_src_url, urls))
    dst = list(map(lamem_dst_url, urls))
    return src, dst


def lamem_prep():
    train1 = 'train_1'
    a = lamem_read(train1)
    # src, dst = lamem_urls(a[:, 0], train1)
    # for i in range(0, 15):
    #     jl.writetxt('gen/%s_%d_src.txt' % (train1, i), src[i*3000:(i+1)*3000])
    #     jl.writetxt('gen/%s_%d_dst.txt' % (train1, i), dst[i*3000:(i+1)*3000])
    rates = a[:, 1]
    rates = jl.floatize(rates)
    for i in range(15):
        jl.npsave('%s_%d_rates' % (train1, i), rates[i*3000:(i+1)*3000])
    # for i in range(0, 15):
    #     jl.writetxt('gen/%s_%d_src.txt' % (train1, i), src[i*3000:(i+1)*3000])
    # resize_imgs('gen/train1src.txt', 'gen/train1dst.txt')
    # for i in range(14, 15):
    #     d = jl.readtxt('gen/%s_%d_dst.txt' % (train1, i))
    #     b = jl.readimg(d)
    #     jl.npsave('%s_%d' % (train1, i), b)
    return


def rater_prep():
    rateurl()
    rate_create_img_npy()
    rate_create_rate_npy()
    rater_filter()
    return


def trainrater():
    x = jl.npload(jl.NPY_PHOTOS)
    y = jl.npload(jl.NPY_RATE)
    datax, testx, datay, testy = train_test_split(x, y, test_size=0.1, shuffle=True)
    for cross in range(10):
        rater.main()
        print("cross %d" % (cross))
        trainx, validx, trainy, validy = train_test_split(datax, datay, test_size=0.1, shuffle=True)
        model = load_model(jl.H5_RATER, custom_objects={'rmse': rater.rmse})
        h = model.fit(
            trainx,
            trainy,
            validation_data=(validx, validy),
            shuffle=True,
            epochs=100,
            batch_size=15
        ).history
        test_loss = model.evaluate(testx, testy, batch_size=15)[0]
        print(test_loss)
        with open('gen/loss.txt', 'a') as f:
            print("================cross #%d================" % (cross), file=f)
            for i, (t, v) in enumerate(zip(h['loss'], h['val_loss'])):
                print("%d %f %f" % (i, t, v), file=f)
            print(test_loss, file=f)
    model.save(jl.H5_RATER)
    return


model = load_model(jl.H5_RATER, custom_objects={'rmse': rater.rmse})


def trainrater2(zxc):
    x_file = '%s_%d' % ('train_1', zxc)
    y_file = '%s_%d_rates' % ('train_1', zxc)
    print(zxc)
    x = jl.npload(x_file)
    print('x')
    y = jl.npload(y_file)
    print('y')
    model.fit(
        x,
        y,
        verbose=2,
        # validation_data=(validx, validy),
        shuffle=True,
        epochs=1,
        batch_size=15
    )
    model.save(jl.H5_RATER)
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


def wtfh():
    y = jl.npload(jl.NPY_RATE)
    q = [0, 0, 0, 0]
    for i in y:
        q[i] = q[i]+1
    print(q)
    return


# main()
# rater.main()
# classifier.main()
# lamem_prep()
# rater_prep()
# trainrater()
for j in range(2):
    for i in range(13):
        trainrater2(i)
# rater_valid()
# rater_test()
# rater_predict()
# wtfh()
