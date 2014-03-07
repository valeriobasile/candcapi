import web
import subprocess as sub
from config import config
import logging as log
from drg import png
import json
import redis
import time

# setting up Redis for rate limit
r = redis.StrictRedis(db=0)

TMPPNG = 'tmp.png'

urls = (
        '/(.+)/version', 'version',
        '/(.+)/pipeline', 'pipeline',
        '/(.+)/boxer', 'boxer',
        '/drg', 'drg',
        '/(.+)/candc', 'candc',
        '/(.+)/t', 't',
        '/(.+)/tcandc', 'tcandc',
        '/(.+)/candcboxer', 'candcboxer',
)

app = web.application(urls, globals())

def output(data, steps, options, form):
    # rate limit
    ip = web.ctx.env['REMOTE_ADDR']
    ts = int(time.time()) / config['interval']
    keyname = "{}:{}".format(ip, ts)
    current = r.get(keyname)
    if current is None:
        r.setex(keyname, config['interval'], 1)
        current = r.get(keyname)
    if current != None and eval(current) > config['rate']:
        err = "too many requests per minute"
        out = ''
    else:
        r.incr(keyname,1)
        out, err = run(data, steps, options)
        
    if form == 'json':
        return json.dumps({'out' : out, 'err' : err})
    # raw -> return stdout
    else:
        if options is not None and 'version' in options:
            return err
        else:
            return out

def run(data, steps, options=None):
    """Creates a Unix-like pipeline with 'data' as input. The pipeline is made
by the processes in the 'steps' list. Returns a 2-tuple 
(standard output, standard error)."""
    
    # command lines creation
    cmdline = {step : [config[step]]+config['{}_opts'.format(step)] 
                       for step in steps}

    for step in steps:
        if options and step=='boxer':
            for key, value in options.iteritems():
                cmdline[step].append('--{}'.format(key))
                if key != 'version':
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
            return None, "cannot communicate with {}\n".format(step)
    return data, err

class t:
    def POST(self, form):
        return output(web.data(), ['tokenizer'], [], form)
        
class candc:
    def POST(self, form):
        return output(web.data(), ['soap_client'], [], form)
        
class tcandc:
    def POST(self, form):
        return output(web.data(), ['tokenizer', 'soap_client'], [], form)
        
class boxer:
    def POST(self, form):
        options = web.input(_method='get')
        return output(web.data(), ['boxer'], options, form)
        
class pipeline:
    def POST(self, form):
        options = web.input(_method='get')
        return output(web.data(), ['tokenizer', 'soap_client', 'boxer'], options, form)

class candcboxer:
    def POST(self, form):
        data = web.data()
        options = web.input(_method='get')
        return output(data, ['soap_client', 'boxer'], options, form)

class version:
    def POST(self, form):
        data = web.data()
        options = {'version' : 'true'}
        # this returns only stderr
        return output(data, ['soap_client', 'boxer'], options, form)
        
class drg:
    def POST(self):
        options = web.input(_method='get')
        options = {'semantics' : 'drg'}
        drg, _ = run(web.data(), ['tokenizer', 'soap_client', 'boxer'], options)
        png(drg.split('\n')[:-2], TMPPNG)
        return open(TMPPNG,"rb").read()

if __name__ == "__main__":
    app.run()

