#!/usr/bin/env bash

# *******************************************************************
# * Script to setup SQS for testing purposes.                       *
# *******************************************************************

CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

QUEUE_NAME="update_queue"
DATA_FILE="file://send_message.json"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}DELETES QUEUE IF IT EXISTS${NC}"
echo -e "${CYAN}***********************************************${NC}"

# aws sqs delete-queue --queue-url https://sqs.us-west-2.amazonaws.com/127516845550/update_queue

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}CREATES QUEUE WITH DEFAULT ATTRIBUTES${NC}"
echo -e "${CYAN}***********************************************${NC}"

# aws sqs create-queue --queue-name update_queue

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}PURGES QUEUE IF IT EXISTS${NC}"
echo -e "${CYAN}***********************************************${NC}"

# aws sqs purge-queue --queue-url https://sqs.us-west-2.amazonaws.com/127516845550/update_queue

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}LISTS QUEUES${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs list-queues

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}GETS QUEUE ATTRIBUTES${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs get-queue-attributes --queue-url https://sqs.us-east-1.amazonaws.com/127516845550/update_queue --attribute-names All

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}SENDS A MESSAGE${NC}"
echo -e "${CYAN}***********************************************${NC}"

# aws sqs send-message --queue-url https://sqs.us-west-2.amazonaws.com/127516845550/update_queue --message-body "'molecular_id': 'sc_WA85O','analysis_id': 'SampleControl_MoCha_3_v2_51d7eedc-5cc1-49fc-a0cc-a184ba7a6df2','site': 'MoCha','bucket': 'ped-match-sample-contro','date_molecular_id_created': '016-08-11+20:31:21.728','vcf_file_name': 'SampleControl_MoCha_3_v2_51d7eedc-5cc1-49fc-a0cc-a184ba7a6df2.vcf','dna_bam_file_name': 'SampleControl_MoCha_3_v2_51d7eedc-5cc1-49fc-a0cc-a184ba7a6df2.bam','cdna_bam_file_name':'SampleControl_MoCha_3_v2_51d7eedc-5cc1-49fc-a0cc-a184ba7a6df2_RNA.bam'" --message-attributes file://send_message.json

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}SENDS MULTIPLE MESSAGES${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs send-message-batch --queue-url https://sqs.us-east-1.amazonaws.com/127516845550/update_queue --entries file://send_message_batch.json

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}RECEIVE MESSAGES${NC}"
echo -e "${CYAN}***********************************************${NC}"

aws sqs receive-message --queue-url https://sqs.us-east-1.amazonaws.com/127516845550/update_queue --attribute-names All --message-attribute-names All --max-number-of-messages 10