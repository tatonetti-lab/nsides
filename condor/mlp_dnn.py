from keras.layers import Input, Dense, Dropout
from keras.models import Model
from keras import metrics
from keras import losses
from keras.utils import np_utils

from keras import regularizers
from scipy import io
from scipy.sparse import vstack

import numpy as np

import argparse
parser = argparse.ArgumentParser(description='Keras MLP model for DDI PSM.')
parser.add_argument('--model-number',
                    help='Numerical ID of the drug against which to fit the model',
                    action='store',
                    dest='model_num',
                    default=0)

args = parser.parse_args()

args.model_num = int(args.model_num)

runIndices = [2451,2465,2571,2512,2200,2431,2596,2875,2889,2912,2882,1931,2973,2975,2977,2983,2984,2996,3015,2960,2231,2922,2934,1955,2985,3014,2928,2916,2865,2859,2094,1960,2897,2904,2932,2071,3020,3023,2926,1864,2858,2860,2237,2950,1898,1966,2048,1876,2001,1971,2066,1793,1845,1724,1804,1745,1738,1770,1692,1782,2854,2955,3017,2890,2850,2780,2793,2731,2773,1714,1844,1697,1709,1775,1760,1786,1809,1815,1831,1799,1816,1766,1947,1801,3266,1995,2219,2114,2156,1896,2154,2296,2259,2373,2374,2324,2359,2291,2305,2283,2400,2357,2372,2311,2270,2278,2286,2304,2011,2266,2361,2391,2405,2276,1825,2207,1848,3910,1740,1837,1853,1703,1783,2524,2518,2492,2548,2552,2437,2527,1962,2031,2753,2342,2157,2723,2789,2790,1871,2804,2803,2811,2788,2835,2717,2238,2236,3180,3669,4215]

model_num = runIndices[args.model_num]
model_num = str(model_num)


def comb_loss(y_true, y_pred):
    return losses.mean_squared_error(y_true,y_pred) + losses.categorical_crossentropy(y_true, y_pred)
#2764 -> 2863
pos_reports = io.mmread('../mxnet/modelCSR_'+model_num+'_posreports.mtx')
neg_reports = io.mmread('../mxnet/modelCSR_'+model_num+'_negreports.mtx')

pos_reports = pos_reports.tocsr()
neg_reports = neg_reports.tocsr()



runTimes = 0

neg_ind = np.arange(neg_reports.shape[0])

for i in range(0,20):

    encoding_dim = 2
    n_hidden_1 = 200
    n_hidden_2 = 50

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


    autoencoder.compile(optimizer='adam', loss=comb_loss, metrics=[metrics.categorical_crossentropy, metrics.mean_squared_error, 'accuracy'])


    multFac = float(neg_reports.shape[0])/float(pos_reports.shape[0])
    if runTimes > multFac:
        continue
    else:
        runTimes = runTimes + 1

    print "multFac:",multFac

    #neg_reports_subset = neg_reports[((runTimes - 1)*pos_reports.shape[0]):(runTimes*pos_reports.shape[0]),:]

    subset_neg_ind = np.random.choice(neg_ind, pos_reports.shape[0], replace=False)
    neg_reports_subset = neg_reports[subset_neg_ind,:]

    print "Picking from ",len(neg_ind)

    neg_ind = [x for x in neg_ind if x not in subset_neg_ind]

    print "Now there are ",len(neg_ind)

    all_reports = vstack([pos_reports,neg_reports_subset]).toarray()
    outcomes = np.concatenate((np.ones(pos_reports.shape[0], np.bool), np.zeros(neg_reports_subset.shape[0], np.bool)))

    new_ind = np.random.permutation(all_reports.shape[0])
    all_reports = all_reports[new_ind,]
    outcomes = outcomes[new_ind]
    outcomes_cat = np_utils.to_categorical(outcomes, 2)

    print "Neg reports:", len(np.where(outcomes == 0)[0])
    print "Pos reports:", len(np.where(outcomes == 1)[0])

    #early_stopping = EarlyStopping(monitor='val_loss', patience=2000, verbose=1)

    #autoencoder.fit(all_reports, outcomes_cat, epochs=5000, batch_size=100000, shuffle=True, callbacks=[TensorBoard(log_dir='/tmp/autoencoder')], validation_split=0.2)
    autoencoder.fit(all_reports, outcomes_cat, epochs=5000, batch_size=100000, shuffle=True, validation_split=0.2)

    del neg_reports_subset
    del outcomes
    del outcomes_cat

    X = np.load("model_"+model_num+"_reports.npy")
    y = np.load("model_"+model_num+"_outcomes.npy")

    predictions = autoencoder.predict(X)

    np.save("scores_"+model_num+"_"+str(runTimes)+".npy",predictions[:,1])

    del predictions
    del X
    del y


#autoencoder.save('ae_subsetpos_2.h5')

#encoder.save('encoder_subsetpos_2.h5')


#p = numpy.random.permutation(len(a))
