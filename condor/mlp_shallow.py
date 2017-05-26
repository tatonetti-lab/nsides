import time
import json

from keras.layers import Input, Dense, Dropout
from keras.models import Model, Sequential
from keras import metrics
from keras import losses
from keras.utils import np_utils
from keras import regularizers
from keras.callbacks import EarlyStopping
import tensorflow as tf

from scipy import io
from scipy.sparse import vstack
from sklearn import metrics as metrics_skl
import numpy as np

from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV

import argparse
parser = argparse.ArgumentParser(description='Keras MLP model for DDI PSM.')
parser.add_argument('--model-number',
                    help='Numerical ID of the drug against which to fit the model',
                    action='store',
                    dest='model_num',
                    default=0)
parser.add_argument('--run-on-cpu',
                    help='If true, run MLP model on CPU instead of GPU',
                    action='store_true',
                    default=False,
                    dest='run_on_cpu')
parser.add_argument('--run-comparisons',
                    help='Boolean flag: do or do not run 3 shallow classifiers',
                    action='store_true',
                    default=False,
                    dest='compare')
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

def comb_loss(y_true, y_pred):
    return losses.mean_squared_error(y_true, y_pred) + losses.categorical_crossentropy(y_true, y_pred)
#2764 -> 2863
pos_reports = io.mmread('modelCSR_'+model_num+'_posreports.mtx')
neg_reports = io.mmread('modelCSR_'+model_num+'_negreports.mtx')

pos_reports = pos_reports.tocsr()
neg_reports = neg_reports.tocsr()

runTimes = 0

neg_ind = np.arange(neg_reports.shape[0])

log = dict()

runTimes = 0

for i in range(0,20):
    
    
    print("  INFO: RUNNING TENSORFLOW WITH GPU")
    print("  INFO: Constructing logistic regression model")
    # Dense(64) is a fully-connected layer with 64 hidden units.
    # in the first layer, you must specify the expected input data shape (k)

    multFac = float(neg_reports.shape[0])/float(pos_reports.shape[0])
    if runTimes > multFac:
        continue
    else:
        runTimes = runTimes + 1

    print "multFac:",multFac

    #neg_reports_subset = neg_reports[((runTimes - 1)*pos_reports.shape[0]):(runTimes*pos_reports.shape[0]),:]

    subset_neg_ind = np.random.choice(neg_ind, pos_reports.shape[0], replace=False)
    neg_reports_subset = neg_reports[subset_neg_ind,:]

    #print "Picking from ",len(neg_ind)

    #neg_ind = [x for x in neg_ind if x not in subset_neg_ind]

    #print "Now there are ",len(neg_ind)

    all_reports = vstack([pos_reports,neg_reports_subset]).toarray()
    outcomes = np.concatenate((np.ones(pos_reports.shape[0], np.bool),
                               np.zeros(neg_reports_subset.shape[0], np.bool)))

    new_ind = np.random.permutation(all_reports.shape[0])
    all_reports = all_reports[new_ind,]
    outcomes = outcomes[new_ind]
    outcomes_cat = np_utils.to_categorical(outcomes, 2)

    print "Neg reports:", len(np.where(outcomes == 0)[0])
    print "Pos reports:", len(np.where(outcomes == 1)[0])
    early_stopping = EarlyStopping(monitor='val_loss', patience=10)
    if args.run_on_cpu==True:
        with tf.device("/cpu:0"):
            print("  INFO: RUNNING TENSORFLOW WITHOUT GPU")
            print("  INFO: Fitting MLP model to training data")
            model = Sequential()
            model.add(Dense(output_dim=2,
                            input_dim=pos_reports.shape[1],
                            activation='softmax',
                            kernel_regularizer=regularizers.l1(1.0)))
            model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy','categorical_crossentropy'])
            model.fit(all_reports,
              outcomes_cat, 
              epochs=500,
              batch_size=1000,
              shuffle=True,
              callbacks=[early_stopping],
              validation_split=0.2)

            model_metrics = model.evaluate(all_reports,outcomes_cat)
            print ("\n model metrics:",model_metrics)
    else:
        print("  INFO: RUNNING TENSORFLOW WITH GPU")
        print("  INFO: Fitting MLP model to training data")
        model = Sequential()
        model.add(Dense(output_dim=2,
                        input_dim=pos_reports.shape[1],
                        activation='softmax',
                        kernel_regularizer=regularizers.l1(0.1)))
        model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy','categorical_crossentropy'])
        model.fit(all_reports,
          outcomes_cat, 
          epochs=500,
          batch_size=100000,
          shuffle=True,
          callbacks=[early_stopping],
          validation_split=0.2)

        model_metrics = model.evaluate(all_reports,outcomes_cat)
        print ("\n model metrics:",model_metrics)


    X = np.load("model_"+model_num+"_reports.npy")
    #X = io.mmread("model_"+model_num+"_reports.mtx")
    #X = X.tocsr()
    y = np.load("model_"+model_num+"_outcomes.npy")

    predictions = model.predict(X)

    np.save("scores_tflr_"+model_num+"_"+str(runTimes)+".npy",predictions[:,1])

    print("  INFO: Evaluating accuracy on test set")
    print ("\n")
    auc = metrics_skl.roc_auc_score(y, predictions[:,1])
    print("  INFO: AUC = {0}".format(auc))
    log['tf_lr_cpu'] = {'auc': auc}


    del predictions
    del X
    del y
    del neg_reports_subset

    bdt = AdaBoostClassifier()
    rfc = RandomForestClassifier()
    lrc = LogisticRegressionCV(penalty='l1',solver='liblinear')
    
    print ("Fitting Adaboost")
    start = time.time()
    bdt.fit(all_reports, outcomes)
    end = time.time()
    print("TIME TO TRAIN ADABOOST CLASSIFIER: {0}s".format(end - start))
    
    print ("Fitting Random Forest")
    start = time.time()
    rfc.fit(all_reports, outcomes)
    end = time.time()
    print("TIME TO TRAIN RANDOM FOREST CLASSIFIER: {0}s".format(end - start))
    
    print ("Fitting Logistic Regression")
    start = time.time()
    lrc.fit(all_reports, outcomes)
    end = time.time()
    print("TIME TO TRAIN LOGISTIC REGRESSION CLASSIFIER: {0}s".format(end - start))
    

    
    #X = np.load("model_"+model_num+"_reports.npy")
    X = io.mmread("model_"+model_num+"_reports.mtx")
    X = X.tocsr()
    y = np.load("model_"+model_num+"_outcomes.npy")
 
    predictions = bdt.predict(all_reports)
    skl_acc = metrics_skl.accuracy_score(outcomes,predictions)
    print("ADABOOST  INFO: ACC = {0}".format(skl_acc))
    if (skl_acc > 0.80):
        predictions = bdt.predict_proba(X)
        np.save("scores_bdt_"+model_num+"_"+str(runTimes)+".npy",predictions[:,1])
    auc = metrics_skl.roc_auc_score(y, predictions[:,1])
    print("ADABOOST  INFO: AUC = {0}".format(auc))
    log['tf_adaboost_cpu'] = {'auc': auc}

    predictions = rfc.predict(all_reports)
    skl_acc = metrics_skl.accuracy_score(outcomes,predictions)
    print("RANDOM FOREST  INFO: ACC = {0}".format(skl_acc))
    if (skl_acc > 0.80):
        predictions = rfc.predict_proba(X)
        np.save("scores_rfc_"+model_num+"_"+str(runTimes)+".npy",predictions[:,1])
    auc = metrics_skl.roc_auc_score(y, predictions[:,1])
    print("RANDOM FOREST  INFO: AUC = {0}".format(auc))
    log['tf_rfc_cpu'] = {'auc': auc}

    predictions = lrc.predict(all_reports)
    skl_acc = metrics_skl.accuracy_score(outcomes,predictions)
    print("LOGISTIC REGRESSION  INFO: ACC = {0}".format(skl_acc))
    if (skl_acc > 0.80):
        predictions = lrc.predict_proba(X)
        np.save("scores_lrc_"+model_num+"_"+str(runTimes)+".npy",predictions[:,1])
    auc = metrics_skl.roc_auc_score(y, predictions[:,1])
    print("LOGISTIC REGRESSION  INFO: AUC = {0}".format(auc))
    log['tf_lrc_cpu'] = {'auc': auc}


    del all_reports
    del neg_reports_subset
    del outcomes
    del outcomes_cat
    del predictions
    del X
    del y
    
    logfname = "results_{0}_{1}.json".format(model_num, int(time.time()))
    with open(logfname, 'w') as f:
        f.write(json.dumps(log))
        
