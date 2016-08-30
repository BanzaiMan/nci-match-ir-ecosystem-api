import os.path
import logging
import re
import pysam


class BamFileProcessor(object):

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
        except Exception, e:
            logger.error("Failed to generate bai file, because : " + str(bam_full_path))
            raise

        logger.info("Generated bai file success!")
        return bai_full_path