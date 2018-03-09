from flask import Flask, request, jsonify
from influxdb import InfluxDBClient

import os

app = Flask(__name__)

client = InfluxDBClient(os.environ['INFLUXDB_HOST'], 8086, 'root', 'root', 'density')

# uncomment below if you need to drop the database
# client.drop_database('density')

try:
    print('creating density database')
    client.create_database('density')
except:
    print('database already created')

# this is mostly wrong. we can determine orientation using doorway identifier
# for each space. no need for the flipped boolean.
spaces = {
    "space_a": [{'dpu_id': 283, 'flipped': False},
                {'dpu_id': 423, 'flipped': False}],
    "space_b": [{'dpu_id': 423, 'flipped': True}]
}

# doorway can change over time, and should be saved with each reading.
# with this, we can correctly count over time with each doorway as our
# key, not using the dpu_id directly.
doorways = {
    "doorway_z": ["space_a", "space_b"],
    "doorway_x": ["space_a", "outside"]
}

@app.route('/')
def home():
    return 'API is available at /v1/pass_event'

@app.route('/v1/room_count/<space>', methods=['GET'])
def room_count(space):
    number = 0
    for dpu in spaces[space]:
        data = client.query("SELECT SUM(direction) FROM walk_event WHERE dpu_id = '%i';" % dpu['dpu_id'])
        if dpu['flipped']:
            number -= list(data.get_points())[0]['sum']
        else:
            number += list(data.get_points())[0]['sum']
    return jsonify({"human_count": max(number, 0)})

@app.route('/v1/event/', methods=['POST'])
def pass_event():
    values = request.json

    json_body = [
        {
            "measurement": "walk_event",
            "time": values['timestamp'],
            "tags": {
                "dpu_id": int(values['dpu_id'])
            },
            "fields": {
                "direction": int(values['direction'])
            }
        }
    ]

    client.write_points(json_body)
    data = client.query("select direction from walk_event;")
    
    return "Result: {0}".format(data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=80)
