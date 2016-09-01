#!/usr/bin/env bash

# *******************************************************************
# * Script to delete item, create item, and update item from        *
# * sample_controls table for testing purposes.                     *
# * To use the script to setup table on a computer other than the   *
# * localhost, simply set the LOCAL_URL variable to the correct     *
# * location or set END_POINT to "" in order to put table on your   *
# * Amazon account, assuming your .aws/credentials are setup        *
# * correctly.                                                      *
# *******************************************************************
# * Color codes for reference purposes                              *
# *******************************************************************
# Black        0;30     Dark Gray     1;30
# Red          0;31     Light Red     1;31
# Green        0;32     Light Green   1;32
# Brown/Orange 0;33     Yellow        1;33
# Blue         0;34     Light Blue    1;34
# Purple       0;35     Light Purple  1;35
# Cyan         0;36     Light Cyan    1;36
# Light Gray   0;37     White         1;37
# *******************************************************************

CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

TABLE_NAME="sample_controls"

# Change to whatever ip address you want, http://localhost:8000 is
# the default and will cause tables to be setup on your local dynamodb
LOCAL_URL="http://localhost:8000"
CURL_URL="http://localhost:5000/api/v1/aliquot/"

# Uncomment to make script setup table on your amazon account
# END_POINT=""

# Comment out if you want to use script to setup table on amazon
END_POINT="--endpoint-url $LOCAL_URL"

ATTRIBUTE='site'
VALUE='mocha'

QUERY_ATTRIBUTE='control_type'
QUERY_VALUE='no_template'

MOLECULAR_ID='SC_YQ111'


## DELETE: Delete an item from the database
echo -e "${CYAN}************************************************************${NC}"
echo -e "${RED}DELETE A ITEM FROM TABLE: NEED A KEY JSON FILE               ${NC}"
echo -e "${CYAN}************************************************************${NC}"
aws dynamodb delete-item --table-name $TABLE_NAME --key file://key_process.json --return-consumed-capacity TOTAL $END_POINT

# PUT: Create an item.json file with the key-value pair and save it to database
echo -e "${CYAN}************************************************************${NC}"
echo -e "${RED}PUT AN NEW ITEM INTO TABLE: NEED AN ITEM JSON FILE           ${NC}"
echo -e "${CYAN}************************************************************${NC}"
aws dynamodb put-item --table-name $TABLE_NAME --item file://item_process.json --return-consumed-capacity TOTAL $END_POINT

# Need start app.py and celery before running curl command
# Curl command: parse update message, process vcf, bam files, and update sample_controls table in dynamodb database
echo -e "${CYAN}***************************************************************************************${NC}"
echo -e "${RED}READ UPDATE MESSAGE, PROCESS, AND UPDATE TABLE: NEED AN UPDATE DATA JSON FILE           ${NC}"
echo -e "${CYAN}***************************************************************************************${NC}"
curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data.json $CURL_URL$MOLECULAR_ID

echo -e "${CYAN}***************************************************************************************${NC}"
echo -e "${RED}SLEEP AND WAIT CELERY TASKS TO COMPLETE                                                 ${NC}"
echo -e "${CYAN}***************************************************************************************${NC}"
sleep 30

## Be sure to comment this part out if loading a large amount of data
## This script was created for testing/demonstration purposes and assumes a small amount of data
echo -e "${CYAN}*****************************************************************${NC}"
echo -e "${RED}SCANNING W/ FILTER EXPRESSION EXISTING TABLE                      ${NC}"
echo -e "${CYAN}*****************************************************************${NC}"
aws dynamodb scan --table-name $TABLE_NAME --filter-expression "$ATTRIBUTE = :value" --expression-attribute-values "{\":value\":{\"S\":\"$VALUE\"}}" $END_POINT
