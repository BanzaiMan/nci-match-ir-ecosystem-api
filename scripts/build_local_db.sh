#!/usr/bin/env bash

# *******************************************************************
# * Script to setup sample_controls table for testing purposes.     *
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
DATA_FILE="file://sample_data.json"
TABLE_KEY_FILE="file://sample_table_key_conditions.json"

# Change to whatever ip address you want, http://localhost:8000 is
# the default and will cause tables to be setup on your local dynamodb
LOCAL_URL="http://localhost:8000"

# Uncomment to make script setup table on your amazon account
# END_POINT=""

# Comment out if you want to use script to setup table on amazon
END_POINT="--endpoint-url $LOCAL_URL"

ATTRIBUTE='site'
VALUE='mocha'

QUERY_ATTRIBUTE='control_type'
QUERY_VALUE='positive'

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}DELETING TABLE IF IT EXIST${NC}"
echo -e "${CYAN}***********************************************${NC}"
aws dynamodb delete-table --table-name $TABLE_NAME $END_POINT

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}BUILDING TABLE${NC}"
echo -e "${CYAN}***********************************************${NC}"
aws dynamodb create-table --table-name $TABLE_NAME --attribute-definitions AttributeName=site,AttributeType=S AttributeName=molecular_id,AttributeType=S --key-schema AttributeName=site,KeyType=HASH AttributeName=molecular_id,KeyType=RANGE --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 $END_POINT

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}WRITING SAMPLE DATA TO TABLE${NC}"
echo -e "${CYAN}***********************************************${NC}"
aws dynamodb batch-write-item --request-items $DATA_FILE $END_POINT

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}SHOWING THE TABLES ON SYSTEM${NC}"
echo -e "${CYAN}***********************************************${NC}"
aws dynamodb list-tables $END_POINT

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}DESCRIBING NEWLY CREATED AND LOADED TABLE${NC}"
echo -e "${CYAN}***********************************************${NC}"
aws dynamodb describe-table --table-name $TABLE_NAME $END_POINT

# To keep code/complexity up front as simple as possible just use the SCAN with filterExpression
# even though this is not as efficient as querying with keys. Though not always true, it is,
# generally speaking, good practice in software engineering to not optimize until you know you need too.

# Be sure to comment this part out if loading a large amount of data
# This script was created for testing/demonstration purposes and assumes a small amount of data
echo -e "${CYAN}*****************************************************************${NC}"
echo -e "${RED}SCANNING W/ FILTER EXPRESSION NEWLY CREATED AND LOADED TABLE      ${NC}"
echo -e "${CYAN}*****************************************************************${NC}"
aws dynamodb scan --table-name $TABLE_NAME --filter-expression "$ATTRIBUTE = :value" --expression-attribute-values "{\":value\":{\"S\":\"$VALUE\"}}" $END_POINT


# Querying is more efficient but makes for more complicated code.
# Notice how the second query filters only records that where selected by first matching a key.
# Whereas above, when we filtered, all records where returned and then filtered.

# Create different $TABLE_KEY_FILE and change variable to point to new file in order to play with query
echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}QUERY NEWLY CREATED AND LOADED TABLE            ${NC}"
echo -e "${CYAN}***********************************************${NC}"
aws dynamodb query --table-name $TABLE_NAME --key-conditions $TABLE_KEY_FILE $END_POINT

# Create different $TABLE_KEY_FILE and change $TABLE_KEY_FILE variable to point to new file in order to play with query
# and/or change the QUERY_* variables to see how filtering works
echo -e "${CYAN}************************************************************${NC}"
echo -e "${RED}QUERY W/ FILTER EXPRESSION NEWLY CREATED AND LOADED TABLE    ${NC}"
echo -e "${CYAN}************************************************************${NC}"
aws dynamodb query --table-name $TABLE_NAME --key-conditions $TABLE_KEY_FILE --filter-expression "$QUERY_ATTRIBUTE = :value" --expression-attribute-values "{\":value\":{\"S\":\"$QUERY_VALUE\"}}" $END_POINT

