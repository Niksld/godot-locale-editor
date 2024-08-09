from loguru import logger
from StatusHandler import update_status
from platform import system as platform_system
import os
import dearpygui.dearpygui as dpg
import csv
from supported_languages import languages
from Dialogs.CsvPropertiesDialog import CsvPropertiesDialog
from Errors import *

VIEWPORT_LABEL = "Glee Localization Editor"

csv_path = None
save_path = None # gets initialized to path
locale_csv: dict = {}
original_csv: dict = {}
locale_languages = None
loaded_flags = []

csv_delimiter = ";"
csv_quote_char = "|"
csv_dialect = "excel"

def reset() -> None:
    """
    Resets the program to it's default state.
    """
    global locale_csv, locale_languages, loaded_flags
    
    logger.debug("Removing old UI elements...")
    for item in dpg.get_item_children("glee.window.buttons")[1]:
        dpg.delete_item(item)
        
    for item in dpg.get_item_children("glee.window.edit")[1]:
        dpg.delete_item(item)
    
    logger.debug("Unloading flags...")
    for flag in loaded_flags:
        dpg.delete_item(flag)
    
    dpg.set_value("glee.text.string_key", "No string selected")
    
    locale_csv = {}
    locale_languages = None
    dpg.set_viewport_title(f"{VIEWPORT_LABEL}")
    
    logger.debug("Reset done!")
    update_status("No CSV file loaded",1)

def data_load() -> None:
    """
        Loads programs save data - currently just last path.
    """
    global default_path
    logger.debug("Loading save data")
    
    if not os.path.exists(save_path+"data.dat"):
        open(save_path+"data.dat", mode="w+").close()
        logger.info("No save found, creating ...")
    
    with open(save_path+"data.dat", encoding="utf-8", mode="r") as f:
        new_path = f.read()
    default_path = new_path if new_path != "" else default_path

def is_file_loaded() -> bool:
    if locale_csv != None or locale_csv != {}:
        return True
    return False
    
def get_langs() -> None:
    """
        Sets the locale_languages variable to a list of languages
    """
    global locale_languages, locale_csv
    
    for item in locale_csv.items():
        key = item[0]
        
        if key[0] == "#":
            continue
        
        if key == "keys":
            locale_languages = item[1]
            logger.debug("Found the header, saving language list, skipping...")
            break
        else:
            locale_languages = item[1]
            logger.debug("Got first non-comment line. This should be our header.")
            break
    
    if len(locale_languages) == 0:
        logger.error(f"No language keys were found! Is your CSV delimiter set correctly?")
        raise NoLanguageFoundError(f"No languages found. CSV is invalid.")
    
    valid_langs = list(languages.keys())
    for lang in locale_languages:
        if lang == "" or lang == "keys" or lang == "key":
            continue
        
        if lang not in valid_langs:
            logger.error(f"'{lang}' was not recognized as a valid language. CSV is invalid.")
            raise InvalidLanguageError(f"{lang} is not a valid language. CSV is invalid.")

def load_language_flags(language_list: list | tuple) -> None:
    """
    Loads flags for the supplied language codes
    
    Args:
        language_list (list | tuple)
    """
    global loaded_flags
    
    update_status("Loading flags...",0)
    logger.debug("Loading flags...")
    
    if language_list == None: # Contrary to PyLance, this code IS reachable. Doesn't mean you want to reach it.
        logger.error("Language list is None, did we load an empty or corrupt CSV file?")
        update_status("Failed to load flags.",2)
        return
    
    for lang in language_list:
        try:
            width, height, channels, data = dpg.load_image("./images/flags/"+lang+".png")
            
            if not dpg.does_item_exist(f"flag.{lang}"):
                with dpg.texture_registry():
                    dpg.add_static_texture(width=width, height=height, default_value=data, tag=f"flag.{lang}")
                    loaded_flags.append(f"flag.{lang}")
        except TypeError:
            logger.debug(f"Couldn't find flag for language '{lang}'. Missing flag?")

def get_save_path() -> str:
    """
    Gets path for save folder\n\n
    Windows: AppData/Roaming
    Linux/Unix based: ~/.Glee/
    """
    
    retval = None
    if platform_system() == "Windows":
        retval = os.getenv("APPDATA") + "\\Glee\\"
    else:
        retval = os.getenv("HOME") + "/.Glee/"
    
    # If the folder doesnt exist, create it
    if not os.path.exists(retval):
        logger.info(f"Save folder not found, creating...")
        os.makedirs(retval)
        
    logger.debug(f"Save path is '{retval}'")
    return retval

def set_csv_properties(s, a, data: dict):
    global csv_delimiter, csv_quote_char, csv_dialect
    
    csv_delimiter = data["delimiter"]
    csv_quote_char = data["quote"]
    csv_dialect = data["dialect"]
    
def file_exists(appdata) -> bool:
    if not appdata["selections"] == {}:
        return True
    else:
        if appdata["file_name"] != ".csv":
            # TODO attempt to fix.
            return False
            
        else:
            logger.error("No file selected, can't load.")
            update_status("No file selected, unable to load", 2)
            return False

def load_file(data: dict) -> bool:
    """
    # Loads CSV file
    
    Expects a semicolon delimiter. Take the file, take first item in row
    as the key, the rest is stored in a list as the "translations". 
    Saves output directly to global var locale_csv.
    
    format : {"uid": [val1, val2, val3],
            ...}
    """
    global locale_csv, save_path, locale_languages, csv_path, original_csv
    
    update_status("Loading CSV file...",1)
    logger.debug("Loading CSV file")
    
    # If csv_path isnt None = something was already loaded. Reset the app.
    if csv_path != None:
        logger.info("One file has been loaded already, resetting app...")
        reset()

    
    # Getting file_path_name gets the files name, but if you select the 
    # same file again in the same directory, the name is empty. 
    # To ensure the file ALWAYS opens, gotta do this hack. Ew.
    csv_path = list(data["selections"].items())[0][1]
    
    with open(csv_path, newline='', encoding="utf-8") as open_csv:
        csv_reader = csv.reader(open_csv, delimiter=csv_delimiter, quotechar=csv_quote_char, dialect=csv_dialect)
        
        for row in csv_reader:
            translations = []
            for i in range(1,len(row)):
                translations.append(row[i])
            try:
                locale_csv.update({row[0]: translations})
            except IndexError:
                update_status("Failed to load - invalid CSV", 4)
                return False
    
    original_csv = locale_csv
    try:
        get_langs()
        load_language_flags(locale_languages)
    except InvalidLanguageError:
        update_status("Failed to load - invalid CSV language keys", 4)
        return False
    except NoLanguageFoundError:
        update_status("Failed to load - No language keys in CSV found", 4)
        return False
    
    
    logger.debug("File loaded!")
    logger.debug("Saving last FD path")
    
    # Save last location of file directory - we sohuld save only when necessary...
    save_last_path(data["current_path"])
    
    # Run integrity check
    file_integrity_check()
        
    update_status("CSV loaded successfully",-1)
    dpg.configure_item("glee.menu.save", enabled=True)
    dpg.configure_item("glee.menu.save_as", enabled=True)
    return True

def file_integrity_check():
    """Check if the loaded CSV is intact and formatted correctly"""
    for key, val in locale_csv.items():
        
        # Not enough delimiters
        if len(list(val)) < len(locale_languages):
                logger.warning("Found CSV line with not enough delimiters, fixing...")
                
                for _ in range(len(locale_languages)-len(list(val))):
                    locale_csv[key].append("")
                logger.debug("Fixed 👍")
        
        # Too many delimiters!
        elif len(list(val)) > len(locale_languages):
            logger.warning("Found CSV line with too many delimiters, attempting to fix...")
            
            while (len(list(locale_csv[key])) != len(locale_languages) and ("" in list(locale_csv[key]))):
                locale_csv[key].remove("")
            logger.debug("Fixed 👍")
            
def save_file():
    """Saves the locale CSV."""
    global csv_path, locale_csv
    
    if locale_csv == {}:
        logger.debug("Attempting to save non-existant CSV file, ignore.")
        # pop-up dialog with message that no save file is loaded
        return
    
    if csv_path == None:
        logger.debug("Saving CSV with no path, asking for path.")
        # TODO: Save dialog pro save
        logger.error("Not yet implemented, sorry!")
        return
    
    with open(csv_path, encoding="utf-8", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|')
        for key, val in locale_csv.items():
            temp = val[::-1] # invert the list, so that we can append the item string name first
            temp.append(key)
            # and invert again to get the correct order
            writer.writerow(temp[::-1])

    update_status("File saved successfully.",-1)

def file_changed() -> bool:
    """Checks if the locale CSV has been modified.
    Returns: 
        bool
    """
    global locale_csv, original_csv
    
    if locale_csv == original_csv:
        return False
    return True

def get_desktop_path() -> str:
    """
    Gets the desktop path based on user's system
    Returns:
        str: path to ~/Desktop
    """
    return os.path.expanduser("~/Desktop")

def save_last_path(path: str) -> None:
    """
    Save last used path for file_dialog
    """
    try:
        with open(save_path+"data.dat", encoding="utf-8", mode="w") as f:
            f.write(path)
    except Exception as e:
        logger.error(f"Couldnt create or write to last directory cache!\n{e}")

def get_last_path() -> str:
    """
    Returns last path used or path to desktop if last path cant be found.
    """
    global save_path
    if os.path.exists(save_path+"data.dat"):
        with open(save_path+"data.dat", encoding="utf-8", mode="r") as f:
            return f.read()
    else:
        return os.environ("~/Desktop")

save_path = get_save_path() # We have to get it for the first time, yknow?