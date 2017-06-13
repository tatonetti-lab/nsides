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
parser.add_argument('--suffix',
                    help='Filename suffix',
                    action='store',
                    dest='suffix',
                    default=1)
parser.add_argument('--run-on-cpu',
                    help='If true, run MLP model on CPU instead of GPU',
                    action='store_true',
                    default=False,
                    dest='run_on_cpu')
args = parser.parse_args()


args.suffix = str(args.suffix)


def comb_loss(y_true, y_pred):
    return losses.mean_squared_error(y_true, y_pred) + losses.categorical_crossentropy(y_true, y_pred)
#2764 -> 2863

def generate_arrays(batchsize):
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

    print "NUMBER OF POSITIVE REPORTS:",pos_reports.shape[0]

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
        for i in range(0,1):

            encoding_dim = 2
            n_hidden_1 = 200
            n_hidden_2 = 50

            pos_reports = io.mmread('model_0_posreports.mtx')

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
            
            autoencoder.fit_generator(generate_arrays(batchsize), steps_per_epoch=int(pos_reports.shape[0]*2/batchsize), epochs=10)

            #X = np.load("model_"+model_num+"_reports.npy")

            X = io.mmread("model_0_reports.mtx")
            X = X.tocsr()
            for reportblock in range(1,50):
                thisreport = io.mmread("model_"+str(reportblock)+"_reports.mtx")
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

            np.save("scores_dnn_"+str(i+1)+"_"+args.suffix+".npy",predictions[:,1])

            del predictions

else:
    for i in range(0,1):

        encoding_dim = 2
        n_hidden_1 = 200
        n_hidden_2 = 50

        pos_reports = io.mmread('model_0_posreports.mtx')

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
        
        autoencoder.fit_generator(generate_arrays(batchsize), steps_per_epoch=int(pos_reports.shape[0]*2/batchsize), epochs=10)

        #X = np.load("model_"+model_num+"_reports.npy")

        X = io.mmread("model_0_reports.mtx")
        X = X.tocsr()
        for reportblock in range(1,50):
            thisreport = io.mmread("model_"+str(reportblock)+"_reports.mtx")
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

        np.save("scores_dnn_"+str(i+1)+"_"+args.suffix+".npy",predictions[:,1])

        del predictions
