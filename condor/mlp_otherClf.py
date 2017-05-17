from __future__ import division, print_function

import argparse
import pdb
import sys
import tqdm
import time
import json

import numpy as np
from scipy import stats, sparse

from keras.models import Sequential 
from keras.layers import Dense, Activation,Dropout
from keras.utils import np_utils
from keras.regularizers import l1
from keras.callbacks import EarlyStopping
import tensorflow as tf  # for specifying device context

from sklearn import metrics, svm
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib


def info(infostr):
    if args.verbose:
        print(infostr)


parser = argparse.ArgumentParser(description='Keras MLP model for DDI PSM.')
parser.add_argument('--model-number',
                    help='Numerical ID of the drug against which to fit the model',
                    action='store',
                    dest='model_num',
                    default=2451)
parser.add_argument('--batch-size', 
                    help='Number of reports per training batch', 
                    action='store', 
                    dest='batch_size', 
                    default=100)
parser.add_argument('--learning-rate', 
                    help='Optimization algorithm step size', 
                    action='store', 
                    dest='lr', 
                    default=0.01)
parser.add_argument('--n-hidden-nodes', 
                    help='Number of nodes in the neural network\'s hidden layer', 
                    action='store', 
                    dest='n_hidden', 
                    default=50)
parser.add_argument('--pos-report-ratio', 
                    help='Ratio of positive to negative reports in training set', 
                    action='store',
                    dest='pos_report_ratio', 
                    default=100)
parser.add_argument('-v', 
                    help='Enable verbose message output', 
                    action='store_true', 
                    default=False, 
                    dest='verbose')
parser.add_argument('--run-comparisons',
                    help='Boolean flag: do or do not run 3 shallow classifiers',
                    action='store_true',
                    default=False,
                    dest='compare')
parser.add_argument('--n-epochs',
                    help="Pass over entire data set N times to train",
                    action='store',
                    default=100,
                    dest='nb_epochs')
args = parser.parse_args()

runIndices = [
    2451,2465,2571,2512,2200,2431,2596,2875,2889,2912,2882,1931,2973,2975,
    2977,2983,2984,2996,3015,2960,2231,2922,2934,1955,2985,3014,2928,2916,
    2865,2859,2094,1960,2897,2904,2932,2071,3020,3023,2926,1864,2858,2860,
    2237,2950,1898,1966,2048,1876,2001,1971,2066,1793,1845,1724,1804,1745,
    1738,1770,1692,1782,2854,2955,3017,2890,2850,2780,2793,2731,2773,1714,
    1844,1697,1709,1775,1760,1786,1809,1815,1831,1799,1816,1766,1947,1801,
    3266,1995,2219,2114,2156,1896,2154,2296,2259,2373,2374,2324,2359,2291,
    2305,2283,2400,2357,2372,2311,2270,2278,2286,2304,2011,2266,2361,2391,
    2405,2276,1825,2207,1848,3910,1740,1837,1853,1703,1783,2524,2518,2492,
    2548,2552,2437,2527,1962,2031,2753,2342,2157,2723,2789,2790,1871,2804,
    2803,2811,2788,2835,2717,2238,2236,3180,3669,4215
]

model_num = str(runIndices[int(args.model_num)])

info("  INFO: Loading dataset")
X = np.load("model_{0}_reports.npy".format(model_num))
y = np.load("model_{0}_outcomes.npy".format(model_num))
k = X.shape[1]


info("  INFO: Splitting data")
test_size = int(y.shape[0] * 0.002)
test_neg_ind = np.random.choice(np.where(y[:,0] == 1)[0], size=(int(test_size * 0.5)))
test_pos_ind = np.random.choice(np.where(y[:,0] == 0)[0], size=(int(test_size * 0.5)))
all_test_inds = np.concatenate((test_neg_ind, test_pos_ind))
np.random.shuffle(all_test_inds)
mask = np.ones(X.shape[0], np.bool)
mask[all_test_inds] = 0
y_test = y[all_test_inds]
X_test = X[all_test_inds]
y_train = y[mask,:]
X_train = X[mask,:]
del(X)
del(y)
del(test_neg_ind)
del(test_pos_ind)
del(all_test_inds)
log = dict()


#LOGISTIC REGRESSION IN KERAS
def run_lr(gpu=True):
    start = time.time()
    if (gpu==False):
        with tf.device("/cpu:0"):
            print("  INFO: RUNNING TENSORFLOW WITHOUT GPU")
            info("  INFO: Constructing logistic regression model")
            model = Sequential()
            # Dense(64) is a fully-connected layer with 64 hidden units.
            # in the first layer, you must specify the expected input data shape (k)
            model.add(Dense(output_dim=y_train.shape[1], input_dim=k, activation='softmax'))
            model.compile(loss='categorical_crossentropy',
                          optimizer='adam',
                          metrics=['accuracy','categorical_crossentropy'])
            early_stopping = EarlyStopping(monitor='val_loss', patience=6)
            info("  INFO: Fitting MLP model to training data")
            model.fit(X_train, 
                      y_train, 
                      epochs=args.nb_epochs,
                      batch_size=args.batch_size, 
                      validation_split=0.5, 
                      callbacks=[early_stopping])
            info("  INFO: Evaluating accuracy on test set")
            predict_mlp_keras = model.predict_proba(X_test)
            print ("\n")
            auc = metrics.roc_auc_score(np.argmax(y_test, axis=1), predict_mlp_keras[:,1])
            acc = model.evaluate(X_test, y_test, batch_size=args.batch_size)[1]
            info("  INFO: AUC = {0}".format(auc))
            log['tf_lr_cpu'] = {'auc': auc, 
                             'acc': acc}
    else:
        print("  INFO: RUNNING TENSORFLOW WITH GPU ACCELERATION")
        info("  INFO: Constructing logistic regression model")
        model = Sequential()
        # Dense(64) is a fully-connected layer with 64 hidden units.
        # in the first layer, you must specify the expected input data shape (k)
        model.add(Dense(output_dim=y_train.shape[1], input_dim=k, activation='softmax'))
        model.compile(loss='categorical_crossentropy',
                      optimizer='adam',
                      metrics=['accuracy','categorical_crossentropy'])
        early_stopping = EarlyStopping(monitor='val_loss', patience=6)
        info("  INFO: Fitting MLP model to training data")
        model.fit(X_train, 
                  y_train, 
                  epochs=args.nb_epochs,
                  batch_size=args.batch_size, 
                  validation_split=0.5, 
                  callbacks=[early_stopping])
        info("  INFO: Evaluating accuracy on test set")
        predict_mlp_keras = model.predict_proba(X_test)
        print ("\n")
        auc =  metrics.roc_auc_score(np.argmax(y_test, axis=1), predict_mlp_keras[:,1])
        info("  INFO: AUC = {0}".format(auc))
        acc = model.evaluate(X_test, y_test, batch_size=args.batch_size)[1]
        log['tf_lr_gpu'] = {'auc': auc, 
                         'acc': acc}
    end = time.time()
    print("  INFO: TIME TO TRAIN RNN: {0}s".format(end - start))

run_lr(gpu=False)
run_lr(gpu=True)

if args.compare:
    y_train_sklearn = np.argmax(y_train, axis=1)
    y_test_sklearn = np.argmax(y_test, axis=1)

    #######################
    # ADABOOST CLASSIFIER #
    #######################
    if args.verbose:
        print("Fitting AdaBoost classifier")
    start = time.time()
    bdt = AdaBoostClassifier()
    bdt.fit(X_train, y_train_sklearn)
    pred = bdt.predict(X_test)
    acc = metrics.accuracy_score(y_test_sklearn, pred)
    auc = metrics.roc_auc_score(y_test_sklearn, pred)
    print("  ACCURACY: {0}".format(acc))
    print("  AUROC:    {0}".format(auc))
    log['adaboost'] = {'auc': auc, 
                     'acc': acc}
    joblib.dump(bdt, "adaboost_fit_{0}.pkl".format(model_num))
    end = time.time()
    print("TIME TO TRAIN ADABOOST CLASSIFIER: {0}s".format(end - start))

    ############################
    # RANDOM FOREST CLASSIFIER #
    ############################
    if args.verbose:
        print("Fitting random forest classifier")
    start = time.time()
    rfc = RandomForestClassifier()
    rfc.fit(X_train, y_train_sklearn)
    pred = rfc.predict(X_test)
    acc = metrics.accuracy_score(y_test_sklearn, pred)
    auc = metrics.roc_auc_score(y_test_sklearn, pred)
    print("  ACCURACY: {0}".format(acc))
    print("  AUROC:    {0}".format(auc))
    log['rf'] = {'auc': auc, 
                 'acc': acc}
    joblib.dump(rfc, "randomforest_fit_{0}.pkl".format(model_num))
    end = time.time()
    print("TIME TO TRAIN ADABOOST CLASSIFIER: {0}s".format(end - start))


logfname = "results_{0}_{1}.json".format(model_num, int(time.time()))
with open(logfname, 'w') as f:
    f.write(json.dumps(log))
