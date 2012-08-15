
from migration_helping_methods import *

def list_field_to_reference(web2py_path, app , new_table_name , new_list_field , list_field_name , old_table_id_field , old_table):
    set_globals(web2py_path,app)
    creating_new_table(new_table_name , new_list_field , list_field_name , old_table_id_field , old_table)
    fill_the_new_table(new_table_name , new_list_field , list_field_name , old_table_id_field , old_table )

def migrating_to_unique_field(web2py_path, app ,field_to_update,changed_table,list_of_tables_for_query):
    set_globals(web2py_path,app)
    import mapping_function
    temp_db = adding_new_fields(field_to_update,changed_table)
    set_db(adding_tables_temp_db(temp_db,list_of_tables_for_query))
    update_with_mappings(changed_table,field_to_update,mapping_function)

def migration_renaming_table(web2py_path, app ,old_table_name,new_table_name):
    set_globals(web2py_path,app)
    renaming_table(old_table_name,new_table_name)

def migration_renaming_field(web2py_path, app ,table_name,old_field_name,new_field_name,attributes_to_copy = None):
    set_globals(web2py_path,app)
    renaming_field(table_name,old_field_name,new_field_name,attributes_to_copy)
