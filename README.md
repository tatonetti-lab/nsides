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


## Deploying to AWS Elastic Beanstalk

1. Make sure Elastic Beanstalk command line interface is installed (`pip install awsebcli`)
2. `eb init` -> select region `1) us-east-1 : US East (N. Virginia)` -> select an application to use `1) nsides-eb`. If prompted `Do you want to set up SSH for your instances?`, choose `y` and select the appropriate keypair (e.g. `tatonettilab-website`)
3. Make sure `.ebignore` is configured as desired, and enter login credentials for `nsides.cnf` and `nsides-mongo.cnf`
4. If adding new dependencies, update `requirements.txt` using `pipreqs` (`pip install pipreqs`) by running `pipreqs --force --ignore /condor,/db .`
4. After making changes and pushing to this repo, run `eb deploy`

# nsides back-end (drug effect database population)
Please see [here](https://github.com/tatonetti-lab/nsides/tree/master/condor)

# nsides middleware (on-demand job submission)
Please see [here](https://github.com/tatonetti-lab/nsides/tree/master/job_api)
