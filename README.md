candcapi - HTTP API to access the C&amp;C/Boxer pipeline.
=========================================================

[C&C tools](http://svn.ask.it.usyd.edu.au/trac/candc "C\&C tools") 
is a suite of software for linguistic analysis of the English language, 
including a tokenizer, several taggers and a parser.
[Boxer](http://svn.ask.it.usyd.edu.au/trac/candc/wiki/boxer "Boxer") 
is a tools for deep semantic analysis that takes in input the output
of the C\&C parser. Together, the C&amp;C tools and Boxer form a pipeline
toolchain to perform a complete analysis on English text.
Here is an example:

    $ curl -d 'John loves Mary.' 'http://127.0.0.1:7778/raw/pipeline'
    sem(1,[1001:[tok:'John',pos:'NNP',lemma:'John',namex:'I-PER'],1002:[tok:loves,pos:'VBZ',lemma:love,namex:'O'],1003:[tok:'Mary',pos:'NNP',lemma:'Mary',namex:'I-PER'],1004:[tok:'.',pos:'.',lemma:'.',namex:'O']],merge(drs([[]:B,[]:C],[[1003]:named(B,mary,per,0),[1001]:named(C,john,per,0)]),drs([[]:D],[[]:rel(D,B,patient,0),[]:rel(D,C,agent,0),[1002]:pred(D,love,v,0)]))).

The main entry point to the C&amp;C/Boxer API is

`$CANDCAPI/$FORMAT/pipeline`

_$CANDCAPI_ is the URL of the API installation. _$FORMAT_ is either _raw_ or
_json_, so possible entry point include:

`http://my.installation.of.candcapi.net/raw/pipeline`
`http://my.installation.of.candcapi.net/json/pipeline`

The text to analyze must be passed as POST to the HTTP request.
The command line options for Boxer are passed as URL paramerers. Here are
listed:

* _Option (values (**default**)) description_
* copula (**true**, false) the copula will introduce an equality condition
* instantiate (true, **false**) generate Prolog atoms for all discourse referents
* integrate (true, **false**) produces one DRS for all input sentences
* modal (true, **false**) modal DRS-conditions are used
* nn (true, **false**) resolves noun-noun relations
* resolve (true, **false**) resolve all anaphoric DRSs and perform merge-reduction
* roles (**proto**, verbnet) role inventory (proto-roles or VerbNet roles
* tense (true, **false**) tense is represented following Kamp & Reyle
* theory (**drt**, sdrt) Standard DRSs with drt, Segmented DRSs with sdrt
* semantics (**drs**,pdrs,fol,drg,tacitus,der] The basic (and default) formalism of semantics is _drs_, but other formats are also possible: _pdrs_ (DRSs with labels, following Projective DRT); _fol_ (first-order formula syntax); _drg_ (discourse representation graphs); _tacitus_ (Hobbsian semantics); _ccg_ (input CCG derivation, nicely printed).

Here's an example using the option _semantics_ to get a first-order logic formula:

    $ curl -d 'Every man loves a woman' 'http://127.0.0.1:7778/raw/pipeline?semantics=fol'
    fol(1,not(some(A,and(n1man(A),not(some(B,some(C,and(r1patient(B,C),and(r1agent(B,A),and(v1love(B),n1woman(C))))))))))).

For a more extensive description of the options of Boxer see the
[official documentation](http://svn.ask.it.usyd.edu.au/trac/candc/wiki/BoxerOptions "Boxer documentation")

Output formats
--------------

The API can return either raw text or JSON. The raw text version corresponds
to the **standard output** of the http://www.let.rug.nl/basile/papers/BasileBos2011ENLG.pdf pipeline.
The JSON version is a simple JSON structure containing both the
standard output and the standard error:

    {"err": "standard error", "out": "standard output"}

Other URLs
----------

It is possible to access the single tools separately by using the
folliowing URLs:

    $CANDCAPI/$FORMAT/t
    $CANDCAPI/$FORMAT/candc
    $CANDCAPI/$FORMAT/boxer

The tokenizer _t_ takes in input a normal text. The parser _candc_ takes in 
input a tokenized text, i.e. a list of words separated by whitespace.
_boxer_ takes in input the Prolog output of the C\&C parser.
For convenience, also the combination of intermediate steps of the
pipeline are included in the API:

    $CANDCAPI/$FORMAT/tcandc
    $CANDCAPI/$FORMAT/candcboxer

respectively, the call the combination tokenizer/parser and parser/Boxer.

To see the version af C\&C/Boxer used by the API:

    $CANDCAPI/$FORMAT/version
        
Graphical output
----------------

Discourse Representation Graph is a semantic formalism described in
the paper
[V. Basile, J. Bos: Towards Generating Text from Discourse Representation Structures](http://www.let.rug.nl/basile/papers/BasileBos2011ENLG.pdf "").
The C&amp;C/Boxer API provides an entry point to generate a PNG image of the
DRG of a given text:

    $CANDCAPI/drg

The URL accepts the same GET parameter as _pipeline_ and returns a raw PNG
file.


