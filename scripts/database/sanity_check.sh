#!/usr/bin/env bash

# *******************************************************************
# * Script to run curl commands for testing purposes.                       *
# *******************************************************************

BLUE='\033[0;34m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

URL='http://localhost:5000'
#URL='https://pedmatch-int.nci.nih.gov'
#URL='https://pedmatch-uat.nci.nih.gov'
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${GREEN}VERSION CHECK${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/ion_reporters/version"
#
#echo -e "${YELLOW}------------------------------------------------------------------------------------------------------------------------${NC}"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${GREEN}ION REPORTER TABLE and RECORD RESOURCES${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/ion_reporters${NC}"
#echo -e "${PURPLE}To return ALL ion reporters in ion reporter table${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/ion_reporters"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/ion_reporters/{ion_reporter_id}${NC}"
#echo -e "${PURPLE}To call resources.ion_reporter_table GET for Ion Reporter with ID IR_AIO78 and return ALL values${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/ion_reporters/IR_JT3E6"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/ion_reporters/{ion_reporter_id}${NC}"
#echo -e "${PURPLE}To call resources.ion_reporter_record GET for Ion Reporter with ID IR_AIO78, SCAN and return only site and status values${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/ion_reporters/IR_AIO78?projection=site&projection=ir_status"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/ion_reporters?site=mocha${NC}"
#echo -e "${PURPLE}To call resources.ion_reporter_table GET, SCAN and return all Ion reporters with site = mocha${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/ion_reporters?site=mocha"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}POST /v1/ion_reporters?site=xxx${NC}"
#echo -e "${PURPLE}To create a new ion reporter. Must contain site name in query${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X POST "${URL}/api/v1/ion_reporters?site=mocha"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}POST /v1/ion_reporters?site=xxx${NC}"
#echo -e "${PURPLE}To create a new ion reporter, without site in query will return message: Must send in a site...${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -v -X POST "${URL}/api/v1/ion_reporters"
##
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}DELETE /v1/ion_reporters?...${NC}"
#echo -e "${PURPLE}Batch deletion request placed on queue to be processed${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X DELETE "${URL}/api/v1/ion_reporters?site=mocha&host_name=NCI-MATCH-IR"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}PUT /v1/ion_reporters/{ion_reporter_id}${NC}"
#echo -e "${PURPLE}The body of this service contains the json message that will notify the PED-MATCH system that the IR Uploader is communicating properly.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X PUT -H 'Content-Type: application/json' -d '{"ir_status":"Lost contact! Last heartbeat was sent 11355 minutes ago"}' "${URL}/api/v1/ion_reporters/IR_AIO78"
#
#curl -X PUT -H 'Content-Type: application/json' -d @./ir_item.json "${URL}/api/v1/ion_reporters/IR_WO3IA"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}DELETE /v1/ion_reporters/{ion_reporter_id}${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
## This should return pretty error
#curl -X DELETE "${URL}/api/v1/ion_reporters"
## this should work by placing the delete on queue
#curl -X DELETE "${URL}/api/v1/ion_reporters/IR_WO3IA"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/ion_reporters/{ion_repoter_id}/{patients|sample_controls}?projection=....${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/ion_reporters/IR_WAO85/sample_controls"
#
#curl -X GET "${URL}/api/v1/ion_reporters/IR_WAO85/sample_controls?projection=molecular_id"
#
#curl -X GET "${URL}/api/v1/ion_reporters/IR_WAO85/sample_controls?projection=site_ip_address&projection=control_type&projection=molecular_id"
#
## should return nice error
#curl -X GET "${URL}/api/v1/ion_reporters/IR_WAO85/sample_control"
#
## should return not implemented
#curl -X GET "${URL}/api/v1/ion_reporters/IR_WAO85/patients"
#
#
#echo -e "${YELLOW}------------------------------------------------------------------------------------------------------------------------${NC}"
#
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${GREEN}SAMPLE CONTROL TABLE and RECORD RESOURCES${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/sample_controls${NC}"
#echo -e "${PURPLE}Return back all the sample controls.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/sample_controls?site={site}&control_type={sample_control_type}${NC}"
#echo -e "${PURPLE}Return back all the sample controls for a given site and control_type. Any parameter is supported${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls?site=mocha&control_type=no_template"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/sample_controls?site=mocha&projection=site&projection=molecular_id${NC}"
#echo -e "${PURPLE}Return back only the sample controls that match a site and then only return the attributes listed${NC}"
#echo -e "${CYAN}***********************************************${NC}"
## Most awesome command ever! :-)
#curl -v -X GET "${URL}/api/v1/sample_controls?site=mocha&projection=site&projection=molecular_id"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}POST /api/v1/sample_controls?site={site}&control_type={sample_control_type}${NC}"
#echo -e "${PURPLE}Creates a new molecular id.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X POST  "${URL}/api/v1/sample_controls?site=mocha&control_type=no_template"
#curl -X POST  "${URL}/api/v1/sample_controls?site=mocha&control_type=positive"
#curl -X POST  "${URL}/api/v1/sample_controls?site=mdacc&control_type=no_template"
#curl -X POST  "${URL}/api/v1/sample_controls?site=mocha&control_type=proficiency_competency"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${PURPLE}Show error message when creating a new molecular id in a wrong way.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X POST "${URL}/api/v1/sample_controls"
#curl -X POST "${URL}/api/v1/sample_controls?site=mocha"
#curl -X POST "${URL}/api/v1/sample_controls?control_type=no_template"
#
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/sample_controls/{molecular_id}${NC}"
#echo -e "${PURPLE}Return back the sample control for a specific molecular id.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls/SC_SA1CB"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}DELETE /api/v1/sample_controls/{molecular_id}${NC}"
#echo -e "${PURPLE}Delete a specific sample control record.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X DELETE "${URL}/api/v1/sample_controls/SC_VEME6"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}PUT /api/v1/sample_controls/{molecular_id}${NC}"
#echo -e "${PURPLE}JSON to update sample control record with${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X PUT -H 'Content-Type: application/json' -d @./sc_item.json "${URL}/api/v1/sample_controls/SC_SA1CB"
#
#
#echo -e "${YELLOW}------------------------------------------------------------------------------------------------------------------------${NC}"
#
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${GREEN}ALIQUOT RESOURCE${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/aliquot/{molecular_id}${NC}"
#echo -e "${PURPLE}Returns data for molecular id if valid else 404${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/aliquot/SC_SA1CB"
#curl -X GET "${URL}/api/v1/aliquot/SC_SA1CB?projection=site&projection=molecular_id&projection=date_molecular_id_created"
#
#echo -e "${PURPLE}Get patient item. Need start patient ecosystem on server before testing ${NC}"
curl -X GET "${URL}/api/v1/aliquot/PT_SS26_TsShipped_MOI1"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}PUT /api/v1/aliquot/{molecular_id}${NC}"
#echo -e "${PURPLE}Upload IR file names and this will update database, update s3 with processed files (bai and tsv)${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
##  no_template with status failed
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data.json "${URL}/api/v1/aliquot/SC_SA1CB"
##  no_template with status failed and false positive
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_no_template_falsePositive.json "${URL}/api/v1/aliquot/SC_YQ111"
##  no_template with status passed
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_no_template_passed.json "${URL}/api/v1/aliquot/SC_KGPVI"
##  positive with status failed
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_positive_failed.json "${URL}/api/v1/aliquot/SC_67VKV"
##  positive with status passed
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_positive_passed.json "${URL}/api/v1/aliquot/SC_5AMCC"
##  positive with false positive
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_positive_falsePositive.json "${URL}/api/v1/aliquot/SC_PALFC"
##  proficiency competency
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_proficiency.json "${URL}/api/v1/aliquot/SC_FDK09"
##  proficiency competency with germline filter
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_proficiency_germline_filter.json "${URL}/api/v1/aliquot/SC_LGU30"
##  proficiency competency with no pass filter
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_data_proficiency_nopass_filter.json "${URL}/api/v1/aliquot/SC_BAXXY"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}PUT /api/v1/aliquot/{molecular_id}${NC}"
#echo -e "${PURPLE}Update confirmed attribute in sample_controls table${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_confirmed_SA1CB.json "${URL}/api/v1/aliquot/SC_SA1CB"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}PUT /api/v1/aliquot/{molecular_id}${NC}"
#echo -e "${PURPLE}Update pass_flag attribute in sample_controls table${NC}"
#echo -e "${PURPLE}pass_flag has 3 possible values: undefined, pass or reject. Default is undefined ${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#curl -H 'Content-Type: application/json' -X PUT -d @./sc_update_pass_flag_SA1CB.json "${URL}/api/v1/aliquot/SC_SA1CB"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}PUT /api/v1/aliquot/{molecular_id}${NC}"
#echo -e "${PURPLE}Process bam and vcf files for patient, send s3 path of processed files (bai and tsv) to patient ecosystem${NC}"
#echo -e "${PURPLE}Get patient item. Need start patient ecosystem on server before testing ${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -H 'Content-Type: application/json' -X PUT -d @./pt_update_data.json "${URL}/api/v1/aliquot/PT_SS26_TsShipped_MOI1"
#
#echo -e "${CYAN}***********************************************${NC}"
#
#sleep 10
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/sample_controls/{molecular_id}/{format}${NC}"
#echo -e "${PURPLE}format = vcf|tsv in this case${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/vcf"
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/tsv"
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/qc"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/sample_controls/{molecular_id}/{bam|bai}/{cdna|dna}${NC}"
#echo -e "${PURPLE}format = bam|bai in this case and type = cdna|dna is required${NC}"
#echo -e "${PURPLE}These return back a link to download files for a specific sample control.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/bam/dna"
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/bai/dna"
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/bam/cdna"
#curl -X GET "${URL}/api/v1/sample_controls/sequence_files/SC_SA1CB/bai/cdna"
#
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}DELETE /api/v1/sample_controls?site={site}${NC}"
#echo -e "${PURPLE}Delete all sample controls matching the given parameters. Deleting with query parameters is not supported.${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X DELETE "${URL}/api/v1/sample_controls?site=mdacc"
#
#
#echo -e "${YELLOW}------------------------------------------------------------------------------------------------------------------------${NC}"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${GREEN}MISCFILE RESOURCE${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/files/<string:molecular_id>/<string:file_name>${NC}"
#echo -e "${PURPLE}Returns s3_download_file_url for molecular id if valid else 404${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls/files/SC_SA1CB/qc_name"
#curl -X GET "${URL}/api/v1/sample_controls/files/SC_SA1CB/dna_bam_name"
#curl -X GET "${URL}/api/v1/sample_controls/files/SC_SA1CB/dna_bai_name"
#curl -X GET "${URL}/api/v1/sample_controls/files/SC_SA1CB/cdna_bam_name"
#curl -X GET "${URL}/api/v1/sample_controls/files/SC_SA1CB/vcf_name"
#curl -X GET "${URL}/api/v1/sample_controls/files/SC_SA1CB/cdna_bai_name"
#
#
#echo -e "${YELLOW}------------------------------------------------------------------------------------------------------------------------${NC}"
#
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${GREEN}GET Rule Engine Output QC.json File Content${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#echo -e "${BLUE}GET /api/v1/quality_control/<string:molecular_id>${NC}"
#echo -e "${PURPLE}Download QC.json file from s3, returns QC.json File Content in json format${NC}"
#echo -e "${CYAN}***********************************************${NC}"
#
#curl -X GET "${URL}/api/v1/sample_controls/quality_control/SC_SA1CB"
