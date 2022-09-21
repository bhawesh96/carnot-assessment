import csv
import datetime
import json
import redis
from flask import Flask, make_response, jsonify
redis_cache = redis.Redis(host='54.163.216.242', port='6379', db=1)  # configure redis
app = Flask(__name__)

@app.route('/')
def home():
    """
    Home page
    """
    return make_response({'status': 'success', 'data': 'Server is up and running!'}, 200)

@app.route('/get_all_data')
def get_all_data():
    """
    Get all data from Redis
    """
    keys = redis_cache.keys('*')
    if len(keys) == 0:
        return make_response({'status': 'fail', 'err': 'No data found in Redis'}, 200)
    vals = list()
    for key in keys:
        vals.append(json.loads(redis_cache.get(key)))
    kv = zip(keys, vals)
    return make_response(jsonify({'status': 'success', 'data': json.dumps(kv)}), 200)

@app.route('/get_info/<string:id>')
def get_info(id):
    """
    Get device information
    :param id: device ID
    :return: Latest information of device
    """
    if not redis_cache.exists(id):
        return make_response(jsonify({'status': 'fail', 'err': 'ID does not exist'}), 200)
    val = json.loads(redis_cache.get(id))
    latest_entry = val[0]
    return make_response(jsonify(json.loads(latest_entry)), 200)

@app.route('/get_location/<string:id>')
def get_start_end_locations(id):
    """
    Get device location information
    :param id: device ID
    :return: Start and End - Latitude, Longitude tuple
    """
    if not redis_cache.exists(id):
        return make_response(jsonify({'status': 'fail', 'err': 'ID does not exist'}), 200)
    val = json.loads(redis_cache.get(id))
    start_entry = json.loads(val[0])
    end_entry = json.loads(val[-1])
    json_data = json.dumps({'start': (start_entry['lat'], start_entry['long']),
                            'end': (end_entry['lat'], end_entry['long'])})
    return make_response(jsonify({'status': 'success', 'data': json.loads(json_data)}), 200)

@app.route('/get_time_based/<string:id>/<string:start_time>/<string:end_time>')
def get_time_based_data(id, start_time, end_time):
    """
    Get device information based on Start and End time
    :param id: device ID
    :param start_time: start time in UTC format
    :param end_time: end time in UTC format
    :return: All the location points as list of latitude, longitude & time stamp
    """
    if not redis_cache.exists(id):
        return make_response(jsonify({'status': 'fail', 'err': 'ID does not exist'}), 200)
    entries = json.loads(redis_cache.get(id))
    device_info = list()
    try:
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    except Exception as e:
        return make_response(jsonify({'status': 'fail', 'err': 'Input timestamp is in wrong format'}), 200)
    if start_time > end_time:
        return make_response(jsonify({'status': 'fail', 'err': 'Start time should be less than end time'}), 200)
    for ent in entries:
        sts = datetime.datetime.strptime(json.loads(ent)['sts'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if start_time <= sts <= end_time:
            device_info.append([json.loads(ent)['lat'], json.loads(ent)['long'], json.loads(ent)['ts']])
        if sts > end_time:
            break
    if len(device_info) == 0:
        return make_response(jsonify({'status': 'success', 'data': 'No entry within these timestamps'}), 200)
    return make_response(jsonify({'status': 'success', 'data': device_info}), 200)

@app.route('/load_data')
def load():
    """
    Load data in Redis
    """
    redis_cache.flushdb()

    class Entry():
        def __init__(self, id, lat, long, ts, sts, speed):
            self.id = id
            self.lat = lat
            self.long = long
            self.ts = ts  # datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
            self.sts = sts  # datetime.datetime.strptime(sts, '%Y-%m-%dT%H:%M:%S.%fZ')
            self.speed = speed

    vals = dict()

    with open('datapoints.csv') as csvfile:
        myreader = csv.reader(csvfile, delimiter=',')
        next(myreader, None)
        for row in myreader:
            ent = Entry(row[0], row[1], row[2], row[3], row[4], row[5])
            if vals.get(ent.id) is None:
                vals[ent.id] = list()
            vals[ent.id].append(ent)

    for id in vals:
        vals[id].sort(key=lambda x: datetime.datetime.strptime(x.sts, '%Y-%m-%dT%H:%M:%S.%fZ'))

    class JSONEncoder(json.JSONEncoder):
        # override
        def default(self, obj):
            return json.dumps(obj.__dict__)

    for id in vals:
        vals[id] = JSONEncoder().encode(vals[id])
        redis_cache.set(id, vals[id])

    return make_response({'status': 'success', 'data': 'Data reloaded successfully'}, 200)

@app.errorhandler(500)
def generic_server_error(e):
    return make_response({'status': 'fail', 'data': str(e)}, 200)


if __name__ == "__main__":
    app.run(debug=False, port='8080', host='0.0.0.0')
