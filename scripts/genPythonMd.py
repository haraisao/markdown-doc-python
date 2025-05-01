#!/usr/bin/python3
#
from ast import *
from ast_comments import *
import os
import traceback
import re
#
#
def get_contents(fname):
  try:
    with open(fname, 'r', encoding='utf-8') as f:
      content = f.read()
      return content
  except:
    print("Error in get_contents")
  return ""
#
#
def save_contents(fname, contents):
  dirname = os.path.dirname(fname)
  if not os.path.exists(dirname):
    os.mkdir(dirname)
  try:
    with open(fname, 'w', encoding='utf-8') as f:
      f.write(contents)
      return
  except:
    print("Error in save_contents")
  return

#
#
def parseModule(fname):
  contents = get_contents(fname)
  if contents:
    root = parse(contents)
    return root
  else:
    print("Fail to paese file: %s" % fname)
  return None
    
#
#
def mkcomment(cmt):
  res=[]
  for x in cmt:
    cmt_=x.value[1:].lstrip()
    if res or cmt_:
      res.append(cmt_)
  return "\n".join(res)

#
#
def getClasses(body):
  if isinstance(body, Module): body=body.body
  res = {}
  for itm in body:
    if isinstance(itm, ClassDef):
      res[itm.name] = itm
  return res

def getClassNames(body):
  if isinstance(body, Module): body=body.body
  res = []
  for itm in body:
    if isinstance(itm, ClassDef):
      res.append(itm.name)
  return res


def getClassInfo(body, name):
  if isinstance(body, Module): body=body.body
  res = {'comment': "", 'tree': None}
  cmmt=[]
  for itm in body:
    if isinstance(itm, Comment):
      if re.match('^#####',itm.value) :
        cmmt=[]
      else:
        cmmt.append(itm)
    else:
      if isinstance(itm, ClassDef):
        if itm.name == name:
          res['tree'] = itm
          res['comment'] = mkcomment(cmmt)
          return res
      cmmt=[]
  return res

#
#
def getFunctions(body):
  if isinstance(body, ClassDef): body=body.body
  res = {}
  for itm in body:
    if isinstance(itm, FunctionDef):
      res[itm.name] = itm
  return res
#
#
def getFunctionNames(body):
  if isinstance(body, ClassDef): body=body.body
  res = []
  for itm in body:
    if isinstance(itm, FunctionDef):
      res.append(itm.name)
  return res
#
#
def getFunctionInfo(body, name):
  if isinstance(body, ClassDef): body=body.body
  res = {'comment': "", 'tree': None}
  cmmt=[]
  for itm in body:
    if isinstance(itm, Comment):
      if re.match('^#####',itm.value) :
        cmmt=[]
      else:
        cmmt.append(itm)
    else:
      if isinstance(itm, FunctionDef):
        if itm.name == name:
          res['tree'] = itm
          res['comment'] = mkcomment(cmmt)
          return res
      cmmt=[]
  return res
#
#
def getAssign(body):
  res=[]
  for itm in body:
    if isinstance(itm, Assign):
      res.append(itm)
  return res

def printAssign(x):
  print(val2String(x))
  return

def printAssignList(tree):
  assigns = getAssign(tree.body)
  res=[]
  for x in assigns:
    res.append("- %s" % val2String(x))
  return "\n".join(res)

def printFunctionList(tree):
  funcs = getFunctions(tree.body)
  res=[]
  for x in funcs:
    info=getFunctionInfo(tree.body, x)
    res.append("- %s  " % val2String(funcs[x]).replace("_","\_"))
    res.append("    %s  " % info['comment'])
  return "\n".join(res)

#
#
def getTuple(tpl):
  return "(%s)" % ', '.join([x.value for x in tpl.elts])

def replace_strings(val, chrdict):
  for k in chrdict:
    val = val.replace(k, chrdict[k])
  return val

#
#
DEFAULT_CHRS={"\n": "\\n", "\t": "\\t", "\r": "\\r"}

def val2String(val):
  if isinstance(val, Constant):
    return val2String(val.value)

  elif isinstance(val, List) :
    return "[%s]" % ','.join([val2String(x) for x in val.elts])

  elif isinstance(val, Tuple) :
    return "(%s)" % ','.join([val2String(x) for x in val.elts])

  elif isinstance(val, Name) :
    return "%s" % val.id

  elif isinstance(val, UnaryOp) :
    res = val2String(val.op) + val2String( val.operand)
    return res

  elif isinstance(val, USub) :
    return "-"

  elif isinstance(val, Div) :
    return "/"

  elif isinstance(val, Attribute) :
    return val2String(val.value) +"." + val.attr

  elif isinstance(val, BinOp) :
    res = val2String(val.left) + val2String(val.op) + val2String( val.right)
    return res

  elif isinstance(val, Assign):
    return "**%s** = %s  " % (val2String(val.targets), val2String(val.value))

  elif isinstance(val, FunctionDef) :
    name = val.name
    args = getArgList(val.args)
    return "**%s**(%s)" % (name, ','.join(args))

  elif isinstance(val, list):
    if len(val) == 1:
      return val2String(val[0])
    else:
      return "[%s]" % ','.join([val2String(x) for x in val])
  elif isinstance(val, Dict) :
    keys=val.keys
    values=val.values
    res = []
    for i in range(len(keys)):
      res.append("%s: %s" % (val2String(keys[i]), val2String(values[i])))
    return "{%s}" % ','.join(res)

  elif isinstance(val, int) or isinstance(val, float):
    return str(val)

  elif isinstance(val, str):
    return "'%s'" % replace_strings(val, DEFAULT_CHRS)

  elif val is None:
    return "None"
    
#
#
def getArgList(args):
  arglist = [x.arg for x in args.args]
  defaultlist = [val2String(x) for x in args.defaults]
  start_idx = len(arglist) - len(defaultlist)
  res=[]
  for i in range(len(arglist)):
    if i < start_idx:
      if arglist[i] == 'self':
        continue
      res.append(arglist[i])
    else:
      res.append("{0}={1}".format(arglist[i], defaultlist[i-start_idx]) )
  return res

#
#
def getClassTreeDiagram(root, basename, class_list=[]):
  clss=getClasses(root.body)

  contents=[]
  for klass in clss:
    for base in clss[klass].bases:
      parent=val2String(base)
      contents.append("%s<|--%s" % (parent, klass))

    if class_list == ['all']:
      contents.append("%s" % getClassDetail(clss[klass]))
    elif klass in class_list:
      contents.append("%s" % getClassDetail(clss[klass]))

    contents.append("class %s" % klass)
    contents.append("link %s \"%s/%s\" \"Link of %s\"" % (klass, basename, klass, klass))
  return "\n".join(contents)

#
#
def getClassDiagram(root, class_name):
  clss=getClasses(root.body)
  contents=[]
  for klass in clss:
    for base in clss[klass].bases:
      parent=val2String(base)
      if parent == class_name or klass == class_name:
        contents.append("%s<|--%s" % (parent, klass))

  contents.append("%s" % getClassDetail(clss[class_name]))

  return "\n".join(contents)

#
#
def output_class_md(dirname, tree, name, clss, cmts):
  parent=os.path.basename(dirname)
  content=[]
  content.append("# [%s](/%s)/%s" %  (parent, parent, name))
  content.append("%s" % cmts)

  content.append(printMermaidHeader())
  content.append(getClassDiagram(tree, name))
  content.append(printMermaidFooter())

  funcs = getFunctions(clss.body)
  slots = getAssignment(funcs['__init__'])

  content.append("## Slots")
  for val in slots:
    content.append("- %s" % (val))

  content.append("## Methods")
  content.append(printFunctionList(clss))
  save_contents("%s/%s.md" % (dirname, name), "\n".join(content))
  return
#
#
def getClassDetail(klass):
  res=[]
  try:
    funcs = getFunctions(klass.body)
    slots = getAssignment(funcs['__init__'])

    for val in slots:
      res.append("%s:%s" % (klass.name, val))
    for fname in funcs:
      args = getArgList(funcs[fname].args)
      res.append("%s:%s(%s)" % (klass.name, fname.replace('_', '\_'), ', '.join(args)))
  except:
    traceback.print_exc()
    pass
  return "\n".join(res)

#
#
def getAssignment(funcdef):
  res = []
  for v in funcdef.body:
    if isinstance(v, Assign):
      try:
        if v.targets[0].value.id == 'self':
          res.append(v.targets[0].attr)
      except:
        pass
  return res

def printMermaidHeader():
  header=[ "```mermaid", "---",
          "  config:",
          "    class:",
          "      hideEmptyMemberBox: true",
          "---",
          "classDiagram"
  ]
  
  return "\n".join(header)

def printMermaidFooter():
  footer=["```"]
  return "\n".join(footer)


def main():
  import sys
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    classlist = sys.argv[2:]

    basename=os.path.splitext(os.path.basename(filename))[0]
    tree = parseModule(filename)

    contents=[]
    ### Title & Variable
    contents.append("# %s" % os.path.basename(filename))
    contents.append("## Variables ")
    contents.append(printAssignList(tree))

    ### Functions
    contents.append("## Functions ")
    contents.append(printFunctionList(tree))

    ### Class diagram
    class_diagram = getClassTreeDiagram(tree, basename, classlist)
    if class_diagram:
      contents.append("## Clsses ")
      contents.append(printMermaidHeader())
      contents.append(class_diagram)
      contents.append(printMermaidFooter())

    ### Save to MD file
    DOC_ROOT="contents"
    save_contents("%s/%s.md" % (DOC_ROOT, basename), "\n".join(contents))

    clss=getClasses(tree)
    for klass in clss:
      info=getClassInfo(tree.body, klass)
      output_class_md("%s/%s" % (DOC_ROOT,basename), tree, klass, clss[klass],
              info['comment'])

  else:
    print("Usage: %s <filename>" % sys.argv[0])

if __name__ == '__main__':
    main()
