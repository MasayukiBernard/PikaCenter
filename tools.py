from win32api import GetMonitorInfo, MonitorFromPoint
import math

# Currently a windows-only solution
def calculate_unused_screen_area(window_size):
    # window_size: dictionary
    # ex: {'width': 800, 'height': 450}

    work_area = GetMonitorInfo(MonitorFromPoint((0,0))).get("Work")
    monitor_size = {'width': work_area[2], 'height': work_area[3]}

    diff_size = {
        'width': int(math.ceil((int(monitor_size['width']) - int(window_size['width'])) / 2)), 
        'height': int(math.ceil((int(monitor_size['height']) - int(window_size['height'])) / 2))
    }

    if diff_size['width'] < 0:
        diff_size['width'] = 0
    if diff_size['height'] < 0:
        diff_size['height'] = 0
    
    
    return "+"+str(diff_size['width'])+"+"+str(diff_size['height'])