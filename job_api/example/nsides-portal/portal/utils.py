from flask import (request,
                   session)

try:
    from urllib.parse import urlparse, urljoin
except:
    from urlparse import urlparse, urljoin

from portal import app, jobtemplate
from oauth2client.client import flow_from_clientsecrets
import requests
import json
from datetime import datetime


def load_portal_client(redirect_uri):
    """Create an AuthClient for the portal"""
    flow = flow_from_clientsecrets(app.config['CLIENT_SECRET'],
                                   scope='PRODUCTION',
                                   redirect_uri=redirect_uri)
    return flow


def is_safe_redirect_url(target):
    """https://security.openstack.org/guidelines/dg_avoid-unvalidated-redirects.html"""  # noqa
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

    return redirect_url.scheme in ('http', 'https') and \
        host_url.netloc == redirect_url.netloc


def get_safe_redirect():
    """https://security.openstack.org/guidelines/dg_avoid-unvalidated-redirects.html"""  # noqa
    url = request.args.get('next')
    if url and is_safe_redirect_url(url):
        return url

    url = request.referrer
    if url and is_safe_redirect_url(url):
        return url

    return '/'


def get_result(base_url, path, access_token):
    req_url = '{}/{}{}'.format(base_url, path, '?pretty=true')
    print 'GET request url:',req_url
    req_headers = dict(Authorization='Bearer {}'.format(access_token))
    resp = requests.get(req_url,
                        headers=req_headers,
                        verify=False)
    # resp.raise_for_status()
    print 'Status code:', resp.status_code
    resp_result = resp.json()
    print 'Response:', resp_result

    if 'status' in resp_result:
        if resp_result['status'] == 'error':
            print 'error message:', resp_result['message']
            return False, resp_result['message']
    elif 'fault' in resp_result:
        return False, resp_result['fault']['message']
    else:
        return False, resp_result

    # resp.raise_for_status()
    return True, resp_result['result']


def post_result(base_url, path, access_token, data_type, post_data):
    if path is None:
        req_url = '{}{}'.format(base_url, '?pretty=true')
    else:
        req_url = '{}/{}{}'.format(base_url, path, '?pretty=true')
    print 'POST request url:',req_url
    req_headers = dict(Authorization='Bearer {}'.format(access_token))
    if data_type == 'json':
        resp = requests.post(req_url,
                             headers=req_headers,
                             json=post_data,
                             verify=False)
    elif data_type == 'data':
        resp = requests.post(req_url,
                             headers=req_headers,
                             data=post_data,
                             verify=False)
    else:
        resp = 'Please choose the data type, "json" or "data"'
        print resp
        return False, resp

    print 'Status code:', resp.status_code
    resp_result = resp.json()
    print 'Response:', resp_result

    if 'status' in resp_result:
        if resp_result['status'] == 'error':
            print 'error message:', resp_result['message']
            return False, resp_result['message']
    elif 'fault' in resp_result:
        return False, resp_result['fault']['message']
    else:
        return False,resp_result

    # resp.raise_for_status()
    return True, resp_result['result']


def get_revoke():
    j_tokens = json.loads(session['tokens'])
    a_token = dict(token='{}'.format(j_tokens['access_token']))

    resp = requests.post(j_tokens['revoke_uri'],
                         auth=(j_tokens['client_id'],j_tokens['client_secret']),
                         data=a_token,
                         verify=False)
    resp.raise_for_status()
    print 'status code for the revoke:',resp.status_code


def handle_permission(username):
    # access token for nsidescommunity account
    # since agave app and system services was registered by nsidescommunity account
    nsides_token = app.config['NSIDESCOMMUNITY_ACCESS_TOKEN']

    # set permission for execution host to submit the job
    path = '{}/{}/{}'.format(app.config['SYSTEM_EXEC_ID'],
                             'roles',
                             username)
    resp = get_result(app.config['SYSTEM_URL_BASE'],path,nsides_token)
    if not resp[0]:
        role = {"role": "USER"}
        resp = post_result(app.config['SYSTEM_URL_BASE'],
                           path,
                           nsides_token,
                           'json',
                           role)
        print 'Result:',resp[1]

    # set permission for storage service
    path = '{}/{}/{}'.format(app.config['SYSTEM_STOR_ID'],
                             'roles',
                             username)
    resp = get_result(app.config['SYSTEM_URL_BASE'],path,nsides_token)
    if not resp[0]:
        role = {"role": "USER"}
        resp = post_result(app.config['SYSTEM_URL_BASE'],
                           path,
                           nsides_token,
                           'json',
                           role)
        print 'Result:', resp[1]

    # set permission for application service
    path = '{}/{}/{}'.format(app.config['APP_ID'],
                             'pems',
                             username)
    resp = get_result(app.config['APP_URL_BASE'], path, nsides_token)
    if not resp[0]:
        perm = 'permission=READ_EXECUTE'
        resp = post_result(app.config['APP_URL_BASE'],
                           path,
                           nsides_token,
                           'data',
                           perm)
        print 'Result:', resp[1]


def get_job(model_type, model_index):

    j_tokens = json.loads(session['tokens'])
    # edit job template
    jobtemplate['name'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    jobtemplate['appId'] = app.config['APP_ID']
    jobtemplate['archiveSystem'] = app.config['SYSTEM_STOR_ID']

    # job archival path
    archival_path = app.config['SYSTEM_STOR_PATH']
    archival_path = archival_path.replace("<username>",session['primary_identity'])
    jobtemplate['archivePath'] = archival_path
    jobtemplate['parameters']['model_type'] = model_type
    jobtemplate['parameters']['model_indexes'] = model_index
    jobtemplate['notifications'][1]['url'] = session['email']
    jobtemplate['notifications'][2]['url'] = session['email']

    print jobtemplate
    resp = post_result(app.config['JOB_URL_BASE'],
                       None,
                       j_tokens['access_token'],
                       'json',
                       jobtemplate)

    return resp


def job_permission(job_id):
    # Update user permissions for a particular job
    j_tokens = json.loads(session['tokens'])
    path = '{}/{}/{}'.format(job_id,
                             'pems',
                             app.config['ADMIN_USER'])
    perm = 'permission=ALL'
    resp = post_result(app.config['JOB_URL_BASE'],
                       path,
                       j_tokens['access_token'],
                       'data',
                       perm)
    print 'Result:', resp[1]
    return resp
