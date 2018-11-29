#-------------------------------------------------------------------------------
# Name:        desuarchive_check.py
# Purpose:     For keeping tabs on DesuArchive
#
# Author:      User
#
# Created:     29-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import auto_failover_refactor as auto_failover




# Board definition/config






def main():
    pass

if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "desuarchive_check.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")