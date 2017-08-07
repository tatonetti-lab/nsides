from scipy import sparse
import numpy as np

all_outcomes = np.load("CUSTOM_all_reports_outcomes_0.npy").item()

for i in range(1,20):                                     
    this_outcome = np.load("CUSTOM_all_reports_outcomes_"+str(i)+".npy").item()                                                                                                                       
    all_outcomes = sparse.vstack((all_outcomes,this_outcome))

np.save("CUSTOM_all_reports_outcomes.npy",all_outcomes)

all_outcomes = np.load("CUSTOM_all_reports_0.npy").item()

for i in range(1,20):                                     
    this_outcome = np.load("CUSTOM_all_reports_"+str(i)+".npy").item()                                                                                                                       
    all_outcomes = sparse.vstack((all_outcomes,this_outcome))

np.save("CUSTOM_all_reports.npy",all_outcomes)
