# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 15:19:15 2018
@author: [NikhilKadayinti, MakbulHussain]
"""
# =============================================================================
# imports the necesary libraries
# Reads from the topic "earth_after" and sends each event into Elastic
# write the data to another topic "earth_after"
# =============================================================================

from kafka import KafkaConsumer
from json import loads
from elasticsearch import Elasticsearch

"""
for every event in the topic, send teh data to Elastic search
index = earth, doc_type = earth_quakes
mapping: location:geo_point
"""

def to_elastic(es, consumer):
    
    for event in consumer:
        try:
            data_point = loads(event.value)
        except Exception:
            continue
        
        #tempd.update({"timemy":datetime.utcnow()})
        print (event.timestamp, event.offset)
        #print (data_point)
        #print (type(data_point))
        es.index(index = 'earth', doc_type = 'earth_quakes', body = data_point)   
    
if __name__ == '__main__':
    
    """
    Initialise the Elastic search and consumer subscribe to topic accordingly
    """    
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    
    consumer = KafkaConsumer('earth_after',
                             bootstrap_servers=['localhost:9092'],
                             auto_offset_reset='latest',
                             enable_auto_commit=True)
    to_elastic(es, consumer)

