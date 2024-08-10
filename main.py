import dearpygui.dearpygui as dpg
from loguru import logger
from supported_languages import languages
import DataHandler as dh
from StatusHandler import update_status
from KeyboardWorkaround import letter_workaround
from Dialogs.CsvPropertiesDialog import CsvPropertiesDialog
from Dialogs.NewStringDialog import NewStringDialog
from Errors import *

button_list = []

dpg.create_context()

# Set Font + Unicode characters
with dpg.font_registry():
    with dpg.font("./fonts/ubuntu/Ubuntu-R.ttf", 16) as ubuntu_reg:
        dpg.add_font_range(0x0100, 0x25ff)
    dpg.bind_font(ubuntu_reg)
    
# Handle shortcuts
def shortcut_handler():
    if dpg.is_key_pressed(dpg.mvKey_S):
        dh.save_file()

with dpg.handler_registry():
    dpg.add_key_down_handler(dpg.mvKey_Control, callback=shortcut_handler)
    
# --- GUI Methods ---
def open_locale_for(item_string: str, a: dict) -> None:
    """
    Opens locale for given item string
    
    Args:
        item_string (str): sender, their tags correspond to item strings in the CSV
        appdata (Any): DearPyGui argument
    """
    global locale_csv
    
    item_string = item_string.removeprefix("glee.loaded_string.")    
    logger.debug(f"Switching to string '{item_string}'")
    dpg.set_value("glee.text.string_key", item_string) # Set title for right pane to item string
    
    for index, lang in enumerate(dh.locale_languages):
        dpg.set_value(f"glee.locale_field.{lang}", dh.locale_csv[item_string][index])
        dpg.configure_item(f"glee.locale_field.{lang}", hint=dh.locale_csv[item_string][index])
        dpg.set_item_user_data(f"glee.locale_field.{lang}", {"locale_string":item_string,"language":dh.locale_languages[index], "lang_index":index})

def generate_buttons(csv: dict) -> None:
    """Generates buttons for each string key""" 
    global button_list
    logger.debug("Creating buttons")
    if button_list != []:
        button_list = []
    for i in enumerate(csv.items()):
        key = i[1][0]
        
        if key[0] == "#" or key == "keys" or i[0] == 0:
            logger.debug("Commment or header found, skipping...")
            continue
        
        if "[img]" in key:
            logger.debug("Found Image tag in text, replacing with image if able (TODO)")
            pass # TODO
        
        # Label could be customized, but we still have to get the item name somehow. thus tag and label
        dpg.add_button(label=key, tag=f"glee.loaded_string.{key}",width=270, height=25, parent="glee.window.buttons", callback=open_locale_for)
        button_list.append(key) 

def regenerate_buttons():
    scroll_amount = dpg.get_y_scroll("glee.window.buttons")
    logger.debug("Regenerating buttons...")
    for item in dpg.get_item_children("glee.window.buttons")[1]:
        dpg.delete_item(item)
    
    generate_buttons(dh.locale_csv)
    dpg.set_y_scroll("glee.window.buttons",scroll_amount)
            
def generate_input_fields():
    """Generates input field for each language"""
    global languages
    logger.debug("Creating input fields ...")
    
    if dh.locale_languages == None:
        logger.error("Locale header is none when generating input fields, cant generate...")
        return
    
    for lang in enumerate(dh.locale_languages):
        if dpg.does_alias_exist(f"flag.{dh.locale_languages[lang[0]]}"):
            ttip_parent = dpg.add_image(f"flag.{dh.locale_languages[lang[0]]}", parent="glee.window.edit", pos=(10, lang[0]*45+25), width=30, height=20, tag=f"img.flag.{dh.locale_languages[lang[0]]}")
        else:
            ttip_parent = dpg.add_text(dh.locale_languages[lang[0]], parent="glee.window.edit", pos=(10, lang[0]*45+25), tag=f"img.flag.{dh.locale_languages[lang[0]]}")

        with dpg.tooltip(ttip_parent):
            try:
                tip_lang = languages[dh.locale_languages[lang[0]]]
            except KeyError:
                tip_lang = "undefined"
            dpg.add_text(tip_lang)
        
        temp = dpg.add_input_text(hint=lang[1], parent="glee.window.edit", width=dpg.get_item_width("glee.window.edit")-15, height=65, pos=(55, lang[0]*45+25), callback=update_translation, tag=f"glee.locale_field.{lang[1]}")
        dpg.set_value(temp, lang[1])

def update_translation(sender, new_string, data):
    global locale_csv, letter_workaround
    
    # Workaround because DPG has a bug with input_text and Latin ext. characters 
    if any(letter in new_string for letter in list(letter_workaround.keys())):
        for corrupt_letter, correct_letter in letter_workaround.items():
            new_string = new_string.replace(corrupt_letter, correct_letter)
    dh.locale_csv[data["locale_string"]][data["lang_index"]] = new_string  
    dpg.set_value(sender, new_string)

def exit_app():
    if dh.file_changed():
        logger.debug("File dialog here!") # popup file dialog to save
    dpg.stop_dearpygui()
    
def add_string():
    if not dh.is_file_loaded():
        logger.debug("No file loaded, creating new empty CSV")
        logger.debug("Not yet implemented, sorry!")
        # TODO
        # pop-up dialog to setup CSV file (dialect, filename and path)
        # pop-up dialog to setup languages
        # pop-up new key dialog
    else:
        logger.debug("Adding new string...")
        try:
            NewStringDialog(button_list, callback=lambda new_key, position:(dh.add_new_string_key(new_key, position), regenerate_buttons(), dpg.delete_item("glee.window.new_string_dialog"), regenerate_buttons()),
                                abort_callback=lambda:(dpg.delete_item("glee.window.new_string_dialog"))
                                )
        except NoStringKeyError:
            logger.error("No String Key supplied")
        except TakenStringKeyError:
            logger.error("String Key is already registered!")

def remove_string():
    if dh.is_file_loaded():
        button_last_position = button_list.index(dpg.get_value("glee.text.string_key"))
        dh.remove_string_key(dpg.get_value("glee.text.string_key"))
        regenerate_buttons()
        open_locale_for(button_list[button_last_position], None)

def create_dialog_csv_properties(se, appdata):
    if dh.file_exists(appdata):
        logger.debug("Creating CSV Properties dialog")
        update_status("Getting CSV properties...",1)
        dpg.split_frame()
        CsvPropertiesDialog(callback=lambda s, a, data:(dh.set_csv_properties(s, a, data), create_ui(se,appdata), dpg.delete_item("glee.window.csv_properties_dialog")),
                            abort_callback=lambda:(dh.reset(), dpg.delete_item("glee.window.csv_properties_dialog"), hide_edit_buttons()),
                            )

def show_edit_buttons():
    dpg.show_item("glee.button.add_string")
    dpg.show_item("glee.button.delete_string")
    
def hide_edit_buttons():
    dpg.hide_item("glee.button.add_string")
    dpg.hide_item("glee.button.delete_string")

def create_ui(s, appdata):
    global locale_csv, button_list
    
    if dh.load_file(appdata):
        generate_buttons(dh.locale_csv)
        generate_input_fields()
        open_locale_for(button_list[0], None)
        dpg.configure_item("glee.menu.close_file",enabled=True)
        dpg.set_viewport_title(f"{dh.VIEWPORT_LABEL} - {list(appdata['selections'].keys())[0]}")
        show_edit_buttons()

logger.debug("Starting Glee")
dh.data_load() # Attempt to load last path

# Viewport
dpg.create_viewport(title=f'{dh.VIEWPORT_LABEL}', width=1000, height=700, resizable=False)

# File Dialog
with dpg.file_dialog(label="Open file", directory_selector=False, show=False, callback=create_dialog_csv_properties, id="glee.window.open_file_dialog", width=700 ,height=400, modal=True, default_path=dh.get_last_path()):
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

# Main window
with dpg.window(label="", width=dpg.get_viewport_width(), height=dpg.get_viewport_height(), no_move=True, no_collapse=True, no_resize=True, no_title_bar=True) as main_window:
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save", enabled=False, tag="glee.menu.save", callback=dh.save_file)
            dpg.add_menu_item(label="Save as..", enabled=False, tag="glee.menu.save_as")
            dpg.add_menu_item(label="Load locale .csv", callback=lambda: dpg.show_item("glee.window.open_file_dialog"))
            dpg.add_menu_item(label="Close CSV File", callback=lambda: (dh.reset(), update_status("No CSV file loaded",1), hide_edit_buttons(), dpg.configure_item("glee.menu.close_file", enabled=False)), enabled=False, tag="glee.menu.close_file")
            dpg.add_menu_item(label="Exit", callback=exit_app)
        with dpg.menu(label="Options"):
            dpg.add_menu_item(label="Preferences")
            
    dpg.add_text("String", pos=(125,25))
    dpg.add_button(label=" + ", show=False, pos=(278,25), height=23, tag="glee.button.add_string", callback=add_string)
    dpg.add_text("No string selected", pos=(310,25), tag="glee.text.string_key")
    dpg.add_button(label=" Delete String ", show=False, pos=(dpg.get_viewport_width()-125,23), height=23, tag="glee.button.delete_string", callback=remove_string)
    dpg.add_text("Status:", pos=(10,dpg.get_viewport_height()-65))
    dpg.add_text("No CSV file loaded", color=(255,238,0),tag="glee.text.status", pos=(60,dpg.get_viewport_height()-65))
    dpg.add_child_window(width=300,height=dpg.get_viewport_height()-115, pos=(0,50), tag="glee.window.buttons")
    dpg.add_child_window(width=670,height=dpg.get_viewport_height()-115, pos=(305,50), tag="glee.window.edit")

# Rest of the DPG setup
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

