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

# for testing
ALIQUOT_URL="http://localhost:5000/api/v1/aliquot/"
MOLECULAR_ID='SC_YQ111'


# Need start app.py before running curl command
# Need start and celery after running curl command
# Curl command: parse update message, process vcf, bam files, and update sample_controls table in dynamodb database
echo -e "${CYAN}***************************************************************************************${NC}"
echo -e "${RED}READ UPDATE MESSAGE, PROCESS, AND UPDATE TABLE: NEED AN UPDATE DATA JSON FILE           ${NC}"
echo -e "${CYAN}***************************************************************************************${NC}"
curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data.json $CURL_URL$MOLECULAR_ID

echo -e "${CYAN}***************************************************************************************${NC}"
echo -e "${RED}RETURN DATA FOR MOLECUALR_ID IF VALID, ELSE 404                                         ${NC}"
echo -e "${CYAN}***************************************************************************************${NC}"
curl -X GET ALIQUOT_URL$MOLECULAR_ID

