import json
import os
import sys
import numpy as np
from functools import reduce

import leveldb
from flask import Flask, request, render_template, send_from_directory
from utils import tokenize_by_CJK_char

app = Flask(__name__)

db = leveldb.LevelDB("./db")

@app.route('/q', methods=['GET'])
def query():
    query = request.args.get("query")
    toks = tokenize_by_CJK_char(query)
    doc_list = []
    for t in toks:
        try:
            docs = db.Get(t.encode()).decode().split(",")
        except KeyError:
            print (f"Key {t} not found.")
            continue
        docs = [int(x) for x in docs]
        doc_list.append(docs)
    fnames = []
    if doc_list:
        docs = reduce(np.intersect1d, doc_list)
        for d in docs:
            fnames.append(db.Get(f"doc_{d}".encode()).decode())
    return json.dumps({"files": fnames}, ensure_ascii=False)


@app.route('/files/<path:filename>')
def send_file(filename):
    return send_from_directory("/",
                               filename, as_attachment=False)
