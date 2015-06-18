#!/usr/bin/env python

import os, sys
import pickle
from pprint import pprint
import subprocess
import fp

try:
    import json
except ImportError:
    import simplejson as json



# path to codegen prg
_codegen_path = "codegen"
# track_id -> filepath dictionary
_tracks = {}
# echoprint database
## managed by fp module

# Call codegen prg, return json object with result.
def codegen(filename, start=-1, duration=-1):
#    if not os.path.exists(_codegen_path):
#        raise Exception("Codegen binary not found.")

    command = _codegen_path + " \"" + filename + "\" " 
    if start >= 0:
        command = command + str(start) + " "
    if duration >= 0:
        command = command + str(duration)

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (json_block, errs) = p.communicate()

    try:
        return json.loads(json_block)
    except ValueError:
        #logger.debug(
        print "No JSON object came out of codegen: error was %s" % (errs)
        return None

# Load echoprint into "local" database.
def local_ingest_json(json):
    fp_codes = []
    #fp.local_load("disk.pkl")

    if len(json):
	track_id = fp.new_track_id()
	code_str = fp.decode_code_string(json[0]["code"])
        meta = json[0]["metadata"]
        l = meta["duration"] * 1000
        a = meta["artist"]
        r = meta["release"]
        t = meta["title"]
        v = meta["version"]
        fp_codes.append({"track_id": track_id, "fp": code_str, "length": str(l), "codever": str(round(v, 2)), "artist": a, "release": r, "track": t})
    fp.ingest(fp_codes, local=True)
    
    #fp.local_save("disk.pkl")
    return track_id

# codegen a file, and load results into database.
def local_ingest_file(path):
    json = codegen(path)
    if not json or "error" in json[0]:
	pass
    else:
	id = local_ingest_json(json)
	_tracks[id] = path

# codegen all recognized files, and load results into database.
def local_ingest_folder(folder_path):
    for subdir, dirs, files in os.walk(folder_path):
	for file in files:
	    f = os.path.join(subdir, file)
	    print f
	    local_ingest_file(f)



# set requested dir
proj_root = os.getcwd()
if len(sys.argv) > 1:
    if not not sys.argv[1]:
	proj_root = sys.argv[1]

echoprint_dir = os.path.join(proj_root, "_echoprint")

local_ingest_folder(proj_root)

# Save databases to Python "pickle" format.
try:
    os.mkdir(echoprint_dir)
except:
    pass
fp.local_save(os.path.join(echoprint_dir, "echoprnt.pkl"))
filename = os.path.join(echoprint_dir, "echotrks.pkl")
disk = open(filename,"wb")
pickle.dump(_tracks,disk)
disk.close()
