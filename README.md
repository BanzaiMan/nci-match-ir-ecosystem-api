# nci-match-ir-ecosystem-api
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/23c5c5dc7d3247f89eae5a053b33ecff)](https://www.codacy.com/app/FNLCR/nci-match-ir-ecosystem-api?utm_source=github.com&utm_medium=referral&utm_content=CBIIT/nci-match-ir-ecosystem-api&utm_campaign=badger)
[![Build Status](https://travis-ci.org/CBIIT/nci-match-ir-ecosystem-api.svg?branch=master)](https://travis-ci.org/CBIIT/nci-match-ir-ecosystem-api)
[![Code Climate](https://codeclimate.com/github/CBIIT/nci-match-ir-ecosystem-api/badges/gpa.svg)](https://codeclimate.com/github/CBIIT/nci-match-ir-ecosystem-api)
[![Issue Count](https://codeclimate.com/github/CBIIT/nci-match-ir-ecosystem-api/badges/issue_count.svg)](https://codeclimate.com/github/CBIIT/nci-match-ir-ecosystem-api)
[![Test Coverage](https://codeclimate.com/github/CBIIT/nci-match-ir-ecosystem-api/badges/coverage.svg)](https://codeclimate.com/github/CBIIT/nci-match-ir-ecosystem-api/coverage)


Set up AWS configuration and DynamoDB following instruction at https://wiki.nci.nih.gov/pages/viewpage.action?pageId=324044179


pip install -r requirements.txt
(try this command if any operation not permitted error on El Capiton:
sudo -H pip install -r requirements.txt --upgrade --ignore-installed six)


Environment variables must be setup in your .profile or .bash_profile:

export AUTH0_CLIENT_ID=""
export AUTH0_CLIENT_SECRET=""
export AUTH0_DOMAIN=""
export AUTH0_DATABASE=""
export SLACK_TOKEN=""
export IR_QUEUE_NAME=""
export ENVIRONMENT="development"
export AWS_ACCESS_KEY_ID=""
export AWS_SECRET_ACCESS_KEY=""

You should be able to get these values from your System administration team (i.e., Jeremy Pumphrey)


Celery must be started in order for updates to database to be processed. 
After configuring AWS environment variables and installing celery. 
It can be started by typing in the application root directory:
**celery -A tasks.tasks worker --concurrency=1 --loglevel=INFO**

Main application is started as
**python ./app.py**