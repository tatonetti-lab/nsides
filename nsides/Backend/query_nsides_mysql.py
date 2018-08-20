import pymysql

# Define table names
CREDENTIALS_DIR = './credentials/'
CONFIG_FILE = CREDENTIALS_DIR + "nsides.cnf"           # log-in credentials for database

def connect ():
    print "Connecting to the MySQL API..."

    # Connect to MySQL database
    print "Connecting to MySQL database"

    conn = pymysql.connect(read_default_file=CONFIG_FILE,
                db='ebdb',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
    return conn

def query_db(service, method, query=False, cache=False):

    print "Connecting to the MySQL API..."

    # Connect to MySQL database
    print "Connecting to MySQL database"

    conn = pymysql.connect(read_default_file=CONFIG_FILE,
                db='ebdb',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    table_suffix = ""
    json_return = []

    if service == 'va':
        print "Service: ",service
        print "Method: ",method
        if method == 'get_ddi_alerts':
            # if query[:4] == 'omop':
            #     query = query[5:]
            SQL = '''select stitch_id1, stitch_id2, ddi
                from va_drugdrug_interactions_alerts_stitch;'''

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                json_return.append({
                    "drug_1": str(result['stitch_id1']),
                    "drug_2": str(result['stitch_id2']),
                    "interaction": int(result['ddi'])
                })
        return json_return


    elif service == 'lab':
        print "Service: ",service
        print "Method: ",method
        # print "Query: ",query
        if method == 'ae_to_lab':
            SQL = '''select adverse_effect_name, lab_test_name, loinc_code, normal_range_low, normal_range_high, limit_value_low, limit_value_high, unit
                from ebdb.adverse_event_to_lab_test;'''.format(query=query)

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                json_return.append({
                    "adverse_event": str(result['adverse_effect_name']),
                    "lab_test": str(result['lab_test_name']),
                    "loinc": str(result['loinc_code']),
                    "normal_range_low": str(result['normal_range_low']),
                    "normal_range_high": str(result['normal_range_high']),
                    "limit_value_low": str(result['limit_value_low']),
                    "limit_value_high": str(result['limit_value_high']),
                    "unit": str(result['unit'])
                })
            return json_return


    elif service == 'omop':
        print "Service: ",service
        print "Method: ",method
        # print "Query: ",query

        if method == 'reference':
            SQL = '''select *
                from omop_reference_effects
                where drugbank_id != ''
                and adverse_event = '{query}';'''.format(query=query)

            # print SQL

            cur.execute(SQL)
            results = cur.fetchall()


            for result in results:
                json_return.append({
                    "drugname": str(result['drugname']),
                    "drugbank_id": str(result['drugbank_id']),
                    "causes_ae": str(result['causes_ae']),
                    "adverse_event": str(result['adverse_event'])
                })

        # Provide comma-separated list of concept_ids to map to names
        # e.g. /api/v1/query?service=omop&meta=conceptsToName&q=4196636,437643
        elif method == 'conceptsToName':
            if len(query.split(',')) > 1:
                concept_ids = str(tuple([int(c) for c in query.split(',') if c != 'None']))
                query_str = "in"
            else:
                concept_ids = query
                query_str = "="

            SQL = '''select concept_id, concept_name
                     from concept
                     where concept_id %s %s''' %(query_str, concept_ids)

            print "RUNNING MYSQL QUERY..."
            cur.execute(SQL)
            results = cur.fetchall()
            print "...QUERY FINISHED."

            for result in results:
                json_return.append({
                    "concept_id": int(result[u'concept_id']),
                    "concept_name": result[u'concept_name'].encode('ascii','ignore')
                })
                
        elif method == 'nameToConcept':
            names = str(tuple(query))
            SQL = '''
                SELECT concept_id, concept_name FROM concept
                WHERE concept_name IN %s
                ''' %(names)
            
            print "RUNNING MYSQL QUERY..."
            cur.execute(SQL)
            results = cur.fetchall()
            print "FINISHED QUERY"

            ref = {}

            for result in results:
                c_name = result[u'concept_name']
                c_id = result[u'concept_id']
                ref[c_name] = c_id
            return ref

        return json_return


    elif service == 'sider':
        print "Service: ",service
        print "Method: ",method
        # print "Query: ",query
        if method == 'drugForEffectFreq':
            SQL = """select stitch_id, drug_name, lower_bound, upper_bound
                    from effect_freqs
                    join mapped_adverse_effects using (stitch_id, umls_id)
                    where umls_id = '{query}'""".format(query=query)
            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                json_return.append({
                    "stitch_id": str(result['stitch_id']),
                    "drug_name": str(result['drug_name']),
                    "lower_bound": str(result['lower_bound']),
                    "upper_bound": str(result['upper_bound'])
                })

        if method == 'drugForEffect':
            SQL = '''select stitch_id, drug_name
                from mapped_adverse_effects
                where umls_id = '{query}';'''.format(query=query)

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()


            for result in results:
                #json_return.append(result)
                json_return.append({
                    "stitch_id": str(result['stitch_id']),
                    "drug_name": str(result['drug_name'])
                })
                    #print result


    elif service == 'snomed':
        print "Service: ",service
        if method == 'getOutcomeFromSnomedId':
            SQL = '''select pt
            from standard_case_outcome
            where snomed_outcome_concept_id = '{query}' LIMIT 1;'''.format(query=query)

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()


            for result in results:
                #json_return.append(result)
                json_return.append({
                    "outcome": str(result['pt'])
                })
                    #print result


    elif service == 'aeolus':
        #delta_qts = query_qtdb_aws.query_db(drugs)
        print "Service: ",service
        if method == 'ingredientList':
            SQL = '''select *
            from standard_drug_list
            join concept on (concept_id = standard_concept_id)
            where concept_class_id = "Ingredient";'''.format(suffix=table_suffix)

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()


            for result in results:
                #json_return.append(result)
                json_return.append({
                    "vocabulary_id": str(result['vocabulary_id']),
                    "concept_class_id": str(result['concept_class_id']),
                    "valid_start_date": str(result['valid_start_date']),
                    "valid_end_date": str(result['valid_end_date']),
                    "concept_name": str(result['concept_name'].replace("'", "")),
                    "invalid_reason": str(result['invalid_reason']),
                    "concept_code": str(result['concept_code']),
                    "standard_concept_id": int(result['standard_concept_id']),
                    "standard_concept": str(result['standard_concept']),
                    "concept_code": int(result['concept_code']),
                    "domain_id": str(result['domain_id']),
                    "concept_id": int(result['concept_id'])
                })
                    #print result
        elif method == 'drugReactionCounts':
            json_pre_return_1 = []
            json_pre_return_2 = []
            if query != ['']:
                # SQL = '''select drug_concept_id, outcome_concept_id, count_a as nreports, count_b + count_a as ndrugreports
                #     from standard_drug_outcome_contingency_table
                #     where count_a > 10;'''.format(suffix=table_suffix)
                SQL = '''select drug_concept_id, outcome_concept_id, count_a as nreports, count_b + count_a as ndrugreports
                    from standard_drug_outcome_contingency_table
                    where count_a > 10
                    limit {query},10000;'''.format(query=query)

                print SQL

                cur.execute(SQL)
                results = cur.fetchall()

                for result in results:
                    #json_return.append(result)
                    json_pre_return_1.append({
                        "drug_concept_id": int(result['drug_concept_id']),
                        "outcome_concept_id": int(result['outcome_concept_id']),
                        "nreports": int(result['nreports']),
                        "ndrugreports": int(result['ndrugreports'])
                    })
            # 'nrows'
            SQL = '''select count(*) as count
                from standard_drug_outcome_contingency_table
                where count_a > 10;'''

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            #json_pre_return_3 = int(results[0])

            print results[0]['count']

            # for result in results:
            #     #json_return.append(result)
            #     json_pre_return_2.append({ int(result['count(*)']) })

            json_pre_return_2.append(results[0]['count'])


            json_return.append({
                "result": json_pre_return_1,
                "nrows": json_pre_return_2
            })

        elif method == 'drugpairReactionCounts':
            json_pre_return_1 = []
            json_pre_return_2 = []
            if query != ['']:
                # SQL = '''select drug_concept_id, outcome_concept_id, count_a as nreports, count_b + count_a as ndrugreports
                #     from standard_drug_outcome_contingency_table
                #     where count_a > 10;'''.format(suffix=table_suffix)
                SQL = '''select outcome_concept_id, drug1_concept_id,
                    drug2_concept_id, n_d1d2ae, n_d1d2
                    from standard_drugpair_outcome_count
                    where n_d1d2ae > 10
                    limit {query},10000;'''.format(query=query)

                print SQL

                cur.execute(SQL)
                results = cur.fetchall()

                for result in results:
                    #json_return.append(result)
                    json_pre_return_1.append({
                        "outcome_concept_id": int(result['outcome_concept_id']),
                        "drug1_concept_id": int(result['drug1_concept_id']),
                        "drug2_concept_id": int(result['drug2_concept_id']),
                        "n_d1d2ae": int(result['n_d1d2ae']),
                        "n_d1d2": int(result['n_d1d2'])
                    })

            # 'nrows'
            SQL = '''select count(*) as count
                from standard_drugpair_outcome_count'''

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            #json_pre_return_3 = int(results[0])

            print results[0]['count']

            # for result in results:
            #     #json_return.append(result)
            #     json_pre_return_2.append({ int(result['count(*)']) })

            json_pre_return_2.append(results[0]['count'])


            json_return.append({
                "results": json_pre_return_1,
                "nrows": json_pre_return_2
            })
        elif method == 'reactionListSNOMED':
            SQL = '''select *
                from standard_outcome_list
                join concept on (concept_id = snomed_outcome_concept_id);'''.format(suffix=table_suffix)

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                json_return.append({
                    "outcome_concept_id": int(result['outcome_concept_id']),
                    "snomed_outcome_concept_id": int(result['snomed_outcome_concept_id']),
                    "concept_id": int(result['concept_id']),
                    "concept_name": str(result['concept_name']),
                    "domain_id": str(result['domain_id']),
                    "vocabulary_id": str(result['vocabulary_id']),
                    "concept_class_id": str(result['concept_class_id']),
                    "standard_concept": str(result['standard_concept']),
                    "concept_code": int(result['concept_code']),
                    "valid_start_date": str(result['valid_start_date']),
                    "valid_end_date": str(result['valid_end_date']),
                    "invalid_reason": str(result['invalid_reason'])})
        elif method == 'reactionListMedDRA':
            SQL = '''select *
                from standard_outcome_list
                join concept on (concept_id = outcome_concept_id);'''.format(suffix=table_suffix)

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                json_return.append({
                    "outcome_concept_id": int(result['outcome_concept_id']),
                    "snomed_outcome_concept_id": int(result['snomed_outcome_concept_id']),
                    "concept_id": int(result['concept_id']),
                    "concept_name": str(result['concept_name']).replace("'", ''),
                    "domain_id": str(result['domain_id']),
                    "vocabulary_id": str(result['vocabulary_id']),
                    "concept_class_id": str(result['concept_class_id']),
                    "standard_concept": str(result['standard_concept']),
                    "concept_code": int(result['concept_code']),
                    "valid_start_date": str(result['valid_start_date']),
                    "valid_end_date": str(result['valid_end_date']),
                    "invalid_reason": str(result['invalid_reason'])})
        elif method == 'drugpairList':
            SQL = '''select * from standard_drugpair_list;'''

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                json_return.append({
                    "drug1_concept_id": int(result['drug1_concept_id']),
                    "drug2_concept_id": int(result['drug2_concept_id'])
                })

        elif method == 'drugpairReactionListMedDRA':
            SQL = '''select *
                from standard_drugpair_outcome_list
                join concept on (concept_id = outcome_concept_id);'''

            print SQL

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                json_return.append({
                    "outcome_concept_id": int(result['outcome_concept_id']),
                    "concept_id": int(result['concept_id']),
                    "concept_name": str(result['concept_name']),
                    "domain_id": str(result['domain_id']),
                    "vocabulary_id": str(result['vocabulary_id']),
                    "concept_class_id": str(result['concept_class_id']),
                    "standard_concept": str(result['standard_concept']),
                    "concept_code": int(result['concept_code']),
                    "valid_start_date": str(result['valid_start_date']),
                    "valid_end_date": str(result['valid_end_date']),
                    "invalid_reason": str(result['invalid_reason'])
                })
        # BEACON REQUESTS
        elif method == 'getConcepts':
            SQL = '''select * from concept WHERE concept_name LIKE '{query}' limit 10'''.format(query=query)

            print SQL
            print service
            print method
            print query

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                json_return.append({
                    "id": "omop:" + str(result['concept_id']),
                    "name": str(result['concept_name']),
                    "semanticGroup": str(result['domain_id']),
                    "synonyms": [],
                    "definition": str(result['concept_name'])
                })
        elif method == 'getConceptDetails':
            if query[:6] == 'aeolus':
                query = query[7:]

            print query
            #SQL = '''select * from concept WHERE concept_id = '{query}';'''.format(query=query)
            SQL = '''select * from concept where concept_id = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)

            print SQL
            print service
            print method
            print query

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                #json_return.append(result)
                if result['domain_id'] == 'Condition':
                    semantic_group = 'DISO'
                elif result['domain_id'] == 'Observation':
                    semantic_group = 'PHEN'
                elif result['domain_id'] == 'Meas Value':
                    semantic_group = 'PHEN'
                json_return.append({
                    "id": "aeolus:" + str(result['concept_id']),
                    "name": str(result['concept_name']),
                    #"semanticGroup": str(semantic_group),
                    "semanticGroup": str(result['domain_id']),
                    "synonyms": [],
                    "definition": str(result['concept_name'])
                })
        elif method == 'getExactMatchesToConceptList':
            if query[:6] == 'aeolus':
                query = query[7:]
                SQL = '''select vocabulary_id, concept_code from concept where concept_id = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)
                cur.execute(SQL)
                results = cur.fetchall()

                for result in results:
                    json_return.append(
                        str(result['vocabulary_id'])+':'+str(result['concept_code'])
                    )
                return json_return
            elif query[:6] == 'rxnorm':
                query = query[7:]
                SQL = '''select * from concept where concept_code = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)
            elif query[:6] == 'snomed':
                query = query[7:]
                SQL = '''select * from concept where concept_code = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)

            print SQL
            print service
            print method
            print query

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                json_return.append(
                    'aeolus:'+str(result['concept_id'])
                )
            return json_return
        elif method == 'getExactMatchesToConcept':
            if query[:6] == 'aeolus':
                query = query[7:]
                SQL = '''select vocabulary_id, concept_code from concept where concept_id = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)
                cur.execute(SQL)
                results = cur.fetchall()

                for result in results:
                    json_return.append(
                        str(result['vocabulary_id'])+':'+str(result['concept_code'])
                    )
                return json_return
            elif query[:6] == 'rxnorm':
                query = query[7:]
                SQL = '''select * from concept where concept_code = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)
            elif query[:6] == 'snomed':
                query = query[7:]
                SQL = '''select * from concept where concept_code = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)

            print SQL
            print service
            print method
            print query

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                json_return.append(
                    'aeolus:'+str(result['concept_id'])
                )
            return json_return
        elif method == 'getEvidence':
            print query
        elif method == 'getStatements':
            if query[:6] == 'aeolus':
                query = query[7:]
                SQL = '''select * from concept where concept_id = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)
                cur.execute(SQL)
                results = cur.fetchall()

                for result in results:
                    json_return.append(
                        str('predicate:{')+str('instance of')+str('},')+
                        str('object:{')+str(result['concept_class_id'])+str('},')+
                        str('subject:{')+str(result['concept_name'])+str('},')+
                        str('id:id')
                    )
                return json_return
            elif query[:6] == 'rxnorm':
                query = query[7:]
                SQL = '''select * from concept where concept_code = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)
            elif query[:6] == 'snomed':
                query = query[7:]
                SQL = '''select * from concept where concept_code = {query} and domain_id in ("Drug", "Condition", "Procedure", "Measurement");'''.format(query=query)

            print SQL
            print service
            print method
            print query

            cur.execute(SQL)
            results = cur.fetchall()

            for result in results:
                json_return.append({
                    'predicate:{'+'}',
                    'object:{'+'}',
                    'subject:{'+'}',
                    'id:id',
                }
                )
            return json_return


    #print json_return

    cur.close()
    conn.close()

    return json_return

def nameToConcept (name):
    return
