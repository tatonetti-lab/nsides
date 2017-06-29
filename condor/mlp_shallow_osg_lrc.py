import time
import json

from scipy import io
from scipy.sparse import vstack
from sklearn import metrics as metrics_skl
import numpy as np

#from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegressionCV

from operator import itemgetter

import argparse
parser = argparse.ArgumentParser(description='Keras MLP model for DDI PSM.')
parser.add_argument('--suffix',
                    help='Filename suffix',
                    action='store',
                    dest='suffix',
                    default=1)
args = parser.parse_args()

args.suffix = str(args.suffix)

def comb_loss(y_true, y_pred):
    return losses.mean_squared_error(y_true, y_pred) + losses.categorical_crossentropy(y_true, y_pred)
#2764 -> 2863
#pos_reports = io.mmread('modelCSR_'+model_num+'_posreports.mtx')
#neg_reports = io.mmread('modelCSR_'+model_num+'_negreports.mtx')
#
#pos_reports = pos_reports.tocsr()
#neg_reports = neg_reports.tocsr()

pos_reports = io.mmread('model_0_posreports.mtx')
pos_reports = pos_reports.tocsr()

neg_reports = io.mmread('model_0_negreports.mtx')
neg_reports = neg_reports.tocsr()

for reportblock in range(1,50):
    print "Procesing",reportblock
    thispos = io.mmread('model_'+str(reportblock)+'_posreports.mtx')
    thispos = thispos.tocsr()
    pos_reports = vstack((pos_reports,thispos))

    thisneg = io.mmread('model_'+str(reportblock)+'_negreports.mtx')
    thisneg = thisneg.tocsr()
    neg_reports = vstack((neg_reports,thisneg))

neg_ind = np.arange(neg_reports.shape[0])

log = dict()

for i in range(0,1):
        
    subset_neg_ind = np.random.choice(neg_ind, pos_reports.shape[0], replace=False)
    neg_reports_subset = neg_reports[subset_neg_ind,:]

    all_reports = vstack([pos_reports,neg_reports_subset]).toarray()
    outcomes = np.concatenate((np.ones(pos_reports.shape[0], np.bool),
                               np.zeros(neg_reports_subset.shape[0], np.bool)))

    del neg_reports_subset

    new_ind = np.random.permutation(all_reports.shape[0])
    all_reports = all_reports[new_ind,]
    outcomes = outcomes[new_ind]

    print "Neg reports:", len(np.where(outcomes == 0)[0])
    print "Pos reports:", len(np.where(outcomes == 1)[0])

#    bdt = AdaBoostClassifier()
#    rfc = RandomForestClassifier()
    lrc = LogisticRegressionCV(penalty='l1',solver='liblinear')
    
#    print ("Fitting Adaboost")
#    start = time.time()
#    bdt.fit(all_reports, outcomes)
#    end = time.time()
#    print("TIME TO TRAIN ADABOOST CLASSIFIER: {0}s".format(end - start))
    
#    print ("Fitting Random Forest")
#    start = time.time()
#    rfc.fit(all_reports, outcomes)
#    end = time.time()
#    print("TIME TO TRAIN RANDOM FOREST CLASSIFIER: {0}s".format(end - start))
    
    print ("Fitting Logistic Regression")
    start = time.time()
    lrc.fit(all_reports, outcomes)
    end = time.time()
    print("TIME TO TRAIN LOGISTIC REGRESSION CLASSIFIER: {0}s".format(end - start))
    

    
    #X = np.load("model_"+model_num+"_reports.npy")
    #X = io.mmread("model_"+model_num+"_reports.mtx")
    X = io.mmread("model_0_reports.mtx")
    X = X.tocsr()
    for reportblock in range(1,50):
        thisreport = io.mmread("model_"+str(reportblock)+"_reports.mtx")
        thisreport = thisreport.tocsr()
        X = vstack([X,thisreport])

    
    X = X.tocsr()
    y = np.load("model_outcomes.npy")

#    predictions = bdt.predict(all_reports)
#    skl_acc = metrics_skl.accuracy_score(outcomes,predictions)
#    print("ADABOOST  INFO: ACC = {0}".format(skl_acc))
#    if (skl_acc > 0.80):
#        predictions = bdt.predict_proba(X)
#        np.save("scores_bdt_"+str(i+1)+"_"+args.suffix+".npy",predictions[:,1])
#        auc = metrics_skl.roc_auc_score(y, predictions[:,1])
#        print("ADABOOST  INFO: AUC = {0}".format(auc))
#        log['tf_adaboost_cpu'] = {'auc': auc}
#    else:
#        print ("ACCURACY BELOW 80%, NOT SAVING SCORES")
#
#    predictions = rfc.predict(all_reports)
#    skl_acc = metrics_skl.accuracy_score(outcomes,predictions)
#    print("RANDOM FOREST  INFO: ACC = {0}".format(skl_acc))
#    if (skl_acc > 0.80):
#        predictions = rfc.predict_proba(X)
#        np.save("scores_rfc_"+str(i+1)+"_"+args.suffix+".npy",predictions[:,1])
#        auc = metrics_skl.roc_auc_score(y, predictions[:,1])
#        print("RANDOM FOREST  INFO: AUC = {0}".format(auc))
#        log['tf_rfc_cpu'] = {'auc': auc}
#    else:
#        print ("ACCURACY BELOW 80%, NOT SAVING SCORES")

    predictions = lrc.predict(all_reports)
    skl_acc = metrics_skl.accuracy_score(outcomes,predictions)
    print("LOGISTIC REGRESSION  INFO: ACC = {0}".format(skl_acc))
    if (skl_acc > 0.80):
        predictions = lrc.predict_proba(X)
        np.save("scores_lrc_"+str(i+1)+"_"+args.suffix+".npy",predictions[:,1])
        auc = metrics_skl.roc_auc_score(y, predictions[:,1])
        print("LOGISTIC REGRESSION  INFO: AUC = {0}".format(auc))
        log['tf_lrc_cpu'] = {'auc': auc}
    else:
        print ("ACCURACY BELOW 80%, NOT SAVING SCORES")


    del all_reports
    del outcomes
    del predictions
    del X
    del y
    
    logfname = "results{0}.json".format(int(time.time()))
    with open(logfname, 'w') as f:
        f.write(json.dumps(log))
        
