# nsides front-end
A comprehensive database of drug-drug(s)-effect relationships

## Installation
To install

1. cd to the directory where requirements.txt is located.
2. `pip install -r requirements.txt` in your shell.

## Running the Application

To run: `python application.py`
To run using Flask: 
1. cd to subdirectory /nsides and run `export FLASK_APP=nsides.py` 
2. The application can with the comman `python -m flask run`


## Deploying and running nSides on AWS
nSides is served on an AWS EC2 instance using Nginx and uWSGI. For consistency, use the approach in the following blog post: http://vladikk.com/2013/09/12/serving-flask-with-nginx-on-ubuntu/

Caveats:

- If using virtualenv, you either have to have the virtualenv directory in the same location as the nsides.py application, or specify the location of the virtualenv using the `uWSGI -H` parameter.

# nsides back-end (drug effect database population)
Please see [here](https://github.com/tatonetti-lab/nsides/tree/master/condor)

# nsides middleware (on-demand job submission)
Please see [here](https://github.com/tatonetti-lab/nsides/tree/master/job_api)
