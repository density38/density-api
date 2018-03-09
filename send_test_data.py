import csv
import requests

with open('input_data/dpu_data.csv', newline='') as csvfile:
    data = csv.DictReader(csvfile)
    for row in data:
        json_payload = {
            "dpu_id": row['dpu_id'],
            "timestamp": row['timestamp'],
            "direction": row['direction']
        }
        r = requests.post('http://localhost:9090/v1/event/', json=json_payload)
        print("sending %s" % json_payload)
        if r.status_code != 200:
            print(r.text)
            exit()
print('finished sending test data')
