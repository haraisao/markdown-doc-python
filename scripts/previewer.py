#!/usr/bin/python3
# -*- code: UTF-8 -*-
import os
import sys
from flask import Flask, render_template, session, request, redirect, jsonify, abort
import glob
import markdown
import traceback
from markdown_include.include import MarkdownInclude

#################
#
PORT='8080'
CONTENTS_DIR=os.path.join(os.path.dirname(__file__),'contents')
TEMPLATE_ROOT=os.path.join(os.path.dirname(__file__), 'template')
app=Flask(__name__,  template_folder=TEMPLATE_ROOT, static_folder=None)
app.config['JSON_AS_ASCII'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

################
#
def load_contents(fname):
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            res = f.read()
            return res
    except:
        traceback.print_exc()
        pass 
    return ""

def save_contents(fname, content):
    try:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
    except:
        return traceback.format_exc()
    return "OK"

def load_binary_contents(fname):
    try:
        with open(fname, 'rb') as f:
            res = f.read()
            return res
    except:
        traceback.print_exc()
        pass 
    return ""

def save_binary_contents(fname, content):
    try:
        with open(fname, 'wb') as f:
            f.write(content)
    except:
        return traceback.format_exc()
    return "OK"

def gen_ul_list(files):
    res = "<ul>"
    for f in files:
        fname = get_filename(f)
        res += "<li><a href=\"%s\">%s</a></li>" % (fname, fname)
    res += "</ul>"
    return res

def getFileList(dirname):
  res=[]
  f_list = os.listdir(dirname)
  for name in f_list:
    fname = os.path.join(dirname, name)
    if os.path.isfile(fname):
      res.append(name)
    elif os.path.isdir(fname) or os.path.islink(fname):
      res.append((fname, getFileList(fname)))
      
  return res

def mkFileList(flist, top_dir="", top_org="", depth=0, recursive=False):
  res = ' '*depth + "<ul>\n"
  for f in flist:
    if type(f) is str:
      fname=os.path.splitext(f)[0]
      url=os.path.join(top_dir[len(top_org):],fname)
      res += ' '*(depth+2) + '<li><span class="file"><a href="%s">%s</a></span> </li>\n' % (url, fname)
    else:
      if recursive:
        res += ' '*(depth+2) + '<li> <span class="folder">%s</span>/\n' % os.path.split(f[0])[-1]
        res += ' '*depth + mkFileList(f[1], f[0], top_org, depth+2)
        res += ' '*(depth+2) + "</li>\n" 
  res += ' '*depth + "</ul>\n"
  return res

def get_filename(pth):
    return pth[len(CONTENTS_DIR)+1:-len('.md')]

def convert_markdown(name, dirname=""):
    filename=os.path.join(CONTENTS_DIR, dirname, name+".md")
    print(filename)
    if os.path.exists(filename) :
        content=load_contents(filename)
        markdown_include = MarkdownInclude(
          configs={'base_path':'contents/', 'encoding': 'utf-8'}
        )
        html_content = markdown.markdown(content,
                extensions=['markdown_mermaidjs',
                    'fenced_code', 'md_in_html', 'def_list', 'attr_list',
                    markdown_include])
        return render_template('contents.tmpl', 
                title=name, dirname=dirname, content=content, html=html_content)
    else:
        return load_contents(os.path.join(os.path.dirname(__file__), 'no_file.html'))
###################
#
@app.route('/', methods=["GET"])
def index():
    #files=glob.glob(os.path.join(CONTENTS_DIR,"**/*.md"), recursive=True )
    #flist=gen_ul_list(files)

    lst = getFileList(CONTENTS_DIR)
    flist=mkFileList(lst, CONTENTS_DIR, CONTENTS_DIR)
    contents = render_template('index.tmpl', files=lst, file_list=flist)
    return contents
    
@app.route('/<string:name>')
def get_doc(name="index"):
    return convert_markdown(name)

@app.route('/<string:dirname>/<string:name>')
def get_doc2(dirname="", name="index"):
    if dirname in ["css", "js"]:
        return load_contents(os.path.join(os.path.dirname(__file__),dirname, name))
    elif dirname in ["images"]:
        return load_binary_contents(os.path.join(os.path.dirname(__file__),dirname, name))
    return convert_markdown(name, dirname)

@app.route('/<string:module>/<string:dirname>/<string:name>')
def get_doc3(module="", dirname="", name="index"):
    pth = os.path.join(module, dirname)
    return convert_markdown(name, pth)
    
@app.route('/preview', methods=["POST", "GET"])
def rest_preview():
    if request.method == 'GET':
        return render_template('preview.tmpl', data="")
    try:
        upload_files = request.files.getlist('uploadFiles')

        content = upload_files[0].stream.read().decode()
        if content:
            html_content = markdown.markdown(content, extensions=['markdown_mermaidjs'])
            return render_template('preview.tmpl', data=html_content)
        else:
            return "Invalid file", 400
    except:
        import traceback
        traceback.print_exc()
        return render_template('preview.tmpl', data="")

@app.route('/rest/save', methods=["POST"])
def rest_save():
    name = request.json['name']
    dirname = request.json['dirname']
    content = request.json['content']
    filename=os.path.join(CONTENTS_DIR, dirname, name+".md")
    save_contents(filename, content)
    
    return convert_markdown(name, dirname)

@app.route('/upload_image', methods=["POST"])
def rest_upload_image():
    msg=""
    try:
        upload_files = request.files.getlist('uploadFiles')

        content = upload_files[0].stream.read()
        if content:
            filename=upload_files[0].filename
            msg=save_binary_contents(os.path.join(os.path.dirname(__file__), 'images', filename), content)
    except:
        msg = traceback.format_exc()
    response={
        'result': msg
    }
    #return jsonify(response)
    return index()

#
#   M A I N 
if __name__=='__main__':
    server_port = os.environ.get('PORT', PORT)
    app.run(debug=False, port=server_port, host='0.0.0.0')
