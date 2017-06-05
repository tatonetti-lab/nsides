from keras.layers import Input, Dense, Dropout
from keras.models import Model
from keras import metrics
from keras import losses
from keras.utils import np_utils
from keras import regularizers
import tensorflow as tf

from scipy import io
from scipy.sparse import vstack
import numpy as np

from operator import itemgetter

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

args.model_num = (args.model_num).split(",")
args.model_num = map(int,args.model_num)

if len(args.model_num) > 1:
    modelIdx = list(itemgetter(*args.model_num)(runIndices))
else:
    modelIdx = [itemgetter(*args.model_num)(runIndices)]

save_string = ''
for model in modelIdx:
    save_string = save_string + '_' + str(model)


def comb_loss(y_true, y_pred):
    return losses.mean_squared_error(y_true, y_pred) + losses.categorical_crossentropy(y_true, y_pred)
#2764 -> 2863

def generate_arrays(batchsize):
    pos_reports = io.mmread('model'+save_string+'_0_posreports.mtx')
    pos_reports = pos_reports.tocsr()
    
    neg_reports = io.mmread('model'+save_string+'_0_negreports.mtx')
    neg_reports = neg_reports.tocsr()
    
    for reportblock in range(1,50):
        print "Procesing",reportblock
        thispos = io.mmread('model'+save_string+'_'+str(reportblock)+'_posreports.mtx')
        thispos = thispos.tocsr()
        pos_reports = vstack((pos_reports,thispos))
    
        thisneg = io.mmread('model'+save_string+'_'+str(reportblock)+'_negreports.mtx')
        thisneg = thisneg.tocsr()
        neg_reports = vstack((neg_reports,thisneg))



    neg_ind = np.arange(neg_reports.shape[0])

    subset_neg_ind = np.random.choice(neg_ind, pos_reports.shape[0], replace=False)
    neg_reports_subset = neg_reports[subset_neg_ind,:]
    
    all_reports = vstack([pos_reports,neg_reports_subset])

    outcomes = np.concatenate((np.ones(pos_reports.shape[0],np.bool),
                               np.zeros(neg_reports_subset.shape[0],np.bool)))

    del pos_reports
    del neg_reports
    del neg_reports_subset

    new_ind = np.random.permutation(all_reports.shape[0])
    all_reports = all_reports[new_ind,]
    outcomes = outcomes[new_ind]
    outcomes_cat = np_utils.to_categorical(outcomes,2)

    numbatches = np.ceil(float(all_reports.shape[0])/float(batchsize))

    while 1:
        for rownum in np.arange(numbatches):
        #for rownum in np.arange(all_reports.shape[0]):
            start_point = int(rownum*batchsize)
            end_point = int((rownum+1)*batchsize)
            if (end_point > all_reports.shape[0]):
                end_point = all_reports.shape[0]
            #print np.reshape(outcomes_cat[start_point:end_point,],(end_point-start_point,2))
            #yield (all_reports[start_point:end_point,].todense(), np.reshape(outcomes_cat[start_point:end_point,],(end_point-start_point,2)))
            yield (all_reports[start_point:end_point,].todense(), np.reshape(outcomes_cat[start_point:end_point,],(batchsize,2)))



if args.run_on_cpu:
    with tf.device("/cpu:0"):
        for i in range(0,20):

            encoding_dim = 2
            n_hidden_1 = 200
            n_hidden_2 = 50

            pos_reports = io.mmread('model'+save_string+'_0_posreports.mtx')

            input_data = Input(shape=(pos_reports.shape[1],))
            #encoded_1 = Dense(n_hidden_1, activation='relu', activity_regularizer=regularizers.l1(1e-4), use_bias=False)(input_data)
            encoded_1 = Dense(n_hidden_1, activation='relu', use_bias=False)(input_data)
            #encoded_DO = Dropout(0.5)(encoded_1)
            encoded_2 = Dense(n_hidden_2, activation='relu', use_bias=False)(encoded_1)
            #encoded_DO_2 = Dropout(0.5)(encoded_2)
            encoded_3 = Dense(encoding_dim, activation='relu', use_bias=False)(encoded_2)
            encoded_out = Dense(2, activation='softmax', use_bias=False)(encoded_3)

            autoencoder = Model(input=input_data, output=encoded_out)
            encoder = Model(input=input_data, output=encoded_3)

            autoencoder.compile(optimizer='adam', loss=comb_loss, metrics=[metrics.categorical_crossentropy,
                                                                           metrics.mean_squared_error,
                                                                           'accuracy'])
            batchsize = 1
            
            autoencoder.fit_generator(generate_arrays(batchsize), steps_per_epoch=int(pos_reports.shape[0]*2/batchsize))

            #X = np.load("model_"+model_num+"_reports.npy")

            X = io.mmread("model"+save_string+"_0_reports.mtx")
            X = X.tocsr()
            for reportblock in range(1,50):
                thisreport = io.mmread("model"+save_string+"_"+str(reportblock)+"_reports.mtx")
                thisreport = thisreport.tocsr()
                X = vstack([X,thisreport])
            
            numsteps = X.shape[0]

            batchsize=50000
            numsteps = np.ceil(float(numsteps)/float(batchsize))

            predictions = autoencoder.predict(X[0:batchsize].todense(), verbose=1)

            for rownum in np.arange(1,numsteps):
                print "Processing",int(rownum),"out of",int(numsteps-1)
                start_point = int(rownum*batchsize)
                end_point = int((rownum+1)*batchsize)
                #print start_point,":",end_point
                if (end_point > X.shape[0]):
                    end_point = X.shape[0]
                thesepredictions = autoencoder.predict(X[start_point:end_point].todense(), verbose=0)
                predictions = np.concatenate((predictions, thesepredictions))
                #print "pred shape:",predictions.shape
                del thesepredictions

            np.save("scores_dnn"+save_string+"_"+str(i+1)+".npy",predictions[:,1])

            del predictions

else:
    for i in range(0,20):

        encoding_dim = 2
        n_hidden_1 = 200
        n_hidden_2 = 50

        pos_reports = io.mmread('model'+save_string+'_0_posreports.mtx')

        input_data = Input(shape=(pos_reports.shape[1],))
        #encoded_1 = Dense(n_hidden_1, activation='relu', activity_regularizer=regularizers.l1(1e-4), use_bias=False)(input_data)
        encoded_1 = Dense(n_hidden_1, activation='relu', use_bias=False)(input_data)
        #encoded_DO = Dropout(0.5)(encoded_1)
        encoded_2 = Dense(n_hidden_2, activation='relu', use_bias=False)(encoded_1)
        #encoded_DO_2 = Dropout(0.5)(encoded_2)
        encoded_3 = Dense(encoding_dim, activation='relu', use_bias=False)(encoded_2)
        encoded_out = Dense(2, activation='softmax', use_bias=False)(encoded_3)

        autoencoder = Model(input=input_data, output=encoded_out)
        encoder = Model(input=input_data, output=encoded_3)

        autoencoder.compile(optimizer='adam', loss=comb_loss, metrics=[metrics.categorical_crossentropy,
                                                                       metrics.mean_squared_error,
                                                                       'accuracy'])
        batchsize = 1
        
        autoencoder.fit_generator(generate_arrays(batchsize), steps_per_epoch=int(pos_reports.shape[0]*2/batchsize))

        #X = np.load("model_"+model_num+"_reports.npy")

        X = io.mmread("model"+save_string+"_0_reports.mtx")
        X = X.tocsr()
        for reportblock in range(1,50):
            thisreport = io.mmread("model"+save_string+"_"+str(reportblock)+"_reports.mtx")
            thisreport = thisreport.tocsr()
            X = vstack([X,thisreport])
        
        numsteps = X.shape[0]

        batchsize=50000
        numsteps = np.ceil(float(numsteps)/float(batchsize))

        predictions = autoencoder.predict(X[0:batchsize].todense(), verbose=1)

        for rownum in np.arange(1,numsteps):
            print "Processing",int(rownum),"out of",int(numsteps-1)
            start_point = int(rownum*batchsize)
            end_point = int((rownum+1)*batchsize)
            #print start_point,":",end_point
            if (end_point > X.shape[0]):
                end_point = X.shape[0]
            thesepredictions = autoencoder.predict(X[start_point:end_point].todense(), verbose=0)
            predictions = np.concatenate((predictions, thesepredictions))
            #print "pred shape:",predictions.shape
            del thesepredictions

        np.save("scores_dnn"+save_string+"_"+str(i+1)+".npy",predictions[:,1])

        del predictions
