from flask import (abort, flash, redirect, render_template, request,
                   session, url_for)
import json

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode

from portal import app, database
from portal.decorators import authenticated
from portal.utils import (load_portal_client,
                          get_safe_redirect,
                          get_result,
                          post_result,
                          get_revoke,
                          handle_permission,
                          get_job,
                          job_permission)


@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    return render_template('home.jinja2')


@app.route('/signup', methods=['GET'])
def signup():
    """Send the user to Agave Auth"""
    return redirect(app.config['SIGNUP'])


@app.route('/login', methods=['GET'])
def login():
    """Send the user to Agave Auth."""
    return redirect(url_for('authcallback'))


@app.route('/logout', methods=['GET'])
@authenticated
def logout():
    """
    - Revoke the tokens with Agave Auth.
    - Destroy the session state.
    - Redirect the user to the Agave Auth logout page.
    """
    get_revoke()
    # Destroy the session state
    session.clear()

    redirect_uri = url_for('home', _external=True)

    return redirect(redirect_uri)


@app.route('/profile', methods=['GET', 'POST'])
@authenticated
def profile():
    """User profile information"""
    if request.method == 'GET':
        identity_id = session.get('primary_identity')
        profile = database.load_profile(identity_id)

        if profile:
            name, email, institution = profile

            session['name'] = name
            session['email'] = email
            session['institution'] = institution

        else:
            flash('Please complete any missing profile fields and press Save.')

        if request.args.get('next'):
            session['next'] = get_safe_redirect()

        return render_template('profile.jinja2')
    elif request.method == 'POST':
        name = session['name'] = request.form['name']
        email = session['email'] = request.form['email']
        institution = session['institution'] = request.form['institution']

        database.save_profile(identity_id=session['primary_identity'],
                              name=name,
                              email=email,
                              institution=institution)

        flash('Thank you! Your profile has been successfully updated.')

        if 'next' in session:
            redirect_to = session['next']
            session.pop('next')
        else:
            redirect_to = url_for('profile')

        return redirect(redirect_to)


@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles the interaction with Agave Auth."""
    # If we're coming back from Agave Auth in an error state, the error
    # will be in the "error" query string parameter.
    if 'error' in request.args:
        flash("You could not be logged into the portal: " +
              request.args.get('error_description', request.args['error']))
        return redirect(url_for('home'))

    redirect_uri = url_for('authcallback',_external=True)
    client = load_portal_client(redirect_uri)
    auth_uri = client.step1_get_authorize_url()
    print 'auth uri', auth_uri

    # If there's no "code" query string parameter, we're in this route
    # starting a Agave Auth login flow.
    if 'code' not in request.args:
        auth_uri = client.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        # If we do have a "code" param, we're coming back from Agave Auth
        # and can start the process of exchanging an auth code for a token.
        code = request.args.get('code')
        print 'code',code
        tokens = client.step2_exchange(code)
        tokens.revoke_uri = app.config['REVOKE_URL']
        token_json = tokens.to_json()
        print 'token json',token_json

        # user_profile = get_profile(tokens.access_token)
        user_profile = get_result(app.config['PROFILE_URL_BASE'],
                                  'me',
                                  tokens.access_token)
        if user_profile[0]:
            print 'username',user_profile[1]['username']
        else:
            flash("User profile was not retrieved. Error:" + user_profile[1])

        session.update(
            tokens=tokens.to_json(),
            is_authenticated=True,
            name=user_profile[1]['full_name'],
            email=user_profile[1]['email'],
            institution='',
            primary_identity=user_profile[1]['username']
        )

        profile = database.load_profile(session['primary_identity'])
        if profile:
            name, email, institution = profile

            session['name'] = name
            session['email'] = email
            session['institution'] = institution

            # handle_permission(session['primary_identity'])
        else:
            # take the user profile and save it into the database
            database.save_profile(identity_id=session['primary_identity'],
                                  name=session['name'],
                                  email=session['email'],
                                  institution=session['institution'])
            # set up the permission for new user
            handle_permission(session['primary_identity'])

            return redirect(url_for('profile',
                            next=url_for('submit_job')))

        return redirect(url_for('submit_job'))


@app.route('/jobsubmission', methods=['GET', 'POST'])
@authenticated
def submit_job():

    if request.method == 'GET':
        return render_template('jobsubmission.jinja2')

    if request.method == 'POST':
        if not request.form.get('mtype'):
            flash('Please select a model type.')
            return redirect(url_for('submit_job'))

        if not request.form.get('model_index'):
            flash('Please type a model index.')
            return redirect(url_for('submit_job'))

        #job submit routine
        job = get_job(request.form.get('mtype'),request.form.get('model_index'))
        if job[0]:
            result = job_permission(job[1]['id'])
            if not result[0]:
                flash('Job permission error: '+result[1])
            flash('Job request submitted successfully. Job ID: ' + job[1]['id'])
        else:
            flash('Job request was not submitted. Error: ' + job[1])

        # return redirect(url_for('job_status', job_id=job['id']))
        return redirect(url_for('job_list'))


@app.route('/status/<job_id>', methods=['GET'])
@authenticated
def job_status(job_id):
    """
    Call Agave to get status/details of job with
    job_id.
    The target template (job_status.jinja2) expects a Job API 'job' object.
    'job_id' is passed to the route in the URL as 'job_id'.
    """

    j_tokens = json.loads(session['tokens'])
    job_info = get_result(app.config['JOB_URL_BASE'],
                          job_id,
                          j_tokens['access_token'])

    return render_template('job_status.jinja2', jobinfo=job_info)


@app.route('/joblist', methods=['GET'])
@authenticated
def job_list():

    j_tokens = json.loads(session['tokens'])
    job_list = get_result(app.config['JOB_URL_BASE'],
                          '',
                          j_tokens['access_token'])

    return render_template('job_list.jinja2', joblist=job_list)
