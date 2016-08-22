#!/usr/bin/env bash

# *******************************************************************
# * Script to setup SQS for testing purposes.                       *
# *******************************************************************

CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

QUEUE_NAME="update_queue"
DATA_FILE="file://send_message.json"

END_POINT=""

END_POINT="--endpoint-url $LOCAL_URL"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}DELETES QUEUE IF IT EXISTS${NC}"
echo -e "${CYAN}***********************************************${NC}"

# aws sqs delete-queue --queue-url https://sqs.us-west-2.amazonaws.com/127516845550/update_queue

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}CREATES QUEUE WITH DEFAULT ATTRIBUTES${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs create-queue --queue-name update_queue

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}PURGES QUEUE IF IT EXISTS${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs purge-queue --queue-url https://sqs.us-west-2.amazonaws.com/127516845550/update_queue

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}LISTS QUEUES${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs list-queues

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}SENDS MESSAGE${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs send-message --queue-url https://sqs.us-west-2.amazonaws.com/127516845550/update_queue --message-body "A Sample from MoCha, #3." --delay-seconds 10 --message-attributes file://send_message.json