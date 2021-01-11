import pymongo
import time

class DatabaseConnection(object):
    def __init__(self, project_name, host, port, user, password):
        # todo get ip and port from somewhere else
        client = pymongo.MongoClient('{}:{}'.format(host, port))
        client.the_database.authenticate(user, password, source='admin')
        self.db = client[project_name]

    def read_many(self, collection_name, _id, fields):
        """ Read the value of field @field of the document with _id @_id
            in collection @collection_name.

        :param collection_name: name of the collection.
        :param _id: _id of the document to be read.
        :param fields: fields to be read.
        :return: value of the fields read or ValueError.
        """
        aggregate_fields = {f:"$"+f for f in fields}
        collection = self.db[collection_name]
        cursor = collection.aggregate([
            {"$match": {"_id": _id}},
            {"$group": {"_id": aggregate_fields}}
        ])
        items = list(cursor)
        if len(items) < 1:
            raise ValueError("No document with the given id "
                             "{} was found.".format(_id))
            return None
        elif len(items) > 1:
            raise ValueError("More than one document with the given id "
                             "{} was found.".format(_id))
            return None
        else:
            item = items[0]['_id']
            return item


    def read_one(self, collection_name, _id, field):
        """ Read the value of field @field of the document with _id @_id
            in collection @collection_name.

        :param collection_name: name of the collection.
        :param _id: _id of the document to be read.
        :param field: field to be read.
        :return: value of the field read or ValueError.
        """
        collection = self.db[collection_name]
        cursor = collection.aggregate([
            {"$match": {"_id": _id}},
            {"$group": {"_id": "$" + field}}
        ])
        items = list(cursor)
        if len(items) < 1:
            raise ValueError("No document with the given id "
                             "{} was found.".format(_id))
            #print("No document with the given id {} was found.".format(_id))
            return None
        elif len(items) > 1:
            raise ValueError("More than one document with the given id "
                             "{} was found.".format(_id))
            #print("No document with the given id {} was found.".format(_id))
            return None
        else:
            item = list(items)[0]['_id']
            # print(item)
            #self.write_one(collection_name, _id, field, item)
            return item

    def write_many(self, collection_name, _id, fields, values):
        """ If the a document with _id @_id exists in collection
            @collection_name, update its field @field with value @value.
            Otherwise, insert a new document to the collection with given _id
            and field, value pair.

        :param collection_name: name of the collection.
        :param _id: _id of the document to be written to.
        :param fields: fields to be written to.
        :param values: values to be written to fields.
        :return: return True for success, False for failure.
        """
        collection = self.db[collection_name]
        cursor = collection.find(
            {"_id": _id},
        )
        id_exist = len(list(cursor)) == 1
        zip_vals = dict(zip(fields, values))
        self._new_update_many(collection_name, _id, fields, values)

        item = self.read_many(collection_name, _id, fields)
        for fld in fields:
        	assert item[fld] == zip_vals[fld], "mismatch between what was written to, and read from the mongo db. MongoDB write failed"

    def write_one(self, collection_name, _id, field, value):
        """ If the a document with _id @_id exists in collection
            @collection_name, update its field @field with value @value.
            Otherwise, insert a new document to the collection with given _id
            and field, value pair.

        :param collection_name: name of the collection.
        :param _id: _id of the document to be written to.
        :param field: field to be written to.
        :param value: field to be written.
        :return: return True for success, False for failure.
        """
        collection = self.db[collection_name]
        cursor = collection.find(
            {"_id": _id},
        )
        id_exist = len(list(cursor)) == 1
        
        for _ in range(5):
            # re-try writing with confirmation for 5 times
            self._new_update_one(collection_name, _id, field, value)

            item = self.read_one(collection_name, _id, field)

            if item == value:
                return True
            else:
                # re-try every 0.5 second
                time.sleep(0.5)

        assert 0, "MongoDB write failed!"


    def _new_update_many(self, collection_name, _id, fields, values):
        collection = self.db[collection_name]
        update_vals = dict(zip(fields, values))
        cursor = collection.update_many(
                               {"_id": _id},
                               {"$set" :update_vals},
                               upsert=True
                               )
        return cursor


    def _new_update_one(self, collection_name, _id, field, value):
        collection = self.db[collection_name]
        cursor = collection.update_one(
                               {"_id": _id},
                               {"$set" :{field: value}},
                               upsert=True
                               )
        return cursor
    

    def read_all(self, collection_name, field):
        return self.db[collection_name].distinct(field)
