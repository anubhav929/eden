
fields = []
query = ""

count = -1;

def setfields(db):
    global fields
    fields.append(db["org_organisation"].ALL)
    print "here"

def mapping(rows):
    global count
    count = count + 1
    return rows[count]["id"]
