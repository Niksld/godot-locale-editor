import dearpygui.dearpygui as dpg
from loguru import logger
from supported_languages import languages
import DataHandler as dh
from StatusHandler import update_status
from KeyboardWorkaround import letter_workaround

button_list = []

dpg.create_context()

def open_locale_for(item_string: str, appdata: dict) -> None:
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
        dpg.set_value(f"locale_field.{lang}", dh.locale_csv[item_string][index])
        dpg.set_item_user_data(f"locale_field.{lang}", {"locale_string":item_string,"language":dh.locale_languages[index], "lang_index":index})

def generate_buttons(csv: dict) -> None: 
    logger.debug("Creating buttons")

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

def generate_input_fields():
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

        temp = dpg.add_input_text(hint=lang[1], parent="glee.window.edit", width=dpg.get_item_width("glee.window.edit")-15, height=65, pos=(55, lang[0]*45+25), callback=update_translation, tag=f"locale_field.{lang[1]}")
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

def create_ui(s, appdata):
    global locale_csv
    dh.load_file(appdata)
    generate_buttons(dh.locale_csv)
    generate_input_fields()
    open_locale_for(button_list[0], None)
    dpg.configure_item("glee.menu.close_file",enabled=True)  

logger.debug("Starting Glee")
dh.data_load()

# Set Font + Unicode characters
with dpg.font_registry():
    with dpg.font("./fonts/ubuntu/Ubuntu-R.ttf", 16) as ubuntu_reg:
        dpg.add_font_range(0x0100, 0x25ff)
    dpg.bind_font(ubuntu_reg)
    

# Viewport
dpg.create_viewport(title='Glee - Localization Editor', width=1000, height=700, resizable=False)

# File Dialogs
with dpg.file_dialog(label="Open file", directory_selector=False, show=False, callback=create_ui, id="glee.window.open_file_dialog", width=700 ,height=400, modal=True, default_path=dh.get_last_path()):
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

# Main window
with dpg.window(label="Glee - Localization Editor", width=dpg.get_viewport_width(), height=dpg.get_viewport_height(), no_move=True, no_collapse=True, no_resize=True, no_title_bar=True) as main_window:
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save", enabled=False, tag="glee.menu.save", callback=dh.save_file)
            dpg.add_menu_item(label="Save as..", enabled=False, tag="glee.menu.save_as")
            dpg.add_menu_item(label="Load locale .csv", callback=lambda: dpg.show_item("glee.window.open_file_dialog"))
            dpg.add_menu_item(label="Close CSV File", callback=lambda: (dh.reset(), update_status("No CSV file loaded",1), dpg.configure_item("glee.menu.close_file", enabled=False)), enabled=False, tag="glee.menu.close_file")
            dpg.add_menu_item(label="Exit", callback=exit_app)
        with dpg.menu(label="Options"):
            dpg.add_menu_item(label="Preferences")
            
    dpg.add_text("String", pos=(125,25))
    dpg.add_text("No string selected", pos=(310,25), tag="glee.text.string_key")
    dpg.add_text("Status:", pos=(10,dpg.get_viewport_height()-65))
    dpg.add_text("No CSV file loaded", color=(255,238,0),tag="glee.text.status", pos=(60,dpg.get_viewport_height()-65))
    dpg.add_child_window(width=300,height=dpg.get_viewport_height()-115, pos=(0,50), tag="glee.window.buttons")
    dpg.add_child_window(width=670,height=dpg.get_viewport_height()-115, pos=(305,50), tag="glee.window.edit")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

