# Import windows
from alert import Alert
from inventory import Inventory
from loading_screen import LoadingScreen
from prompt_db_pass import PromptDatabasePassword

# Import dependencies
from pg8000.native import Connection
import tools


if __name__ == '__main__':
    # Fire up postgreSql service, if not yet on
    # load_screen = LoadingScreen()

    password = {'inputted': "password"}
    windows_status = {
        'promptdbpass': {'is_closed': True},
        'inventory': {'is_closed': False},
    }
    
    while not windows_status['promptdbpass']['is_closed']:
        # PromptDatabasePassword(window_status['promptdbpass'], password)
        try:
            conn = Connection(user="postgres", password=password['inputted'], database="pikacenter")
            conn.run("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        except Exception as e:
            if not windows_status['promptdbpass']['is_closed']:
                Alert('Database belum nyala / Kata sandi pengguna database salah!')
            continue
    
    
    while not windows_status['inventory']['is_closed']:
        Inventory(windows_status['inventory'], db_password=password['inputted'])
    # Stop postgresql service