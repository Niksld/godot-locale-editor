from loguru import logger
#from main import reset
from StatusHandler import update_status
from platform import system as platform_system
import os
import dearpygui.dearpygui as dpg
import csv

csv_path = None
save_path = None # gets inicialized to path
locale_csv: dict = {}
original_csv: dict = {} 
locale_languages = None
loaded_flags = []

def reset() -> None:
    """
    Resets the program
    """
    global locale_csv, locale_languages, loaded_flags
    
    logger.debug("Removing old UI elements...")
    for item in dpg.get_item_children("button_list")[1]:
        dpg.delete_item(item)
        
    for item in dpg.get_item_children("editing_window")[1]:
        dpg.delete_item(item)
    
    logger.debug("Unloading flags...")
    for flag in loaded_flags:
        dpg.delete_item(flag)
    
    dpg.set_value("string_key", "No string selected")
    
    locale_csv = {}
    locale_languages = None

def data_load() -> None:
    """_summary_
        Loads programs save data - currently just last path
    """
    global default_path
    logger.debug("Loading save data")
    
    if not os.path.exists(save_path+"data.dat"):
        open(save_path+"data.dat", mode="w+").close()
        logger.info("No save found, creating ...")
    
    with open(save_path+"data.dat", encoding="utf-8", mode="r") as f:
        new_path = f.read()
    default_path = new_path if new_path != "" else default_path

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

def load_language_flags(language_list: list | tuple) -> None:
    """_summary_
    Loads flags for the supplied language codes
    
    Args:
        language_list (list | tuple)
    """
    global loaded_flags
    
    update_status("Loading flags...",0)
    logger.debug("Loading flags...")
    
    if language_list == None:
        logger.error("Language list is None, did we load an empty or corrupt CSV file?")
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

def load_file(data: dict) -> bool:
    """_summary_
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
        csv_reader = csv.reader(open_csv, delimiter=';', quotechar='|')
        for row in csv_reader:
            translations = []
            for i in range(1,len(row)):
                translations.append(row[i])
            locale_csv.update({row[0]: translations})
    
    original_csv = locale_csv
    get_langs()
    load_language_flags(locale_languages)
    
    
    logger.debug("UI Done! - Saving last FD path")
    
    # Save last location of file directory - we sohuld save only when necessary...
    save_last_path(data["current_path"])
        
    update_status("CSV loaded successfully",-1)
    dpg.configure_item("savebutton", enabled=True)
    dpg.configure_item("saveasbutton", enabled=True)
    return True

def save_file():
    global csv_path, locale_csv
    # save the file to CSV
    with open(csv_path, encoding="utf-8", mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='|')
        for key, val in locale_csv.items():
            temp = val[::-1] # invert the list, so that we can append the item string name first
            temp.append(key)
            # and invert again to get the correct order
            writer.writerow(temp[::-1])
        
    # update status
    pass

def file_changed() -> bool:
    global locale_csv, original_csv
    
    if locale_csv == original_csv:
        return False
    
    return True

def get_desktop_path() -> str:
    """_summary_
    Gets the desktop path based on user's system
    Returns:
        str: path to ~/Desktop
    """
    return os.path.expanduser("~/Desktop")

def save_last_path(path: str) -> None:
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

save_path = get_save_path()