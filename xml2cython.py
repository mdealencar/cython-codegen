"""\
xml2cython: process xml files generated by gccxml and generate cython code

Usage:
    xml2cython header xmlfile

By default, xml2cython pull out every function available in the xmlfile."""
import getopt
import sys
import re
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from tp_puller import TypePuller
from misc import classify, query_items
from cycodegen import generate_cython

def generate_main(header, xml, output, lfilter=None):
    items, named, locations = query_items(xml)

    output.write("cdef extern from '%s':\n" % header)

    funcs, tpdefs, enumvals, enums, structs, vars, unions = \
            classify(items, locations, lfilter=lfilter)

    puller = TypePuller(items)
    for f in funcs.values():
        puller.pull(f)

    needed = puller.values()

    # Order 'anonymous' enum values alphabetically
    def cmpenum(a, b):
        return cmp(a.name, b.name)
    anoenumvals = enumvals.values()
    anoenumvals.sort(cmpenum)

    # List of items to generate code for
    gen = list(needed) + funcs.values()
    generate_cython(output, gen, anoenumvals)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = """\
usage: xml2cython [options] headerfile xmlfile

%s""" % msg

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # parse command line options
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "ho:l:f:",
                                       ["help", "output", "location-filter",
                                        "function-name-filter"])
            if len(args) != 2:
                raise Usage("Error, exactly one input file must be specified")
            header_input = args[0]
            xml_input = args[1]
        except getopt.error, msg:
            raise Usage(msg)
    except Usage, e:
        print >>sys.stderr, e.msg
        print >>sys.stderr, "for help use --help"
        return 2

    # process options
    output = None
    lfilter_str = None
    ffilter_str = None
    for o, a in opts:
        if o in ("-h", "--help"):
            print __doc__
            return 0
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-l", "--location-filter"):
            lfilter_str = a
        elif o in ("-f", "--function-name-filter"):
            ffilter_str = a

    if lfilter_str:
        lfilter = re.compile(lfilter_str).search

    if ffilter_str:
        ffilter = re.compile(ffilter_str).search

    # Generate cython code
    out = StringIO()
    try:
        generate_main(header_input, xml_input, out, lfilter=lfilter)
        if output:
            f = open(output, 'w')
            try:
                f.write(out.getvalue())
            finally:
                f.close()
        else:
            print out.getvalue()
    finally:
        out.close()

if __name__ == '__main__':
    sys.exit(main())


# #root = 'asoundlib'
# #root = 'CoreAudio_AudioHardware'
# root = 'foo'
# header_name = '%s.h' % root
# #header_matcher = re.compile('alsa')
# header_matcher = re.compile(header_name)
# #header_matcher = re.compile('AudioHardware')
# xml_name = '%s.xml' % root
# pyx_name = '_%s.pyx' % root
# if sys.platform[:7] == 'darwin':
#     so_name = root
# else:
#     so_name = 'lib%s.so' % root
#
# items, named, locations = query_items(xml_name)
# funcs, tpdefs, enumvals, enums, structs, vars, unions = \
#         classify(items, locations, lfilter=header_matcher.search)
#
# #arguments = signatures_types(funcs.values())
# #print "Need to pull out arguments", [named[i] for i in arguments]
#
# puller = TypePuller(items)
# for f in funcs.values():
#     puller.pull(f)
#
# needed = puller.values()
# #print "Pulled out items:", [named[i] for i in needed]
#
# # Order 'anonymous' enum values alphabetically
# def cmpenum(a, b):
#     return cmp(a.name, b.name)
# anoenumvals = enumvals.values()
# anoenumvals.sort(cmpenum)
#
# # List of items to generate code for
# #gen = enumvals.values() + list(needed) + funcs.values()
# gen = list(needed) + funcs.values()
#
# #gen_names = [named[i] for i in gen]
#
# cython_code = [cy_generate(i) for i in gen]
#
# output = open(pyx_name, 'w')
# output.write("cdef extern from '%s':\n" % header_name)
# output.write("\tcdef enum:\n")
# for i in anoenumvals:
#     output.write("\t\t%s = %d\n" % (i.name, int(i.value)))
# for i in cython_code:
#     if not i:
#         continue
#     if len(i) > 1:
#         output.write("\t%s\n" % i[0])
#         for j in i[1:]:
#             output.write("\t%s\n" % j)
#     else:
#         output.write("\t%s\n" % i[0])
# output.close()
