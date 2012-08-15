import migration_scripts

def list_field_to_reference():
    migration_scripts.set_globals("/home/web2py","eden")
    new_table_name = "sector_id_reference"
    new_list_field = list_field_name = "sector_id"
    old_table_id_field = "id"
    old_table = "org_organisation"
    migration_scripts.creating_new_table(new_table_name , new_list_field , list_field_name , old_table_id_field , old_table)
    migration_scripts.fill_the_new_table(new_table_name , new_list_field , list_field_name , old_table_id_field , old_table )

def renaming_field():
    migration_scripts.set_globals("/home/web2py","eden")
    attributes_to_copy = ["type","length","default","required","requires","ondelete","notnull","unique",
            "uploadfield","widget","label","comment","writable","readable","update","authorize",
            "autodelete","represent","uploadfolder","uploadseparate","uploadfs","compute","custom_store",
            "custom_retrieve","custom_retrieve_file_properties","custom_delete","filter_in","filter_out"]        
    migration_scripts.renaming_field("pr_person","first_name","renamed_person4",attributes_to_copy,dbengine)

def renaming_field():
    migration_scripts.set_globals("/home/web2py","eden")
    migration_scripts.renaming_table("vehicle_vehicle","rename_vehicle")

def adding_new_field():
    migration_scripts.set_globals("/home/web2py","eden")
    field_to_update = "NewField"
    changed_table = "org_organisation"
    import mapping_function
    temp_db = migration_scripts.adding_new_fields(field_to_update,changed_table)
    db = migration_scripts.adding_tables_temp_db(temp_db,["org_organisation_type","org_sector"])
    migration_scripts.update_with_mappings(changed_table,field_to_update,mapping_function)


    
