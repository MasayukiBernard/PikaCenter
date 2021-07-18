# Import windows
from alert import Alert
from inventory import Inventory
from loading_screen import LoadingScreen
from prompt_db_pass import PromptDatabasePassword

# Import dependencies
from pg8000.native import Connection
import ctypes
import os

def try_connecting_to_db(window_status):
    is_success = False
    PromptDatabasePassword(window_status, password)
    try:
        conn = Connection(user="postgres", password=password['inputted'], database="pikacenter")
        conn.run("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        is_success = True
    except Exception as e:
        if not window_status['is_closed']:
            Alert('Database belum nyala / Kata sandi pengguna database salah!')
    
    if windows_status['promptdbpass']['is_closed']:
        exit(1)
    
    return is_success

if __name__ == '__main__':
    if ctypes.windll.shell32.IsUserAnAdmin():
        # Fire up postgreSql service, if not yet on
        command_res = os.system("sc start postgresql-x64-13")

        load_screen = LoadingScreen()

        password = {'inputted': ""}
        windows_status = {
            'promptdbpass': {'is_closed': True},
            'inventory': {'is_closed': True},
        }
        
        while not try_connecting_to_db(windows_status['promptdbpass']): pass
        
        Inventory(windows_status['inventory'], db_password=password['inputted'])
        if windows_status['inventory']['is_closed']:
            # Stop postgresql service
            command_res = os.system("sc stop postgresql-x64-13")
        else:
            pass

    else:
        pass