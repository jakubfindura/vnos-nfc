import logging

LOGGING_FILE = "logs.log"

# create logger
LOG = logging.getLogger('VNOS-SERVER')

LOG.setLevel(logging.DEBUG)
# create console handler and set level to debug
fh = logging.FileHandler(filename=LOGGING_FILE)
fh.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
fh.setFormatter(formatter)
# add ch to logger
LOG.addHandler(fh)
# 'application' code
LOG.debug('debug message')
LOG.info('info message')
LOG.warn('warn message')
LOG.error('error message')
LOG.critical('critical message')