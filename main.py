# Import windows
from alert import Alert
from loading_screen import LoadingScreen
from prompt_db_pass import PromptDatabasePassword

# Import dependencies
from pg8000.native import Connection
import tools


if __name__ == '__main__':
    # Fire up postgreSql service, if not yet on
    load_screen = LoadingScreen()

    password = {'inputted': ""}
    is_passed = False
    conn = None
    
    while not is_passed:
        PromptDatabasePassword(password)
        try:
            conn = Connection("postgres", password=password['inputted'])
        except Exception as e:
            Alert('Kata sandi pengguna database salah!')
            continue

        is_passed = True
    # Stop postgresql service