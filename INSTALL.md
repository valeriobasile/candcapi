Installation
============

To make your own installation of the C&C API, the C&C tools must be installed,
**including the SOAP-based client/server** version of the parser. For instruction
on how to install the C&C tools see the
[official documentation](http://svn.ask.it.usyd.edu.au/trac/candc/wiki/Installation "C&C installation").

Once C&C is installed and the SOAP server running, open the file config.py
and edit (at least) the two values _candc\_root_ and _soap\_server\_url_ with
respectively the root directory of the C&C installation and the url:port of
the SOAP server.

The default values for the other configuration variables should work in most
cases.

Before running the API server, check if the dependencies are installed 
(see below). Then run the server by simply typing:

    $ python server PORT

_PORT_ is the port number to open for the service. To check if the installation
was successful, try contacting the service, e.g. with cURL:

    $ curl -d 'John brohter loves Mary' 'http://localhost:7777/raw/pipeline'

Dependencies
------------

* [web.py](http://webpy.org/ "web.py")
* [python-graph](http://code.google.com/p/python-graph/)
* [pygraphviz](http://pygraphviz.github.io/)

