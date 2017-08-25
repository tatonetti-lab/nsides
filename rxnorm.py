import sys
import json
import urllib2
import numpy as np

W  = '\033[0m'  # white (normal)
R  = '\033[31m' # red
G  = '\033[32m' # green
O  = '\033[33m' # orange
B  = '\033[34m' # blue
P  = '\033[35m' # purple
BLACK	= '\033[30m'
LR  = '\033[91m'
LG  = '\033[92m'

# print(R+"hello how are you"+W)

def relasource2code(rela_source) :
	if rela_source == 'ATC1-4' :
		return 'ATC'
	if rela_source == 'MESHPA' :
		return 'MESH'
	if rela_source == 'CHEM' :
		return 'CHEM'
	if rela_source == 'ATC1-4' :
		return 'ATC'
	if rela_source == 'PE' :
		return 'DAILYMED'
	if rela_source == 'DISEASE' :
		return 'NDFRT'

def getRxDetails(rxcui) :
	url = 'https://rxnav.nlm.nih.gov/REST/rxcui/' + rxcui + '/properties.json'
	rxDetails = json.load(urllib2.urlopen(url))
	return rxDetails
	# try:
	#     for drug_details in rxclassMembers['drugMemberGroup']['drugMember']:
	# 		if drug_details['minConcept']['rxcui'] not in drugs:
	# 			drugs[drug_details['minConcept']['rxcui']] = { 'rxcui' : drug_details['minConcept']['rxcui'] }
	# 			drugs[drug_details['minConcept']['rxcui']] = { 'rxcui' : drug_details['minConcept']['rxcui'], 'name' : drug_details['minConcept']['name'] }
	# 		return drugs
	# except KeyError:
	#     rxclass_from_rxnorm = 'None Found'


def getClassMembers(class_id, rela_source, rela) :
	drugs = {}
	url = ''

	# print class_id
	# print rela_source
	# print rela

	url = 'https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?'
	if class_id : 
		url = url + 'classId=' + class_id
	if rela_source :
		url = url + '&relaSource=' + rela_source #relasource2code(rela_source)
	if rela :
		url = url + '&rela=' + rela

	print url 

	rxclassMembers = json.load(urllib2.urlopen(url))

	try:
	    for drug_details in rxclassMembers['drugMemberGroup']['drugMember']:
			if drug_details['minConcept']['rxcui'] not in drugs:
				drugs[drug_details['minConcept']['rxcui']] = { 'rxcui' : drug_details['minConcept']['rxcui'] }
				drugs[drug_details['minConcept']['rxcui']] = { 'rxcui' : drug_details['minConcept']['rxcui'], 'name' : drug_details['minConcept']['name'] }
	except KeyError:
	    rxclass_from_rxnorm = 'None Found'

	return drugs

def getClassFromRxnorm(rxcui) :
	output = []
	dictionary = {}
	url = 'https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui=' + rxcui
	rxnorm2rxclass = json.load(urllib2.urlopen(url))

	for details in rxnorm2rxclass['rxclassDrugInfoList']['rxclassDrugInfo']:
		if details['rxclassMinConceptItem']['classId'] not in dictionary:
			dictionary[details['rxclassMinConceptItem']['classId']] = { 'classId' : details['rxclassMinConceptItem']['classId'] }
			dictionary[details['rxclassMinConceptItem']['classId']] = { 'classId' : details['rxclassMinConceptItem']['classId'], 'className' : details['rxclassMinConceptItem']['className'], 'classType' : details['rxclassMinConceptItem']['classType'], 'rela' : details['rela'], 'relaSource' : details['relaSource'] }

	return dictionary


def concept2rxnorm(concept_id, concept2rxnorm):
	if concept2rxnorm.has_key(concept_id):
		rxnorm_from_concept = concept2rxnorm[concept_id]
		return rxnorm_from_concept
	else:
		return 'not found'


def rxnorm2concept(rxnorm_id, rxnorm2concept):
	if rxnorm2concept.has_key(rxnorm_id):
		concept_from_rxnorm = rxnorm2concept[rxnorm_id]
		return concept_from_rxnorm
	else:
		return 'not found'


def process_input():
	# print 'Number of arguments:', len(sys.argv), 'arguments.'
	# print 'Argument List:', str(sys.argv)

	if len(sys.argv) > 1: 
		return sys.argv[1]
	else :
		return ''


def main():
	weird_rxnorm = np.load('index/data/weird_rxnorm.npy')
	rxnorm2concept_obj = np.load('index/data/rxnorm2concept.npy').item()
	concept2rxnorm_obj = np.load('index/data/concept2rxnorm.npy').item()

	# Generate a list of RxNorm IDs concept IDs we have in the mongoDB minus 360 drugs that don't have well defined RxNorm inforamtion inthe API.
	mappable_rxnorm = list(set(rxnorm2concept_obj.keys()) - set(weird_rxnorm))

	#print mappable_rxnorm

	print "Hello World"

	cui = ''

	if process_input() != '':
		print "Start with a CUI ... " + process_input()
		cui = process_input()
	else :
		print "Start with a CUI ... 42898278"
		cui = '42898278'

	rxnorm_from_concept = concept2rxnorm(cui, concept2rxnorm_obj)
	print "Recieve back RxNorm CUI ... " + rxnorm_from_concept

	rxDetails = getRxDetails(rxnorm_from_concept)
	print 'Drug is named ... ' + rxDetails['properties']['name']

	print "Is this RxNorm ID in our set?"
	print("Yes" if rxnorm_from_concept in mappable_rxnorm else "No")

	print "Now check if it belongs to a class ... " 

	try:
	    rxclass_from_rxnorm = getClassFromRxnorm(rxnorm_from_concept)
	except KeyError:
	    rxclass_from_rxnorm = 'None Found'

	for key, value in rxclass_from_rxnorm.iteritems():
		print BLACK + value['className'] + ' (' + value['relaSource'] + ' - ' + value['rela'] + ') ... ' + value['classId']
		if value['classType'] == "PE" :
			class_rela = 'has_PE'
		elif value['classType'] == "DISEASE" :
			class_rela = 'may_treat'

		class_members = getClassMembers(str(value['classId']), str(value['relaSource']), str(value['rela']))

		print "Now check if the children of this class are in our set ... " 
		for key, value in class_members.iteritems():
			print(G + u'\u2714' + BLACK + ' - ' + value['rxcui'] + ', ' + value['name'] + ' (' + rxnorm2concept(value['rxcui'], rxnorm2concept_obj) + ')' + BLACK if value['rxcui'] in mappable_rxnorm else R + u'\u2718' + BLACK + ' - ' + value['rxcui'] + ', ' + value['name'] + ' (' + rxnorm2concept(value['rxcui'], rxnorm2concept_obj) + ')' + BLACK)

		#print '+++'
	# for rxclass in rxclass_from_rxnorm:
	#     if rxclass['rxclassMinConceptItem']['classId']['classId'] not in output:
	#     	output.append([details['rxclassMinConceptItem']['classId']['className'], details['rxclassMinConceptItem']['classId']['classId']])
	# print output

	

	#if rxclass_from_rxnorm != "None Found" :
		#print getClassMembers('N0000008638', 'DAILYMED', 'has_PE')
		#print getClassMembers('N0000029067', 'NDFRT', 'has_VAClass')
		#print "Classes Found"


	


if __name__ == '__main__':
    main()