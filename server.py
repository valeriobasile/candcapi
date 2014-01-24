import web
import subprocess as sub
from config import config
import logging as log
from drg import png

TMPPNG = 'tmp.png'

urls = (
        '/(.+)/version', 'version',
        '/(.+)/pipeline', 'pipeline',
        '/(.+)/boxer', 'boxer',
        '/(.+)/drg', 'drg',
        '/(.+)/candc', 'candc',
        '/(.+)/t', 't',
        '/(.+)/tcandc', 'tcandc',
        '/(.+)/candcboxer', 'candcboxer',
)

app = web.application(urls, globals())

def run(data, steps, options=None):
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
    def POST(self, output):
        return run(web.data(), ['tokenizer'])
        
class candc:
    def POST(self, output):
        return run(web.data(), ['soap_client'])
        
class tcandc:
    def POST(self, output):
        return run(web.data(), ['tokenizer', 'soap_client'])
        
class boxer:
    def POST(self, output):
        options = web.input(_method='get')
        return run(web.data(), ['boxer'], options)
        
class pipeline:
    def POST(self, output):
        options = web.input(_method='get')
        return run(web.data(), ['tokenizer', 'soap_client', 'boxer'], options)

class candcboxer:
    def POST(self, output):
        data = web.data()
        options = web.input(_method='get')
        return run(data, ['soap_client', 'boxer'], options)

class version:
    def POST(self, output):
        data = web.data()
        options = {'version' : 'true'}
        # this returns only stderr
        return run(data, ['soap_client', 'boxer'], options)

class drg:
    def POST(self, output):
        options = web.input(_method='get')
        options = {'semantics' : 'drg'}
        drg = run(web.data(), ['tokenizer', 'soap_client', 'boxer'], options)
        png(drg.split('\n')[:-2], TMPPNG)
        return open(TMPPNG,"rb").read()

if __name__ == "__main__":
    app.run()

