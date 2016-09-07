#!/usr/bin/env bash

# *******************************************************************
# * Script to run curl commands for testing purposes.                       *
# *******************************************************************

CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}VERSION CHECK${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -i http://localhost:5000/api/v1/version

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) GET /v1/ion_reporters?site=mocha etc...${NC}"
echo -e "${RED}Scan ion reporters and return data${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X GET "http://localhost:5000/api/v1/ion_reporters?site=mocha&host_name=NCI-MATCH-IR"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) POST /v1/ion_reporters?site=xxx${NC}"
echo -e "${RED}To create a new ion reporter. Pass data in json -d. Must contain site name in query${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X POST -H "Content-Type: application/json" -d '{ip_address:"143.333.85.66"}' "http://localhost:5000/api/v1/ion_reporters?site=mocha"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) DELETE /v1/ion_reporters?...${NC}"
echo -e "${RED}Batch deletion request placed on queue to be processed${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X DELETE "http://localhost:5000/api/v1/ion_reporters?site=mocha&host_name=NCI-MATCH-IR"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) GET /v1/ion_reporters/{ion_reporter_id}${NC}"
echo -e "${RED}Get information about that IR (will not return sample controls or patients)${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X GET "http://localhost:5000/api/v1/ion_reporters/IR_WAO85"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) PUT /v1/ion_reporters/{ion_reporter_id}${NC}"
echo -e "${RED}The body of this service contains the json message that will notify the PED-MATCH system that the IR Uploader is communicating properly.${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X PUT -H 'Content-Type: application/json' -d '{"status":"Lost contact! Last heartbeat was sent 11355 minutes ago"}' "http://localhost:5000/api/v1/ion_reporters/IR_WO3IA"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) DELETE /v1/ion_reporters/{ion_reporter_id}${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X DELETE "http://localhost:5000/api/v1/ion_reporters"
curl -X DELETE "http://localhost:5000/api/v1/ion_reporters/IR_WO3IA"

echo -e "${CYAN}***********************************************${NC}"
echo -e "${RED}(person: waleed) GET /api/v1/ion_reporters/{ion_repoter_id}/{patients|sample_controls}?projection=....${NC}"
echo -e "${CYAN}***********************************************${NC}"

curl -X GET "http://localhost:5000/api/v1/ion_reporters/IR_WAO85/sample_controls?projection=site_ip_address&projection=control_type&projection=molecular_id"

curl -X GET "http://localhost:5000/api/v1/ion_reporters/IR_WAO85/sample_controls?projection=molecular_id"

curl -X GET "http://localhost:5000/api/v1/ion_reporters/IR_WAO85/sample_controls"

# should return nice error
curl -X GET "http://localhost:5000/api/v1/ion_reporters/IR_WAO85/sample_control"

# should return not implemented
curl -X GET "http://localhost:5000/api/v1/ion_reporters/IR_WAO85/patients"