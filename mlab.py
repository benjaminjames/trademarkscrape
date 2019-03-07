# -*- coding: utf-8 -*-


from pymongo import MongoClient


# pymongo tutorial: https://api.mongodb.com/python/current/tutorial.html


def getDb(db_name):
    """
    Example usage:
    db = mlab.get_db(db_name,,True)
    ! Third value refers to replicaSet
    """

    mlab_URIs = {
        'app_data': 'mongodb://benjaminknudson:Asclepius*8@ds139569-a0.mlab.com:39569/',
        'skunkworks': 'mongodb://benjaminknudson:Asclepius*8@ds117860-a0.mlab.com:17860/',
        'mastercard': 'mongodb://benjaminknudson:Asclepius*8@ds131841-a0.mlab.com:31841/',
        'mc-project-test' : 'mongodb://localhost:27017'
    }

    creds = mlab_URIs[db_name]
    repSetId = creds.split('@')[-1].split('-')[0]

    if db_name == 'mc-project-test':
        mongo_client = MongoClient(creds)
    else:
        mongo_client = MongoClient(creds + db_name, replicaSet='rs-%s' % repSetId)

    db = mongo_client[db_name]

    return db  # then access collection: db.test_collection


def get_collection(db_name, collection_name, replicaSetBoolean):
    """
    Example usage:
    coll = mlab.get_collection(db_name,collection_name,True)
    ! Third value refers to replicaSet
    """

    mlab_URIs = {
        'app_data': 'mongodb://benjaminknudson:Asclepius*8@ds139569-a0.mlab.com:39569/',
        'skunkworks': 'mongodb://benjaminknudson:Asclepius*8@ds117860-a0.mlab.com:17860/',
        'mastercard': 'mongodb://benjaminknudson:Asclepius*8@ds131841-a0.mlab.com:31841/'
    }

    creds = mlab_URIs[db_name]
    repSetId = creds.split('@')[-1].split('-')[0]

    if replicaSetBoolean:
        mongo_client = MongoClient(creds + db_name, replicaSet='rs-%s' % repSetId)
    else:
        mongo_client = MongoClient(creds + db_name)

    db = mongo_client[db_name]
    # print db.collection_names()

    coll = db[collection_name]

    return coll


def getDbSchema(db_name,exclusion_list):
    db = getDb(db_name)

    fields = set()

    collections = db.collection_names()

    count = 1

    for coll in collections:

        print 'Processing %s of %s...' % (count,len(collections))
        count += 1

        if '.' not in coll and coll not in exclusion_list:
            collection = db[coll]

            for doc in collection.find({},limit=1000):
                for key in doc.keys():
                    if len(key) > 2:
                        fields.add(key.upper())

    return list(fields)


def mcdb(collection_name):
    creds = 'mongodb://benjaminknudson:Asclepius*8@ds131841-a0.mlab.com:31841/'
    repSetId = creds.split('@')[-1].split('-')[0]

    mongo_client = MongoClient(creds + 'mastercard', replicaSet='rs-%s' % repSetId)
    # mongo_client = MongoClient(creds + 'mastercard')

    db = mongo_client['mastercard']
    coll = db[collection_name]

    return coll


def fieldContains(field, term):
    fieldContainsQuery = {
        field: {
            "$regex": ".*\Q%s\E.*" % (term),
            "$options": "i"
        }
    }
    return fieldContainsQuery


def insert_if_new(collection, unique_key, doc):
    # unique_key ex: URL or app_id
    # doc is a python dictionary
    doc_exists = collection.find_one({unique_key: doc[unique_key]})
    if not doc_exists:
        collection.insert_one(doc)
        print "DATABASED: %s" % doc[unique_key]
        return True


def update_doc(collection, doc):
    update = collection.update({'_id': doc['_id']}, {"$set": doc}, upsert=False)
    if '_id' in update.keys():
        return True


def upsert_doc(collection, doc):
    # updates doc if doc exists, inserts doc if not
    upsert = collection.update({'_id': doc['_id']}, {"$set": doc}, upsert=True)
    if '_id' in upsert.keys():
        return True


def count_fieldname_matches(collection, fieldname, fieldvalue):
    res = collection.count({fieldname: fieldvalue})
    return res


def count_text_matches(collection, fieldname, text):
    # Example: coll.remove({'app_title':'Downloading..'})
    criteria = {
        fieldname: {
            '$regex': '.*\Q{}\E.*'.format(text),
            '$options': 'i'
        }
    }
    counts = collection.count(criteria)
    return counts


def migrate(source_db_name, source_coll_name, dest_db_name, dest_coll_name):
    # m.migrate('app_data','alexa_top_sites',True,'mastercard','alexa_top_sites',False)
    source = get_collection(source_db_name, source_coll_name, True)
    destination = get_collection(dest_db_name, dest_coll_name, True)

    source_docs = [x for x in source.find({})]
    print 'TRANSFERRING %s DOCS...' % len(source_docs)
    destination.insert_many(source_docs)
    print 'TRANSFERRED %s DOCS...' % destination.count({})

    if source.count({}) == destination.count({}):
        print "DELETING SOURCE DOCS..."
        source.remove({})
    else:
        print "MIGRATION ERROR."


def getMatchingDocs(collection, fieldname, keyword):
    query_json = {
        fieldname: {
            '$regex': '.*\Q%s\E.*' % keyword,
            '$options': 'i'
        }
    }

    data = list(collection.find(query_json))

    return data


def remove_all_matching_docs(collection, fieldname, text):
    # Example: coll.remove({'app_title':'Downloading..'})
    criteria = {
        fieldname: {
            '$regex': '.*\Q{}\E.*'.format(text),
            '$options': 'i'
        }
    }
    collection.remove(criteria)


def delete_field_from_collection(collection, query, fieldname):
    collection.update(query, {'$unset': {fieldname: 1}}, multi=True)


def text_search(collection, fieldname, text):
    cursor = collection.find({
        fieldname: {
            '$regex': '.*\Q{}\E.*'.format(text),
            '$options': 'i'
            }
        }
    )
    return cursor


"""
WIP: ObjectID to Timestamp conversion
collection.update_many({},{'created_date':doc['_id'].generation_time.strftime("%m-%d-%Y %H:%M:%S")},upsert=False)
"""
