# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 15:19:15 2018
@author: [NikhilKadayinti, MakbulHussain]
"""

# =============================================================================
# imports the necesary libraries
# Reads from the topic "earth_before" and proces each event
# write the data to another topic "earth_after"
# =============================================================================

import faust
from kafka import KafkaProducer
import json
from datetime import datetime

"""
Takes in the event data and transforms 
1. makes the datetime feild and location feild to put in elastic search
time - in accordance with the Elastic recognizable format (iso format - datetime)
location - a list of lat and long values for Elastic 'geo-point' format
delete the unused feilds accordingly
"""

def make_data(event):
    date,time = event['Date'], event['Time']
    old_dtime = date + '-' + time
    readf = "%m/%d/%Y-%H:%M:%S"
    writef = "%Y/%m/%d %H:%M:%S"
    new_dtime = datetime.strptime(old_dtime, readf)
    new_dtime_str = new_dtime.strftime(writef)
    
    event['Location'] = [event.get('Longitude', 0), event.get('Latitude', 0)]
    event.update({"time":new_dtime_str})
    
    del event['Date']
    del event['Time']
    del event['Longitude']
    del event['Latitude']
    
    return event
    

# Register the Application as k2k_transform  and read from a topic
app = faust.App(
                'k2k_transform',
                broker='kafka://localhost:9092',
                value_serializer='raw',
                )

# Read from a topic  and initialise the producer to send data after transformation
before_topic = app.topic('earth_before', value_serializer = 'json')
producer = KafkaProducer(bootstrap_servers = "localhost:9092")

"""
process each event in the topic and tansform
send the transformed event data into anotehr topic for consumption
data is read from the topic as json/dictionary format
data is sent to teh topic as byte of strings - so the dumps and encode
"""

@app.agent(before_topic)
async def send_to_another(earth_data):
    async for msg in earth_data:
        #tempd = json.dumps(msg)
        transformed_data = make_data(msg)
        print (transformed_data["ID"], transformed_data['Type'])
        #print (type(tempd))
        producer.send('earth_after', json.dumps(transformed_data).encode('utf-8'))
        