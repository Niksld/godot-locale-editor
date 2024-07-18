import dearpygui.dearpygui as dpg
from loguru import logger
from platform import system as platform_system
import csv
import os
from languages import languages


locale_csv: dict = {}
default_path = os.path.expanduser("~/Desktop")
save_path = None
os_type = platform_system()
locale_languages = None
app_started = False
dpg.create_context()

def data_load() -> None:
    global default_path
    update_status("Loading save data...",0)
    logger.debug("Loading save data")
    
    if not os.path.exists(save_path+"data.dat"):
        open(save_path+"data.dat", mode="w+").close()
        logger.info("No save found, creating ...")
    
    with open(save_path+"data.dat", encoding="utf-8", mode="r") as f:
        new_path = f.read()
    default_path = new_path if new_path != "" else default_path

def load_language_flags(language_list: list) -> None:
    update_status("Loading flags...",0)
    logger.debug("Loading flags...")
    for lang in language_list:
        try:
            width, height, channels, data = dpg.load_image("./images/flags/"+lang+".png")
        except TypeError:
            logger.info(f"Couldn't find flag for language '{lang}'. Missing flag?")
            
        if not dpg.does_item_exist(f"flag.{lang}"):
            with dpg.texture_registry():
                dpg.add_static_texture(width=width, height=height, default_value=data, tag=f"flag.{lang}")

def get_save_path() -> str:
    global os_type
    retval = None
    if os_type == "Windows":
        retval = os.getenv("APPDATA") + "\\Glee\\"
    else:
        retval = os.getenv("HOME") + "/.Glee/"
        
    if not os.path.exists(retval):
        logger.info(f"Save folder not found, creating...")
        os.makedirs(retval)
    logger.debug(f"Save path is '{retval}'")
    return retval

def open_locale_for(item_string, a):
    global locale_csv, locale_languages
    
    logger.debug(f"Switching to string '{item_string}'")
    dpg.set_value("string_key", item_string)
    for field in enumerate(locale_languages):
        dpg.set_value(f"locale_field.{field[1]}", locale_csv[item_string][field[0]])
        dpg.set_item_user_data(f"locale_field.{field[1]}", {"locale_string":item_string,"language":locale_languages[field[0]], "lang_index":field[0]})

def load_file(sender, app_data) -> None:
    """_summary_
    # Loads CSV file
    
    Expects a semicolon delimiter. Take the file, take first item in row
    as the key, the rest is stored in a list as the "translations". 
    Saves output directly to global var locale_csv.
    
    format : {"uid": [val1, val2, val3],
            ...}
    """
    global locale_csv, save_path, locale_languages
    
    update_status("Loading CSV file...",1)
    logger.debug("Loading CSV file")
    with open(app_data["file_path_name"], newline='', encoding="utf-8") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            row_translations = []
            for i in range(1,len(row)):
                row_translations.append(row[i])
            locale_csv.update({row[0]: row_translations})
            
    generate_buttons(locale_csv)
    load_language_flags(locale_languages)
    generate_input_fields()
    
    logger.debug("UI Done! - Saving last FD path")
    # Save last location of file directory
    default_path = app_data["current_path"]
    
    with open(save_path+"data.dat", encoding="utf-8", mode="w") as f:
        f.write(default_path)
    update_status("CSV loaded successfully",-1)
    dpg.configure_item("savebutton", enabled=True)
    dpg.configure_item("saveasbutton", enabled=True)

def save_file():
    # save the file to CSV
    # update add_input_text label hints
    # update status
    pass

def generate_buttons(csv: dict) -> None: 
    global locale_languages
    logger.debug("Creating buttons")
    for i in enumerate(csv.items()):
        key = i[1][0]
        
        if key == "keys":
            locale_languages = key = i[1][1]
            logger.debug("Found the header, saving language list, skipping...")
            continue
        
        if "[img]" in key:
            logger.debug("Found Image tag in text, replacing with image if able (TODO)")
            pass # TODO
        
        # Label could be customized, but we still have to get the item name somehow. thus tag and label
        dpg.add_button(label=key, tag=key,width=270, height=25, parent="button_list", callback=open_locale_for) 

def generate_input_fields():
    global languages
    
    logger.debug("Creating input fields ...")
    for lang in enumerate(locale_languages):
        if os.path.exists(f"./images/flags/{locale_languages[lang[0]]}.png"):
            ttip_parent = dpg.add_image(f"flag.{locale_languages[lang[0]]}", parent="editing_window", pos=(10, lang[0]*45+25), width=30, height=20)
        else:
            ttip_parent = dpg.add_text(locale_languages[lang[0]], parent="editing_window", pos=(10, lang[0]*45+25))

        with dpg.tooltip(ttip_parent):
            try:
                tip_lang = languages[locale_languages[lang[0]]]
            except KeyError:
                tip_lang = "undefined"
            dpg.add_text(tip_lang)

        temp = dpg.add_input_text(hint=lang[1], parent="editing_window", width=dpg.get_item_width("editing_window")-5, height=65, pos=(55, lang[0]*45+25), callback=update_translation, tag=f"locale_field.{lang[1]}")
        dpg.set_value(temp, lang[1])

def update_status(message: str, severity: str | int = None) -> None:
    """_summary_
    Update status of the app
    message - str: message to display
    severity - List[str, int] - color the text by severity name or number.
    \n0 - low / 4 - very high
    """
    global app_started
    color = None
    
    if not app_started:
        return
    
    match severity:
        case "very high" | 4:
            color = [255,0,0]
        case "high" | 3:
            color = [255,94,0]
        case "medium" | 2:
            color = [245,114,0]
        case "low" | 1:
            color = [255,238,0]
        case "success" | -1:
            color = [0,255,0]
        case _:
            color = [255,255,255]

    dpg.set_value("status_text", message)
    dpg.configure_item("status_text", color=color)

def update_translation(s, new_string, data):
    global locale_csv
    locale_csv[data["locale_string"]][data["lang_index"]] = new_string  

logger.debug("Starting Glee")
save_path = get_save_path() 
data_load()

# Set Font + Unicode characters
with dpg.font_registry():
    with dpg.font("./fonts/ubuntu/Ubuntu-R.ttf", 16) as ubuntu_reg:
        dpg.add_font_range(0x0100, 0x25ff)
    dpg.bind_font(ubuntu_reg)

# Viewport
dpg.create_viewport(title='Glee - Localization Editor', width=1000, height=700, resizable=False)
with dpg.file_dialog(directory_selector=False, show=False, callback=load_file, id="file_dialog", width=700 ,height=400, modal=True, default_path=default_path):
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

# Main window
with dpg.window(label="Glee - Localization Editor", width=dpg.get_viewport_width(), height=dpg.get_viewport_height(), no_move=True, no_collapse=True, no_resize=True, no_title_bar=True) as main_window:
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save", enabled=False, tag="savebutton")
            dpg.add_menu_item(label="Save as..", enabled=False, tag="saveasbutton")
            dpg.add_menu_item(label="Load locale .csv", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_menu_item(label="Exit") # TODO: Check if file is saved, if not prompt user to save
        with dpg.menu(label="Options"):
            dpg.add_menu_item(label="Preferences")
            
    dpg.add_text("String", pos=(125,25))
    dpg.add_text("No string selected", pos=(310,25), tag="string_key")
    dpg.add_text("Status:", pos=(10,dpg.get_viewport_height()-65))
    dpg.add_text(tag="status_text", pos=(60,dpg.get_viewport_height()-65))
    dpg.add_child_window(width=300,height=dpg.get_viewport_height()-115, pos=(0,50), tag="button_list")
    dpg.add_child_window(width=670,height=dpg.get_viewport_height()-115, pos=(305,50), tag="editing_window")
app_started = True
update_status("No .CSV file loaded", 1)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()