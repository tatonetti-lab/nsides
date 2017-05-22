import numpy as np
from scipy import io
from scipy import sparse
import glob
import pickle
import sys

import argparse

parser = argparse.ArgumentParser(description='Evaluate models for DDI PSM.')
parser.add_argument('--model-number',
                    help='Numerical ID of the drug against which to fit the model',
                    action='store',
                    dest='model_num',
                    default=2451)

parser.add_argument('--model-type',
                    help='Model type to evaluate',
                    action='store',
                    default='bdt',
                    dest='model_type')

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

if args.model_type == 'nopsm':
    print "Evaluating without propensity score matching..."
    reactions = io.mmread("AEOLUS_all_reports_alloutcomes.mtx")
    reactions = reactions.tocsc()
    y = np.load("model_"+str(model_num)+"_outcomes.npy")
    invy = np.ones((y.shape[0],y.shape[1]))
    invy[np.where(y==1)[0]] = 0
    y = sparse.csc_matrix(y)
    invy = sparse.csc_matrix(invy)

    reactionPRRs = list()

    for reactionIdx in range(0,reactions.shape[1]):
        if reactionIdx % 200 == 0:
            print "Processed",reactionIdx,"reactions."
        reactionVector = reactions[:,reactionIdx]
        exposedVector = sparse.csc_matrix.multiply(y,reactionVector)
        nonexposedVector = sparse.csc_matrix.multiply(invy,reactionVector)
        
        A = sparse.csc_matrix.sum(exposedVector)
        AplusB = sparse.csc_matrix.sum(y)
        C = sparse.csc_matrix.sum(nonexposedVector)
        CplusD = sparse.csc_matrix.sum(invy)
        if AplusB > 0 and CplusD > 0:
            A = float(A)
            AplusB = float(AplusB)
            C = float(C)
            CplusD = float(CplusD)

            num = A/AplusB
            den = C/CplusD
            if den > 0:
                reactionPRRs.append(num/den)
            else:
                reactionPRRs.append(-1)
        else:
            reactionPRRs.append(-1)

    output = open('results_'+str(model_num)+'_'+str(args.model_type)+'.pkl','wb')
    pickle.dump(reactionPRRs,output)
    output.close()

    sys.exit(0)

    

scores_files = glob.glob("scores_"+args.model_type+"_"+model_num+"*.npy")

print "Processing model,",model_num
print "Model type:",args.model_type

print "Processing ",len(scores_files)," score files."

comb_scores = np.load(scores_files[0])
sum_tracker = np.ones(comb_scores.shape[0], np.int)
sum_tracker[np.where(comb_scores == 0.5)[0]] = 0
comb_scores[np.where(comb_scores == 0.5)[0]] = 0

for score_file in scores_files:
    if score_file == scores_files[0]:
        continue
    
    thisScore = np.load(score_file)
    thisTracker = np.ones(thisScore.shape[0], np.int)
    thisTracker[np.where(thisScore == 0.5)[0]] = 0
    thisScore[np.where(thisScore == 0.5)[0]] = 0
    comb_scores = np.add(comb_scores,thisScore)
    sum_tracker = np.add(sum_tracker, thisTracker)

norm_comb_scores = np.divide(comb_scores, sum_tracker)

zerbins = np.where(sum_tracker == 0.0)

sum_tracker[ zerbins ] = 1
comb_scores[ zerbins ] = 10

norm_comb_scores = np.divide(comb_scores, sum_tracker)

y = np.load("model_"+str(model_num)+"_outcomes.npy")

print np.sum(y), "number of cases."

all_reportids = np.array(np.load("all_reportids.npy"))
all_ages = np.load("all_ages.npy").item()

ord_ages = list()
for mrn in all_reportids:
    if all_ages[mrn] != []:
        ord_ages.append((all_ages[mrn])[0])
    else:
        ord_ages.append(-1)
    
ord_ages = np.array(ord_ages)

mrns_exp = np.expand_dims(all_reportids,axis=1)
ages_exp = np.expand_dims(ord_ages,axis=1)
resu_exp = y
outc_exp = np.expand_dims(norm_comb_scores, axis=1)

print (mrns_exp.shape)
print (ages_exp.shape)
print (resu_exp.shape)
print (outc_exp.shape)

mrns_ages_outcome_outc = np.hstack((mrns_exp, ages_exp, resu_exp, outc_exp))

def calcbin(outcome=1, binLo=0.0, binHi=0.10):
    x_indices_posoutcome_outcbin = np.where(
    np.logical_and(
    np.logical_and(
    np.logical_and(mrns_ages_outcome_outc[:,2] == outcome, mrns_ages_outcome_outc[:,3] <= binHi),
        mrns_ages_outcome_outc[:,3] > binLo),
        mrns_ages_outcome_outc[:,1] != -1)
    )[0]

    #x_indices_posoutcome_outcbin = np.where( (mrns_ages_outcome_outc[:,2] == outcome) & (mrns_ages_outcome_outc[:,3] <= binHi) & (mrns_ages_outcome_outc[:,3] > binLo) & (mrns_ages_outcome_outc[:,1] != -1) )
   
    #print len(x_indices_posoutcome_outcbin), "\t", np.median(mrns_ages_outcome_outc[x_indices_posoutcome_outcbin,1])
    
    return x_indices_posoutcome_outcbin


granularity = 0.0005

lobin = 0.0
hibin = granularity

totPosReports = 0
totNegReports = 0
negAvg = 0
posAvg = 0

binList = list()

while 1:
    thisBinPos = len(calcbin(1,lobin,hibin))
    thisBinNeg = len(calcbin(0,lobin,hibin))
    ratio = 0
    if thisBinPos > 0:
        ratio = float(thisBinNeg)/float(thisBinPos)
    if thisBinPos < 10 or ratio < 10.0:
        hibin = hibin+granularity
    else:
        posbins = calcbin(1,lobin,hibin)
        negbins = calcbin(0,lobin,hibin)

        binList.append(lobin)
        print lobin, hibin, len(posbins), len(negbins), np.mean(mrns_ages_outcome_outc[posbins,1]), np.mean(mrns_ages_outcome_outc[negbins,1])
        
        lobin=hibin
        hibin=lobin+granularity
        totPosReports = totPosReports + len(posbins)
        totNegReports = totNegReports + len(negbins)
        
        negAvg = negAvg + len(posbins)*np.mean(mrns_ages_outcome_outc[negbins,1])
        posAvg = posAvg + len(posbins)*np.mean(mrns_ages_outcome_outc[posbins,1])
    if hibin > 1.0:
        break
        
print "Number of case reports used:",totPosReports
print "Number of control reports used:",totNegReports
negAvg = negAvg/totPosReports
posAvg = posAvg/totPosReports
print "Weighted average of controls:",negAvg
print "Weighted average of cases:",posAvg

reactions = io.mmread("AEOLUS_all_reports_alloutcomes.mtx")
reactions = reactions.tocsc()

binList.append(1.0)
reactionPRRs = list()

for reactionIdx in range(0,reactions.shape[1]):

    num = 0
    den = 0

    for bin in range(0,len(binList)-1):
        lobin = binList[bin]
        hibin = binList[bin+1]
        
        posbins = calcbin(1,lobin,hibin)
        negbins = calcbin(0,lobin,hibin)
        
        posreports = reactions[posbins,:]
        negreports = reactions[negbins,:]


    
        exposedVector = posreports[:,reactionIdx]
        thisA = sparse.csc_matrix.sum(exposedVector)
        thisB = exposedVector.shape[0] - sparse.csc_matrix.sum(exposedVector)
        nonexposedVector = negreports[:,reactionIdx]
        thisC = sparse.csc_matrix.sum(nonexposedVector)
        thisD = nonexposedVector.shape[0] - sparse.csc_matrix.sum(nonexposedVector)

        thisWeight = 0
        if (thisC+thisD) > 0:
            thisWeight = thisC/(thisC+thisD)

        num = num + thisA
        den = den + (thisA + thisB)*thisWeight

    if (den != 0):
        reactionPRRs.append(num/den)
    else:
        reactionPRRs.append(-1)



output = open('results_'+str(model_num)+'_'+str(args.model_type)+'.pkl','wb')
pickle.dump(reactionPRRs,output)
output.close()


    
#
#drugExposure = sparse.csc_matrix(y)
#
#print "Reactions shape:",reactions.shape
#
#for reactionIdx in range(0,reactions.shape[1]):
#    thisReaction = reactions[:,reactionIdx]
#    #sparse.csc
