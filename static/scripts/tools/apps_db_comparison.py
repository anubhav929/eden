# This script compares the db schema of 2 eden apps to tell the differences 
#
# Just run the script with 3 necessary arguments in this order 
#1.WEB2PY_PATH 
#2.OLD_APP
#3.NEW_APP
# i.e python applications/eden/static/scripts/tools/apps_db_comparison.py  /home/web2py  eden_old  eden_new
#
#This script also has an test script that makes 2 new web2py apps to compare
#Just run the test script to compare
#i.e python applications/eden/tests/dbmigration TestScript.py


import os
import sys
import copy
import subprocess

"""
SETTING VARIABLES
"""
WEB2PY_PATH = sys.argv[1]
if not 'WEB2PY_PATH' in os.environ:
    os.environ['WEB2PY_PATH'] = WEB2PY_PATH

NEW_APP = sys.argv[3]
OLD_APP = sys.argv[2]
NEW_PATH = "%s/applications/%s" % (os.environ['WEB2PY_PATH'], NEW_APP)
OLD_PATH = "%s/applications/%s" % (os.environ['WEB2PY_PATH'], OLD_APP)


"""
WE ARE LOADING THE 2 ENVIRONMENTS WITH ALL THERE MODELS
"""

os.chdir(os.environ['WEB2PY_PATH'])
sys.path.append(os.environ['WEB2PY_PATH'])


from gluon.custom_import import custom_import_install
custom_import_install(os.environ['WEB2PY_PATH'])
from gluon.shell import env
from gluon import DAL, Field

new_env = env(NEW_APP, c=None, import_models=True)
d = globals().copy()
d.update(**new_env)
new_str ='''
try:
    s3db.load_all_models()
except NameError:
    print "s3db not defined"
new_db = db
'''
exec new_str in d, locals()

d.clear()

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

"""
*****************************************************

Gets The Table and fileds and their constraints which are
stored the above dict . It gets the following properties of the fields
1.not null
2.unique
3.length
4.type
5.foreign key constarints

******************************************************
"""
old_database = {}
new_database = {}
database = {}  #buffer

def get_tables_fields(db):
    tables = db.tables
    for table in tables:
        database[table] = {}
        database[table]['id'] = str(db[table]['_id']).split('.')[-1]
        fields = db[table]['_fields']
        for field in fields:
            database[table]['field_'+field]= {}
            database[table]['field_'+field]['type'] = db[table][field].type
            database[table]['field_'+field]['notnull'] = db[table][field].notnull
            database[table]['field_'+field]['unique'] = db[table][field].unique
            database[table]['field_'+field]['length'] = db[table][field].length
        for table in database.keys():
            database[table]['refrences'] = []
            database[table]['referenced_by'] = []

def get_foriegn_key(db):
    tables = db.tables
    for table in tables:
        database[table]['referenced_by'] = db[table]['_referenced_by'] #needed for ondelete action
        tables_referenced = db[table]['_referenced_by']
        for table_referenced in tables_referenced:
            database[table_referenced[0]]['refrences'].append(str(table))   

traversed = []


get_tables_fields(old_db)
get_foriegn_key(old_db)
old_database = copy.deepcopy(database)

database = {}

get_tables_fields(new_db)
get_foriegn_key(new_db)
new_database = copy.deepcopy(database)

"""
Get the topological order in traversed
"""
def intersect(a, b):
    return list(set(a) & set(b))

def union(a, b):
    return list(set(a) | set(b))

def topo_sort():
    while len(set(traversed)) != len(union(old_database.keys(),new_database)):
        for table in old_database.keys():
            if table not in traversed and len(intersect(old_database[table]['referenced_by'],traversed)) == 0:
                traversed.append(table)
        for table in new_database.keys():
            if table not in traversed and len(intersect(new_database[table]['referenced_by'],traversed)) == 0:
                traversed.append(table)

topo_sort()
#print traversed
#print "TOPO Order = ",traversed

"""
CHANGES SCRIPT
"""

change = {}

change["appeared"] = []
change["disappeared"] = []
tables_disappeared = []
tables_appeared = []

"""
DETECTING THE CHANGE IN TABLES , RENAMING , ADDING OR DELETING FIELDS
"""
for table in traversed:
    old_field = []
    change[table] = {}
    change[table]["appeared"] = []
    change[table]["disappeared"] = []
    if table in old_database.keys():
        for field in old_database[table].keys():
            if field.find("field_") >= 0:
                old_field.append(field)
        if table in new_database.keys():
            for field in new_database[table].keys():
                if field.find("field_") < 0:
                    continue
                else:
                    if field not in old_field:
                        change[table]["appeared"].append(field)
                    else:
                        old_field.remove(field)
            change[table]["disappeared"].extend(old_field)
        else: 
            tables_disappeared.append(table)
    else:
        tables_appeared.append(table)
        
"""
GENERATING REPORTS OF THE CHANGES
"""

print "\nTables Appeared =",tables_appeared
print "\nTables Disappeared =",tables_disappeared

for table in traversed:
	if len(change[table]["appeared"]) > 0:
		print "table =", table , "changes appeared = ",change[table]["appeared"] 
	if len(change[table]["disappeared"]) > 0:
		print "table =", table , "changes disappeared = ",change[table]["disappeared"]
