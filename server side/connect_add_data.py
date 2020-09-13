#!/usr/bin/python
import psycopg2
import pandas as pd
from config import config
from datetime import datetime,date

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
        
	# execute the statements
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
        print('Inserting data into label_types...')
	#add the data to label_types
        query = """INSERT INTO label_types (comments, label_name, label_id) VALUES (\'Positive feeling\', \'positive\', \'1\');
                   INSERT INTO label_types (comments, label_name, label_id) VALUES (\'Negative feeling\', \'negative\', \'0\');
                   INSERT INTO label_types (comments, label_name, label_id) VALUES (\'Neutral feeling\', \'neutral\', \'2\');"""
        cur.execute(query)
	#adding the IMDB DATASET to the database.
        print('Reading data from IMDB File...')	
        df = pd.read_csv('IMDB Dataset.csv')
        data = [(index, content['review'], date.today()) for index, content in df.iterrows()]
        query1 = 'INSERT INTO data_input(text_id,content,content_date) VALUES(%s,%s,%s)'
        query2 = 'INSERT INTO data_labeling(text_id,label_id,labeling_timestamp) VALUES(%s,%s,%s)'
        print('Inserting IMDB DATASET into the database...')
        cur.executemany(query1,data)
        data = []
        for index, content in df.iterrows():
            x = 2
            if content['sentiment'] == 'positive':
                x = 1
            elif content['sentiment'] == 'negative':
                x = 0
            data.append((index, x, datetime.now()))
        cur.executemany(query2,data)
        print('Inserting data done.')
	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    connect()