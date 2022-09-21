import requests as req

base_url = 'http://54.163.216.242:8080'
# base_url = 'http://127.0.0.1:8080'
def get_latest_info():
    id = raw_input('Device ID: ')
    resp = req.get(base_url + '/get_info/{}'.format(id))
    print(resp.json())

def get_start_end_location():
    id = raw_input('Device ID: ')
    resp = req.get(base_url + '/get_location/{}'.format(id))
    print(resp.json())

def get_time_based_data():
    id = raw_input('Device ID: ')
    start_time = raw_input('Start time in UTC format: ')
    end_time = raw_input('End time in UTC format: ')
    resp = req.get(base_url + '/get_time_based/{}/{}/{}'.format(id, start_time, end_time))
    print(resp.json())

def get_all_data():
    resp = req.get(base_url + '/get_all_data')
    print(resp.json())

def reload_data():
    print('Reloading data in redis. Please wait')
    resp = req.get(base_url + '/load_data')
    print(resp.json())

def check_server():
    resp = req.get(base_url + '/')
    print(resp.json())

def exit_program():
    exit(0)

while(1):
    print('--------------------------------------')
    print('0. Check server')
    print('1. Get latest')
    print('2. Get start & end location')
    print('3. Get time based data')
    print('4. Get all data')
    print('8. Reload data in redis')
    print('9. Exit')
    inp = input()
    func_map = {
        0: 'check_server',
        1: 'get_latest_info',
        2: 'get_start_end_location',
        3: 'get_time_based_data',
        4: 'get_all_data',
        8: 'reload_data',
        9: 'exit_program'
    }
    locals()[func_map[inp]]()