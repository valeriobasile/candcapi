# general configuration
config = dict()

# C&C tools directory
config['candc_root'] = 'CHANGETHIS'

config['tokenizer'] = config['candc_root'] + '/bin/t'
config['tokenizer_opts'] = ['--stdin']

config['models'] = config['candc_root'] + '/models/boxer'
config['soap_server_url'] = 'localhost:8888'
config['soap_client'] = config['candc_root'] + '/bin/soap_client'
config['soap_client_opts'] = ['--url', config['soap_server_url']]

config['boxer'] = config['candc_root'] + '/bin/boxer'
config['boxer_opts'] = ['--stdin']

# rate limit
config['interval'] = 3600
config['rate'] = 5000

