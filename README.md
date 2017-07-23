# nsides
Exploring drug interactions on a massive scale.

## Installation
To install

1. cd to the directory where requirements.txt is located.
2. `pip install -r requirements.txt` in your shell.

## Running the Application

To run: `python application.py`

## Deploying to AWS Elastic Beanstalk

1. Make sure Elastic Beanstalk command line interface is installed (`pip install awsebcli`)
2. `eb init` -> select region `1) us-east-1 : US East (N. Virginia)` -> select an application to use `1) nsides-eb`
3. Make sure `.ebignore` is configured as desired and `requirements.txt` contains any new dependencies
4. After making changes and pushing to this repo, run `eb deploy`