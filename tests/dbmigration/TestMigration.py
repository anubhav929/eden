import os
import sys
import subprocess

WEB2PY_PATH = "/home/web2py"
OLD_APP = "eden3"
changed_table = "org_organisation"

os.chdir(WEB2PY_PATH)
sys.path.append(WEB2PY_PATH)

from gluon.custom_import import custom_import_install
custom_import_install(WEB2PY_PATH)
from gluon.shell import env
from gluon import DAL, Field

old_env = env(OLD_APP, c=None, import_models=True)
old_str ='''
try:
    s3db.load_all_models()
except NameError:
    print "s3db not defined"
old_db = db
'''
d = globals().copy()
d.update(**old_env)
exec old_str in d, locals()

d.clear()

for a in range(10):
    old_db[changed_table].insert(name = "test_%s" %(str(a)), type = a%5 , uuid = "%s%s" %(old_db[changed_table]["uuid"].default,str(a)))

old_db.commit()
subprocess.call("python %s/applications/eden/static/scripts/tools/miration.py" % \
         (WEB2PY_PATH) , shell =True )

"""
Retreiving Data
"""
