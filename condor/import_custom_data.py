import pandas
from collections import defaultdict
from tqdm import tqdm
import numpy as np

import argparse

parser = argparse.ArgumentParser(description='Evaluate models for DDI PSM.')

parser.add_argument('--data',
                    help='CSV file containing report data',
                    action='store',
                    default='data.csv',
                    dest='data')

args = parser.parse_args()

input_data = pandas.read_csv(args.data)

drug_map = defaultdict(list)

for report_id in tqdm(input_data.report_id.unique()):
    for drug_concept_id in input_data[input_data[u'report_id']==report_id].drug_concept_id.unique():
        drug_map[int(report_id)].append(int(drug_concept_id))

np.save('drugmap.npy',drug_map)

all_drug_strings = list()

for drug_concept_id in tqdm(input_data.drug_concept_id.unique()):
    all_drug_strings.append(drug_concept_id)
print len(all_drug_strings)

np.save('alldrugstrings.npy',all_drug_strings)

all_reports = list()
for report_id in tqdm(input_data.report_id.unique()):
    all_reports.append(report_id)
print len(all_reports)

np.save('allreports.npy',all_reports)

outcome_map = defaultdict(list)

for report_id in tqdm(input_data.report_id.unique()):
    for outcome_concept_id in input_data[input_data[u'report_id']==report_id].outcome_concept_id.unique():
        outcome_map[int(report_id)].append(int(outcome_concept_id))

np.save('outcomemap.npy',outcome_map)

all_outcome_strings = list()

for outcome_concept_id in tqdm(input_data.outcome_concept_id.unique()):
    all_outcome_strings.append(outcome_concept_id)
print len(all_outcome_strings)

np.save('alloutcomestrings.npy',all_outcome_strings)

