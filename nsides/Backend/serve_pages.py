'''
File to handle and modularize the serving of frontend pages

@author: Kai Xiang Chen, 2018
'''

from flask import Blueprint, render_template, abort, make_response, send_from_directory
from jinja2 import TemplateNotFound
from nsides_helpers import authenticated

serve_pages = Blueprint('serve_pages', __name__, template_folder='../Frontend/dist', static_folder='../Frontend/dist')
                        #name of the blueprint is what you will use in the html

@serve_pages.route('/serve_bundle')#development
def serve_bundle():
    resp = make_response(send_from_directory('../Frontend/dist/bundles/dev', 'bundle.js'))

    return resp

@serve_pages.route('/')
def home():
    return render_template("nsides.html")

@serve_pages.route('/', defaults={'path': ''})
@serve_pages.route('/<path:path>')
@authenticated
def catch_all(path):
    print 'fell in catchall'
    return render_template("nsides.html")