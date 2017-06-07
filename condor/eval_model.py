import numpy as np
from scipy import io
from scipy import sparse
import glob
import pickle
import sys

from operator import itemgetter

import argparse

parser = argparse.ArgumentParser(description='Evaluate models for DDI PSM.')

parser.add_argument('--model-type',
                    help='Model type to evaluate',
                    action='store',
                    default='bdt',
                    dest='model_type')

parser.add_argument('--model-number',
                    help='Model number',
                    action='store',
                    default='2451',
                    dest='model_num')

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

all_reportids = np.array(np.load("data/all_reportids.npy"))
all_ages = np.load("data/all_ages.npy").item()
all_years = np.load("data/all_years.npy").item()

ord_ages = list()
ord_years = list()
for mrn in all_reportids:
    if all_ages[mrn] != []:
        ord_ages.append((all_ages[mrn])[0])
    else:
        ord_ages.append(-1)

    ord_years.append(int(all_years[mrn]))
    
ord_ages = np.array(ord_ages)
ord_years = np.array(ord_years)

mrns_exp = np.expand_dims(all_reportids,axis=1)
ages_exp = np.expand_dims(ord_ages,axis=1)
years_exp = np.expand_dims(ord_years,axis=1)

if args.model_type == 'nopsm':
    for year in range(2004,2017):
        print "Evaluating without propensity score matching..."
        reactions = io.mmread("data/AEOLUS_all_reports_alloutcomes.mtx")
        reactions = reactions.tocsr()
        y = np.load("model_outcomes.npy")
        y = y[0:4855498]
        invy = np.ones((y.shape[0],y.shape[1]))
        invy[np.where(y==1)[0]] = 0
        #y = sparse.csc_matrix(y)
        #invy = sparse.csc_matrix(invy)
    
        reactionPRRs = list()
        reactionPRRs_err = list()
    
        posbins = np.where((y==1) & (ages_exp != -1) & (years_exp <= year))[0]
        negbins = np.where((y==0) & (ages_exp != -1) & (years_exp <= year))[0]
    
        Avec = sparse.csr_matrix.sum(reactions[posbins,:],axis=0)
        AplusB = float(len(posbins))
        Cvec = sparse.csr_matrix.sum(reactions[negbins,:],axis=0)
        CplusD = float(len(negbins))
    
        num = Avec * (1/AplusB)
        den = Cvec * (1/CplusD)
    
        for reactionIdx in range(0,reactions.shape[1]):
            thisnum = num[0,reactionIdx]
            thisden = den[0,reactionIdx]
            reactionPRRs.append(thisnum/thisden)
    
            if Avec[0,reactionIdx] !=0 and Cvec[0,reactionIdx] !=0:
                invA = 1/float(Avec[0,reactionIdx])
                invC = 1/float(Cvec[0,reactionIdx])
    
                reactionPRRs_err.append( (invA - (1/AplusB) + invC - (1/CplusD))**0.5 )
    
            else:
                reactionPRRs_err.append(-1)
    
    
        reactionPRRs_out = np.vstack(( np.asarray(reactionPRRs), np.asarray(reactionPRRs_err) ))
    
        output = open('results_'+str(args.model_type)+save_string+'_'+str(year)+'.pkl','wb')
        pickle.dump(reactionPRRs_out,output)
        output.close()

    sys.exit(0)

print("Trying to load file:")
print("scores_"+args.model_type+"*.npy")
scores_files = glob.glob("scores_"+args.model_type+"*.npy")

print "Model type:",args.model_type

print "Processing ",len(scores_files)," score files."

if len(scores_files) == 0:
    sys.exit(0)

comb_scores = np.load(scores_files[0])
comb_scores = comb_scores[0:4855498]
sum_tracker = np.ones(comb_scores.shape[0], np.int)
sum_tracker[np.where(comb_scores == 0.5)[0]] = 0
comb_scores[np.where(comb_scores == 0.5)[0]] = 0

for score_file in scores_files:
    if score_file == scores_files[0]:
        continue
    
    thisScore = np.load(score_file)
    thisScore = thisScore[0:4855498]
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

y = np.load("model_outcomes.npy")
y = y[0:4855498]

print np.sum(y), "number of cases."

resu_exp = y
outc_exp = np.expand_dims(norm_comb_scores, axis=1)

print (mrns_exp.shape)
print (ages_exp.shape)
print (years_exp.shape)
print (resu_exp.shape)
print (outc_exp.shape)

#mrns_ages_years_outcome_outc = np.hstack((mrns_exp, ages_exp, years_exp, resu_exp, outc_exp))

def calcbin(outcome=1, binLo=0.0, binHi=0.10, year=2016):
#    x_indices_posoutcome_outcbin = np.where(
#    np.logical_and(
#    np.logical_and(
#    np.logical_and(
#    np.logical_and(mrns_ages_years_outcome_outc[:,3] == outcome, mrns_ages_years_outcome_outc[:,4] <= binHi),
#        mrns_ages_years_outcome_outc[:,4] > binLo),
#        mrns_ages_years_outcome_outc[:,1] != -1),
#        mrns_ages_years_outcome_outc[:,2] == year)
#    )[0]

    x_indices_posoutcome_outcbin = np.where( (resu_exp == outcome) & (outc_exp <= binHi) & (outc_exp > binLo) & (ages_exp != -1) & (years_exp <= year))[0]

    #x_indices_posoutcome_outcbin = np.where( (mrns_ages_outcome_outc[:,2] == outcome) & (mrns_ages_outcome_outc[:,3] <= binHi) & (mrns_ages_outcome_outc[:,3] > binLo) & (mrns_ages_outcome_outc[:,1] != -1) )
   
    #print len(x_indices_posoutcome_outcbin), "\t", np.median(mrns_ages_outcome_outc[x_indices_posoutcome_outcbin,1])
    
    return x_indices_posoutcome_outcbin

for year in range(2004,2017):

    granularity = 0.0005
    
    lobin = 0.0
    hibin = granularity
    
    totPosReports = 0
    totNegReports = 0
    negAvg = 0
    posAvg = 0
    
    binList = list()
    
    while 1:
        thisBinPos = len(calcbin(1,lobin,hibin,year))
        thisBinNeg = len(calcbin(0,lobin,hibin,year))
        ratio = 0
        if thisBinPos > 0:
            ratio = float(thisBinNeg)/float(thisBinPos)
        if thisBinPos < 10 or ratio < 10.0:
            hibin = hibin+granularity
        else:
            posbins = calcbin(1,lobin,hibin,year)
            negbins = calcbin(0,lobin,hibin,year)
    
            binList.append(lobin)
            print lobin, hibin, len(posbins), len(negbins), np.mean(ages_exp[posbins]), np.mean(ages_exp[negbins])
            
            lobin=hibin
            hibin=lobin+granularity
            totPosReports = totPosReports + len(posbins)
            totNegReports = totNegReports + len(negbins)
            
            negAvg = negAvg + len(posbins)*np.mean(ages_exp[negbins])
            posAvg = posAvg + len(posbins)*np.mean(ages_exp[posbins])
        if hibin > 1.0:
            break
            
    print "Number of case reports used:",totPosReports
    print "Number of control reports used:",totNegReports
    negAvg = negAvg/totPosReports
    posAvg = posAvg/totPosReports
    print "Weighted average of controls:",negAvg
    print "Weighted average of cases:",posAvg
    
    reactions = io.mmread("data/AEOLUS_all_reports_alloutcomes.mtx")
    reactions = reactions.tocsr()
    
    binList.append(1.0)
    reactionPRRs = list()
    reactionPRRs_err = list()
    
    allposbins = calcbin(1,binList[0],1.0,year)
    
    totA = sparse.csr_matrix.sum(reactions[allposbins,:],axis=0)
    totA = sparse.csr_matrix(totA)
    totPRRden = sparse.csr_matrix((1,reactions.shape[1]))
    
    numvec = sparse.csr_matrix((1,reactions.shape[1]))
    denvec = sparse.csr_matrix((1,reactions.shape[1]))
    
    
    for bin in range(0,len(binList)-1):
        lobin = binList[bin]
        hibin = binList[bin+1]
    
        posbins = calcbin(1,lobin,hibin,year)
        negbins = calcbin(0,lobin,hibin,year)
    
        Avec = sparse.csr_matrix.sum(reactions[posbins,:],axis=0)
        Avec = sparse.csr_matrix(Avec)
        AplusB = float(len(posbins))
        Cvec = sparse.csr_matrix.sum(reactions[negbins,:],axis=0)
        Cvec = sparse.csr_matrix(Cvec)
        CplusD = float(len(negbins))
    
        numvec = numvec + Avec
        denvec = denvec + Cvec * (AplusB/CplusD)
        
        #thisTerm = (Avec/AplusB)
        #thisTerm = thisTerm*Cvec
        #print (thisTerm.shape)
        
        weightFac = sparse.csr_matrix(np.repeat(AplusB/CplusD,reactions.shape[1]))
    
        totPRRden = totPRRden + sparse.csr_matrix.multiply(weightFac,Cvec)
    
    totPRR = sparse.csr_matrix(totA/totPRRden)
    
    for reactionIdx in range(0,reactions.shape[1]):
        num = numvec[0,reactionIdx]
        den = denvec[0,reactionIdx]
    
        reactionPRRs.append(num/den)
    
    errvec = sparse.csr_matrix((1,reactions.shape[1]))
    
    for bin in range(0,len(binList)-1):
        lobin = binList[bin]
        hibin = binList[bin+1]
    
        posbins = calcbin(1,lobin,hibin,year)
        negbins = calcbin(0,lobin,hibin,year)
    
        Cvec = sparse.csr_matrix.sum(reactions[negbins,:],axis=0)
        Cvec = sparse.csr_matrix(Cvec)
        CplusD = sparse.csr_matrix(np.repeat(float(len(negbins)),reactions.shape[1]))
        Dvec = CplusD - Cvec
    
        weightvec = Cvec/CplusD
    
        Avec = sparse.csr_matrix.sum(reactions[posbins,:],axis=0)
        AplusB = float(len(posbins))
        Bvec = float(len(posbins)) - Avec
        
        #(1-totPRR*weightvec)**2 * Avec
        term1 = sparse.csr_matrix(np.repeat(1,reactions.shape[1])) - sparse.csr_matrix.multiply(totPRR,weightvec)
        term1 = sparse.csr_matrix.multiply(term1,term1)
        term1 = sparse.csr_matrix.multiply(term1,Avec)
        
        #(totPRR*weightvec)**2 * Bvec
        term2 = sparse.csr_matrix.multiply(totPRR,weightvec)
        term2 = sparse.csr_matrix(term2)
        term2 = sparse.csr_matrix.multiply(term2,term2)
        term2 = sparse.csr_matrix.multiply(term2,Bvec)
        
        # term3 = (totPRR*(Avec+Bvec))**2 * Cvec * Dvec
        # termd3den = (Cvec+Dvec)**3
        term3 = Avec+Bvec
        term3 = sparse.csr_matrix.multiply(totPRR,term3)
        term3 = sparse.csr_matrix(term3)
        term3 = sparse.csr_matrix.multiply(term3,term3)
        term3 = sparse.csr_matrix.multiply(term3,Cvec)
        term3 = sparse.csr_matrix.multiply(term3,Dvec)
        term3den = Cvec + Dvec
        term3den = sparse.csr_matrix.multiply(term3den,term3den)
        term3den = sparse.csr_matrix.multiply(term3den,term3den)
        
        term3 = sparse.csr_matrix(term3/term3den)
    
        errvec = errvec + term1 + term2 + term3
    
    errvecden = sparse.csr_matrix.multiply(totA,totA)
    errvec = sparse.csr_matrix(errvec/errvecden)
    
    for reactionIdx in range(0,reactions.shape[1]):
        reactionPRRs_err.append(errvec[0,reactionIdx]**0.5)
    
    output = open('results_'+str(args.model_type)+save_string+'_'+str(year)+'.pkl','wb')
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
