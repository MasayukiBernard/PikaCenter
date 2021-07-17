from win32api import GetMonitorInfo, MonitorFromPoint
import math

def generate_tk_geometry(window_size):
    return window_size['width'] + "x" + window_size['height'] + calculate_unused_screen_area(window_size)

def get_monitor_actual_area():
    work_area = GetMonitorInfo(MonitorFromPoint((0,0))).get("Work")
    return {'width': work_area[2], 'height': work_area[3]}

# Currently a windows-only solution
def calculate_unused_screen_area(window_size):
    # window_size: dictionary
    # ex: {'width': 800, 'height': 450}

    monitor_size = get_monitor_actual_area()

    diff_size = {
        'width': int(math.ceil((int(monitor_size['width']) - int(window_size['width'])) / 2)), 
        'height': int(math.ceil((int(monitor_size['height']) - int(window_size['height'])) / 2))
    }

    if diff_size['width'] < 0:
        diff_size['width'] = 0
    if diff_size['height'] < 0:
        diff_size['height'] = 0
    
    
    return "+"+str(diff_size['width'])+"+"+str(diff_size['height'])

def change_window_status(window_status_var, key, status):
    window_status_var[key] = status

def create_pretty_numerical(numeric):
    stripped_zeros = ('%.24f' % numeric).rstrip('0').rstrip('.')
    return "{:,}".format(int(stripped_zeros))

def remove_non_integer(string):
    return ''.join(filter(str.isdigit, string))