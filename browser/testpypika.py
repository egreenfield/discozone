from pypika import MySQLQuery as Query, Table, Field

pairs = {
    "id":"some_id",
    "comments":"some_comments"
}

t = Table("Dance")
q = Query.into(t).columns("x",*(pairs.keys())).insert(1,*pairs.values())
for aKey in pairs:
    q = q.on_duplicate_key_update(aKey,pairs[aKey])
print(f'query is:  "{str(q)}"')
