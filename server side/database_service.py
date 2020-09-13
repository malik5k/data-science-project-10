#!/usr/bin/python
import psycopg2
import json
from config import config

conn = None
cur = None

def get_data_count(label_name, count = None):
    no_error = True
    serialized_data = None
    if count != None:
        try:
            cur.execute('SELECT * FROM data_labeling FETCH FIRST %s ROWS ONLY;', (count,))
        except ValueError:
            print('Error: Invalid parameter (count)')
            no_error = False
            pass
    else:
        cur.execute('SELECT * FROM data_labeling;')
    if label_name == 'negative' or label_name == 'positive':
        lable_id = 0 if label_name == 'negative' else 1
    else:
        print('Error: Invalid parameter (label_name)')
        no_error = False
    if no_error:
        data = [record[1] for record in cur if record[1] == lable_id]
        serialized_data = json.dumps(len(data))

    return serialized_data


def get_data(count, sort_order):
    no_error = True
    serialized_data = None
    if count != None:
        try:
            if sort_order == 'ASC':
                cur.execute("""SELECT  data_input.content, data_labeling.label_id 
				FROM data_input 
				INNER JOIN data_labeling
				ON data_input.text_id = data_labeling.text_id
				ORDER BY content_date asc FETCH FIRST %s ROWS ONLY;""", (count,))
            else:
                cur.execute("""SELECT  data_input.content, data_labeling.label_id 
				FROM data_input 
				INNER JOIN data_labeling
				ON data_input.text_id = data_labeling.text_id
				ORDER BY content_date desc FETCH FIRST %s ROWS ONLY;""", (count,))
        except ValueError:
            print('Error: Invalid parameter (count)')
            no_error = False
            pass
    if no_error:
        data = [record  for record in cur]
        serialized_data = json.dumps(data)

    return serialized_data


def connect():
    """ Connect to the PostgreSQL database server """
    try:
        # read connection parameters
        params = config()
        global conn
        global cur
        conn = psycopg2.connect(**params)
        # create a cursor
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def close_conn():
    if conn is not None:
        # close the communication with the PostgreSQL
        cur.close()
        conn.commit()
        conn.close()
        print('DB_Connection Closed')

# execute the connect() method only when the module is imported.
if __name__ != '__main__':
    connect()