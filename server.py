import web
import subprocess as sub
from config import config
import logging as log

urls = ('/boxer', 'boxer')
app = web.application(urls, globals())

class boxer:
    def POST(self):
        # command lines creation
        steps = ['tokenizer', 'soap_client', 'boxer']
        cmdline = {step : [config[step]]+config['{}_opts'.format(step)] 
                   for step in steps}

        # get raw text
        data = web.data()
        options = web.input(_method='get')
        
        for step in steps:
            # get options from URL
            if step == 'boxer':
                for key, value in options.iteritems():
                    cmdline[step].append('--{}'.format(key))
                    cmdline[step].append(value)
            
            # call the command line
            try:
                p = sub.Popen(cmdline[step],    
                                     stdin=sub.PIPE,
                                     stdout=sub.PIPE,
                                     stderr=sub.PIPE)
                data, err = p.communicate(data)
            except:
                log.exception('cannot communicate with {0} {1}'.format(
                                step, config[step]))
                return "cannot communicate with {}\n".format(step)
        
        # just send back the output as it is    
        return "{}\n{}".format(data, err)

if __name__ == "__main__":
    app.run()

