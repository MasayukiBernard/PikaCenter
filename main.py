# Import windows
from loading_screen import LoadingScreen
from main_nav import MainNavigation
from prompt_db_pass import PromptDatabasePassword

# Import dependencies
import ctypes
from os import system

def try_connecting_to_db(window_status, password):
    is_success = [False]
    PromptDatabasePassword(window_status, password, is_success)
    
    if windows_status['promptdbpass']['is_closed']:
        exit(1)
    
    return is_success[0]

if __name__ == '__main__':
    # TO REMEMBER
    # .exe program needs to always run in admin mode
    # hide console and create a single file using "pyinstaller --onefile --noconsole --hidden-import babel.numbers --name PC-INV main.py"
    if ctypes.windll.shell32.IsUserAnAdmin():
        # Fire up postgreSql service, if not yet on
        command_res = system("sc start postgresql-x64-13")

        load_screen = LoadingScreen()

        password = {'inputted': ""}
        # password = {'inputted': "password"}
        windows_status = {
            'main_nav': {'is_closed': True},
            'promptdbpass': {'is_closed': True},
            'inventory': {'is_closed': True},
        }
        
        while not try_connecting_to_db(windows_status['promptdbpass'], password): pass
        
        MainNavigation(windows_status, password['inputted'])
        
        system("sc stop postgresql-x64-13")

    else:
        pass