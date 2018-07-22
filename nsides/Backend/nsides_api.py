'''
File to handle and modularize the api requests

@author: Kai Xiang Chen, 2018
'''

from flask import Blueprint, request, render_template, abort, make_response, send_from_directory
from jinja2 import TemplateNotFound
from query_nsides_mongo import query_nsides_in, drugs_from_effect, effects_from_ingredients, get_dictionary_of_all_ingredients_or_effects, drugs_and_effect_result, get_suggestions_of_all_ingredients_or_effects
import query_nsides_mongo
import json
from nsides_helpers import mongodbRxnormToName, effectsSnomedToName

nsides_api = Blueprint('nsides_api', __name__, template_folder='../Frontend/dist', static_folder='../Frontend/dist')
                        #name of the blueprint is what you will use in the html

@nsides_api.route('/api/drugsFromEffect/query', methods=['GET'])
def route_drugs_from_effect():
    effect = request.args.get('effect')
    return drugs_from_effect(effect)

@nsides_api.route('/api/effectsFromDrugs/query', methods=['GET'])
def route_effects_from_drugs():
    drugs = request.args.get('drugs')
    return effects_from_ingredients(drugs)

@nsides_api.route('/api/drugs_and_effect_result/query')
def route_drugs_and_effect_result():
    return query_nsides_in(drugs_and_effect_result, request)

@nsides_api.route('/api/get_all_dict/<ingredients_or_effect>', methods=['GET'])
def mapping(ingredients_or_effect):
    return get_dictionary_of_all_ingredients_or_effects(ingredients_or_effect)

@nsides_api.route('/api/get_suggestions/query')
def get_all_suggestions():
    return get_suggestions_of_all_ingredients_or_effects(request)

@nsides_api.route('/test')
def test():
    data = None
    # query_nsides_mongo.add_field_maximum_lower_bound()
    data = query_nsides_mongo.sort_by_mlb()

    if data == None:
        return json.dumps([])
    else:
        return data