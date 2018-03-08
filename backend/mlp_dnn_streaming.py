from keras.layers import Input, Dense, Dropout
from keras.models import Model
from keras import metrics
from keras import losses
from keras.utils import np_utils
from keras import regularizers
import tensorflow as tf

from scipy import io
from scipy.sparse import vstack
from scipy import sparse
from sklearn import metrics as metrics_skl
from sklearn.model_selection import StratifiedKFold
import numpy as np

import sys

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

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def comb_loss(y_true, y_pred):
    return losses.mean_squared_error(y_true, y_pred) + losses.categorical_crossentropy(y_true, y_pred)
#2764 -> 2863

def generate_arrays(indices, predict=False):
    if predict == False:
        while 1:
            for row in batch(indices,100):
                #yield (all_reports[row,].todense(), np.reshape(outcomes[row,],(1,2)))
                yield (all_reports[row,].todense(), np.reshape(outcomes_cat[row,],(len(row),2)))
    else:
        while 1:
            for row in batch(indices,100):
                yield (all_reports[row,].todense())
                

def shuffle_weights(model, weights=None):
    if weights is None:
        weights = model.get_weights()
    weights = [np.random.permutation(w.flat).reshape(w.shape) for w in weights]
    model.set_weights(weights)


if args.run_on_cpu:
    with tf.device("/cpu:0"):
        for i in range(0,1):

            encoding_dim = 2
            n_hidden_1 = 200
            n_hidden_2 = 50

            print ("Building positive and negative report matrices...")

            pos_reports = io.mmread('model_0_posreports.mtx')
            pos_reports = pos_reports.tocsr()

            neg_reports = io.mmread('model_0_negreports.mtx')
            neg_reports = neg_reports.tocsr()
    
            for reportblock in range(1,50):
                print ("Procesing",reportblock)
                thispos = io.mmread('model_'+str(reportblock)+'_posreports.mtx')
                thispos = thispos.tocsr()
                pos_reports = vstack((pos_reports,thispos))
    
                thisneg = io.mmread('model_'+str(reportblock)+'_negreports.mtx')
                thisneg = thisneg.tocsr()
                neg_reports = vstack((neg_reports,thisneg))

            print ("Done.")

            neg_ind = np.arange(neg_reports.shape[0])
            pos_ind = np.arange(pos_reports.shape[0])

            subset_neg_ind = np.random.choice(neg_ind, pos_reports.shape[0], replace=False)
            neg_reports_subset = neg_reports[subset_neg_ind,:]

            all_reports = vstack([pos_reports,neg_reports_subset])

            outcomes = np.concatenate((np.ones(pos_reports.shape[0],np.bool),
                                       np.zeros(neg_reports_subset.shape[0],np.bool)))

            rowSums = sparse.csr_matrix.sum(all_reports,axis=1)
            to_keep_rows = np.where(rowSums != 0)[0]

            all_reports = all_reports[to_keep_rows,:]
            outcomes = outcomes[to_keep_rows]
            #outcomes = np_utils.to_categorical(outcomes, 2)



            input_data = Input(shape=(pos_reports.shape[1],))
            #encoded_1 = Dense(n_hidden_1, activation='relu', activity_regularizer=regularizers.l1(1e-4), use_bias=False)(input_data)
            encoded_1 = Dense(n_hidden_1, activation='relu', use_bias=False)(input_data)
            #encoded_DO = Dropout(0.5)(encoded_1)
            encoded_2 = Dense(n_hidden_2, activation='relu', use_bias=False)(encoded_1)
            #encoded_DO_2 = Dropout(0.5)(encoded_2)
            encoded_3 = Dense(encoding_dim, activation='relu', use_bias=False)(encoded_2)
            encoded_out = Dense(2, activation='softmax', use_bias=False)(encoded_3)

            autoencoder = Model(inputs=input_data, outputs=encoded_out)
            encoder = Model(inputs=input_data, outputs=encoded_3)

            autoencoder.compile(optimizer='adam', loss=comb_loss, metrics=[metrics.categorical_crossentropy,
                                                                           metrics.mean_squared_error,
                                                                           'accuracy'])

            initial_weights = autoencoder.get_weights()
            
            batchsize = 1
            
            X = io.mmread("model_0_reports.mtx")
            X = X.tocsr()
            for reportblock in range(1,50):
                thisreport = io.mmread("model_"+str(reportblock)+"_reports.mtx")
                thisreport = thisreport.tocsr()
                X = vstack([X,thisreport])

            kfold = StratifiedKFold(n_splits=3,shuffle=True)

            cvscores = []
            calculated_weights = []

            for train,test in kfold.split(all_reports, outcomes):

                outcomes_cat = np_utils.to_categorical(outcomes, 2)

                shuffle_weights(autoencoder, initial_weights)
                batchsize=50000

                if pos_reports.shape[0] < 200:
                    autoencoder.fit(all_reports[train].todense(),outcomes_cat[train],validation_data=(all_reports[test].todense(),outcomes_cat[test]),epochs=100)
                    scores = autoencoder.evaluate(all_reports[test].todense(), outcomes_cat[test], verbose=0)
                else:
                    autoencoder.fit_generator(generate_arrays(train),steps_per_epoch=int(len(train)/100), epochs=100,validation_data=generate_arrays(test),validation_steps=int(len(test)/100))
                    scores = autoencoder.evaluate_generator(generate_arrays(test),steps=int(len(test)/100))
                    #scores = autoencoder.evaluate_generator(generate_arrays(test),steps=int(len(test)/100))
                    #predictions = autoencoder.predict(all_reports[test].todense())
                    #scores = metrics_skl.roc_auc_score(outcomes_cat[test,1], predictions[:,1])

                #print("%s: %.2f%" % (autoencoder.metrics_names[3], scores[3]))
                #print("%.2f" % (scores))
                print (scores)

                cvscores.append(scores[3])
                calculated_weights.append(autoencoder.get_weights())
                
            print ("max val acc:",np.amax(cvscores))
            print ("model with max val acc:",np.argmax(cvscores))

            autoencoder.set_weights(calculated_weights[np.argmax(cvscores)])

            scores = autoencoder.evaluate_generator(generate_arrays(np.arange(all_reports.shape[0])),steps=max(100,int(all_reports.shape[0]/100)))

            print (scores)

            if scores[3] < 0.80:
                print ("ACCURACY BELOW 80%, NOT SAVING SCORES")
                sys.exit()


            numsteps = X.shape[0]
            numsteps = np.ceil(float(numsteps)/float(batchsize))

            predictions = autoencoder.predict(X[0:batchsize].todense(), verbose=1)

            for rownum in np.arange(1,numsteps):
                print ("Processing",int(rownum),"out of",int(numsteps-1))
                start_point = int(rownum*batchsize)
                end_point = int((rownum+1)*batchsize)
                #print start_point,":",end_point
                if (end_point > X.shape[0]):
                    end_point = X.shape[0]
                thesepredictions = autoencoder.predict(X[start_point:end_point].todense(), verbose=0)
                predictions = np.concatenate((predictions, thesepredictions))
                del thesepredictions




            np.save("scores_dnn_"+str(i+1)+"_"+args.suffix+".npy",predictions[:,1])

            del predictions

