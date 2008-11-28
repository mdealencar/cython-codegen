import sys
import re

from ctypeslib.codegen.gccxmlparser import parse
from ctypeslib.codegen import typedesc
from codegenlib import Func, parse_type

root = 'foo'
header_name = '%s.h' % root
header_matcher = re.compile(header_name)
xml_name = '%s.xml' % root
if sys.platform[:7] == 'darwin':
    so_name = root
else:
    so_name = 'lib%s.so' % root

items = parse(xml_name)
#keep = [it for it in items if (hasattr(it, 'name') and it.name and not it.name.startswith('__'))]
keep = []
named_items = {}
for it in items:
    # Avoid pulling all the builtins
    if hasattr(it, 'name'):
        if it.name and not it.name.startswith('__builtin'):
            if hasattr(it, 'location'):
                if header_matcher.search(it.location[0]):
                    #print "%s matched location" % it.name
                    keep.append(it)
                    named_items[it.name] = it
            else:
                keep.append(it)
                named_items[it.name] = it
    else:
        keep.append(it)

# Dictionaries name -> typedesc instances
funcs = {}
tpdefs = {}
enumvals = {}
enums = {}
structs = {}
vars = {}

# Dictionary name -> location (as integer)
locations = {}

# List of items used as function argument
arguments = {}

# List of items we may use and can handle
handled = {}

for k in keep:
    # XXX: Location computation only works when all definitions/declarations
    # are pulled from one header.
    if hasattr(k, 'name'):
        handled[k.name] = k
        if hasattr(k, 'location'):
            locations[k.name] = int(k.location[1])
    if isinstance(k, typedesc.Function):
        funcs[k.name] = k
    elif isinstance(k, typedesc.EnumValue):
        enumvals[k.name] = k
    elif isinstance(k, typedesc.Enumeration):
        enums[k.name] = k
    elif isinstance(k, typedesc.Typedef):
        tpdefs[k.name] = k
    elif isinstance(k, typedesc.Structure):
        structs[k.name] = k
    elif isinstance(k, typedesc.Variable):
        vars[k.name] = k
    else:
        print "Do not know how to handle", str(k)

from funcs import generic_as_arg

def find_named_type(tp):
    if hasattr(tp, 'name'):
        return tp.name
    elif isinstance(tp, typedesc.CvQualifiedType) or \
         isinstance(tp, typedesc.PointerType):
        return find_named_type(tp.typ)
    elif isinstance(tp, typedesc.FunctionType):
        return None
    else:
        raise ValueError("Unhandled type %s" % str(tp))

def find_unqualified_type(tp):
    if isinstance(tp, typedesc.FundamentalType) or \
            isinstance(tp, typedesc.Structure) or \
            isinstance(tp, typedesc.Typedef):
        return tp
    elif isinstance(tp, typedesc.CvQualifiedType) or \
         isinstance(tp, typedesc.PointerType):
        return find_unqualified_type(tp.typ)
    elif isinstance(tp, typedesc.FunctionType):
        return None
    else:
        raise ValueError("Unhandled type %s" % str(tp))

def generate_func_signature(func):
    args = [generic_as_arg(a) for a in func.iterArgTypes()]
    return "%s %s(%s)" % (generic_as_arg(func.returns), func.name, ", ".join(args))

def signature_types(func):
    types = []
    for a in func.iterArgTypes():
        #namedtype = find_named_type(a)
        #if namedtype:
        #    types.append(namedtype)
        types.append(a)

    return types

for name, f in funcs.items():
    print generate_func_signature(f)
    types = signature_types(f)
    for t in types:
        ut = find_unqualified_type(t)
        if ut in keep:
            arguments[ut] = None

print "Need to pull out arguments", arguments.keys()

from cytypes import generic_decl, generic_def

print "========== declarations ============="
for a in arguments.keys():
    print generic_decl(a)
    if isinstance(a, typedesc.Typedef):
        print generic_decl(a.typ)

print "========== definitions ============="
for a in arguments.keys():
    print generic_def(a)
    if isinstance(a, typedesc.Typedef):
        print generic_def(a.typ)

print "============================="
print structs
