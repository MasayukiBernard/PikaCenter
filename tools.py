from win32api import GetMonitorInfo, MonitorFromPoint
import math
from re import escape

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

def create_pretty_alphanumerical(string):
    return string.replace("\n", "").rstrip().lstrip()

def create_pretty_numerical(numeric):
    stripped_zeros = ('%.24f' % numeric).rstrip('0').rstrip('.')
    return "{:,}".format(int(stripped_zeros))

def correct_numerical_entry_input(prev_str, cursor_pos, input_str):
    corrected_pos = cursor_pos
    corrected = create_pretty_numerical(int(input_str))
    corrected_len = len(corrected)
    if cursor_pos > 0 and cursor_pos < corrected_len:
        prev_str = prev_str[:cursor_pos]
        prev_corr_str = corrected[:cursor_pos]
        comma_count = prev_str.count(',')
        corrected_comma_count = prev_corr_str.count(',')
        if corrected_comma_count - comma_count > 0:
            corrected_pos += 1
        elif corrected_comma_count - comma_count < 0:
            corrected_pos -= 1
            
    return corrected_pos, corrected

def create_db_input_string(string):
    return escape(create_pretty_alphanumerical(string)).replace('\'','\'\'').replace('"','""')
    
def remove_non_integer(string):
    return ''.join(filter(str.isdigit, string))

def destroy_roots_recursively(roots_list):
    for list_item in roots_list:
        if type(list_item) is not list:
            try:
                list_item.destroy()
            except Exception as e:
                pass
            
            continue

        destroy_roots_recursively(list_item)