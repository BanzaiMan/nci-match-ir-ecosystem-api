import os.path
import logging
import re
import pysam


class SequenceFileProcessor(object):

    @staticmethod
    def bam_to_bai(bam_full_path):
        logger = logging.getLogger(__name__)
        logger.info("Processing bam file to generate bai file")
        logger.debug("bam file: " + str(bam_full_path))

        if not os.path.isfile(bam_full_path):
            logger.debug("bam file does not exist: " + str(bam_full_path))
            logger.debug("Failed to convert vcf file to tsv file.")

        p = re.compile('.bam')
        bai_full_path = p.sub('.bai', bam_full_path)
        logger.debug("destination bai file: " + str(bai_full_path))

        try:
            pysam.index(bam_full_path, bai_full_path)
        except Exception as e:
            logger.error("Failed to generate bai file, because : " + e.message)
            raise

        logger.info("Generated bai file success!")
        return bai_full_path

    @staticmethod
    def vcf_to_tsv(vcf_full_path):
        logger = logging.getLogger(__name__)
        logger.info("Processing vcf file to generate tsv file")
        logger.debug("vcf file: " + str(vcf_full_path))

        if not os.path.isfile(vcf_full_path):
            logger.debug("vcf file does not exist: " + str(vcf_full_path))
            logger.debug("Failed to convert vcf file to tsv file.")

        p = re.compile('.vcf')
        tsv_full_path = p.sub('.tsv', vcf_full_path)
        logger.debug("destination tsv file: " + str(tsv_full_path))

        conversion_script = '../oncomine-vcf-converter-1.4.1/scripts/convert_vcf.py'
        curr_dir = os.path.dirname(__file__)
        conv_full_path = os.path.join(curr_dir, conversion_script)

        try:
            conversion_cmd = '%s --force -i %s -o %s' % (conv_full_path, vcf_full_path, tsv_full_path)
            logger.debug("Convert vcf to tsv command: " + str(conversion_cmd))
            os.system(conversion_cmd)
            if os.path.isfile(tsv_full_path):
                logger.info("Generated tsv file: " + str(tsv_full_path))
                return tsv_full_path
            else:
                logger.debug("Failed to generate tsv file from : " + str(vcf_full_path))
                return None
        except Exception as e:
            logger.error("Failure reason: " + e.message)
            raise
