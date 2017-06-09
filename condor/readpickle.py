import pickle
import math
import numpy as np
from scipy import io
from scipy import sparse

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

all_reportids = np.array(np.load("data/all_reportids.npy"))
ord_years = list()
all_years = np.load("data/all_years.npy").item()

for mrn in all_reportids:
    ord_years.append(int(all_years[mrn]))

ord_years = np.array(ord_years)
years_exp = np.expand_dims(ord_years,axis=1)
reactions = io.mmread("data/AEOLUS_all_reports_alloutcomes.mtx")
reactions = reactions.tocsr()


print "TdP"

dirnames = ["local_80","local_104","local_80,104"]

for dirname in dirnames:

    y = np.load(dirname+"/model_outcomes.npy")
    y = y[0:4855498]

    if dirname == "local_80":
        model_string = "1816_"
        model = "quetiapine"
    if dirname == "local_104":
        model_string = "2270_"
        model = "methadone"
    if dirname == "local_80,104":
        model_string = "1816_2270_"
        model = "quetiapine, methadone"

    print model
    print "TdP"

    for year in range(2004,2017):
        posbins = np.where ( (y==1) & (years_exp <= year) )[0]
        Avec = sparse.csr_matrix.sum(reactions[posbins,:],axis=0)
        f = open(dirname+'/results_dnn_'+model_string+str(year)+'.pkl')
        result = pickle.load(f)

        print year, ":", result[0,138], "95% CL:", result[0,138]/math.exp(1.96*result[1,138]), ",", result[0,138]*math.exp(1.96*result[1,138]), "num:", Avec[0,138]

    print "LQTS"

    for year in range(2004,2017):
        posbins = np.where ( (y==1) & (years_exp <= year) )[0]
        Avec = sparse.csr_matrix.sum(reactions[posbins,:],axis=0)
        f = open(dirname+'/results_dnn_'+model_string+str(year)+'.pkl')
        result = pickle.load(f)

        print year, ":", result[0,1650], "95% CL:", result[0,1650]/math.exp(1.96*result[1,1650]), ",", result[0,1650]*math.exp(1.96*result[1,1650]), "num:", Avec[0,1650]

#for dirname in dirnames:
#    y = np.load(dirname+"/model_outcomes.npy")
#    y = y[0:4855498]
#
#    print model_string
#
#    for year in range(2004,2017):
#        posbins = np.where ( (y==1) & (years_exp <= year) )[0]
#        Avec = sparse.csr_matrix.sum(reactions[posbins,:],axis=0)
#        print year, ":", Avec[0,1650], Avec[0,138]
