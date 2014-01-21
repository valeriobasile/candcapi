import web
import subprocess as sub
from config import config
import logging as log
from drg import png

TMPPNG = 'tmp.png'

urls = ('/boxer', 'boxer',
        '/boxert', 'boxert',
        '/drg', 'drg',
        '/candc', 'candc',
        '/t', 't')
app = web.application(urls, globals())

def pipeline(data, steps, options=None):
    # command lines creation
    cmdline = {step : [config[step]]+config['{}_opts'.format(step)] 
                       for step in steps}

    for step in steps:
        if options and step=='boxer':
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
    return data

class t:
    def POST(self):
        # get raw text
        data = web.data()
        
        # just send back the output as it is    
        return pipeline(data, ['tokenizer'])
        
class candc:
    def POST(self):
        # get raw text
        data = web.data()
        
        # just send back the output as it is    
        return pipeline(data, ['tokenizer', 'soap_client'])
        
class boxer:
    def POST(self):
        # get raw text
        data = web.data()
        options = web.input(_method='get')
        
        return pipeline(data, ['tokenizer', 'soap_client', 'boxer'], options)

class boxert:
    def POST(self):
        # get raw text
        data = web.data()
        options = web.input(_method='get')
        
        return pipeline(data, ['soap_client', 'boxer'], options)

class drg:
    def POST(self):
        # get raw text
        data = web.data()
        options = web.input(_method='get')
        
        drg = pipeline(data, ['tokenizer', 'soap_client', 'boxer'], options)
        png(drg.split('\n'), TMPPNG)
        return open(TMPPNG,"rb").read()

if __name__ == "__main__":
    app.run()

