

def fields(db):    
    fields = []
    fields.append(db["org_organisation"].ALL)
    return fields

def query(db):    
    query = db.org_organisation.organisation_type_id == db.org_organisation_type.id
    return query

def mapping(row):
    return row["id"]
