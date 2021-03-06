from collections import defaultdict
from scipy import sparse
import numpy as np
from tqdm import tqdm
import multiprocessing

def subjob(num):

    all_data = sparse.lil_matrix((100000,len(all_drug_strings)),dtype=np.bool)

    startnum = num*100000
    endnum = num*100000 + 100000 - 1
    for isr_report_id in tqdm(all_reports[startnum:endnum]):
    #     processed += 1
    #     if processed % 1000 == 0:
    #         print "\r",
    #         print "Processed: %d" % processed,

        #print all_reports.index(isr_report_id)
        #print drug_map[isr_report_id]
        #print isr_report_id
        for drug in drug_map[isr_report_id]:
            #if all_reports.index(isr_report_id) == 3118:
                #print "%s %s" % (drug, isr_report_id)
            x_index = all_reports.index(isr_report_id) - startnum
            y_index = all_drug_strings.index(drug)
            #print "%d %d" % (x_index,y_index)
            all_data[x_index,y_index] = True
            
    np.save("CUSTOM_all_reports_"+str(num), all_data)

if __name__ == '__main__':

    drug_map = np.load('drugmap.npy').item()
    all_reports = list(np.load('allreports.npy'))
    all_drug_strings = list(np.load('alldrugstrings.npy'))
    
    jobs = []
    for i in range(0,20):
        p = multiprocessing.Process(target=subjob,args=(i,))
        jobs.append(p)
        p.start()
