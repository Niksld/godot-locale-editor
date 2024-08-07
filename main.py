import dearpygui.dearpygui as dpg
from loguru import logger
from supported_languages import languages
import DataHandler as dh
from StatusHandler import update_status
from KeyboardWorkaround import letter_workaround

dpg.create_context()

def open_locale_for(item_string: str, appdata: dict) -> None:
    """
    Opens locale for given item string
    
    Args:
        item_string (str): sender, their tags correspond to item strings in the CSV
        appdata (Any): DearPyGui argument
    """
    global locale_csv
    
    logger.debug(f"Switching to string '{item_string}'")
    dpg.set_value("string_key", item_string) # Set title for right pane to item string
    
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
        dpg.add_button(label=key, tag=key,width=270, height=25, parent="button_list", callback=open_locale_for) 

def generate_input_fields():
    global languages
    logger.debug("Creating input fields ...")
    
    if dh.locale_languages == None:
        logger.error("Locale header is none when generating input fields, cant generate...")
        return
    
    for lang in enumerate(dh.locale_languages):
        if dpg.does_alias_exist(f"flag.{dh.locale_languages[lang[0]]}"):
            ttip_parent = dpg.add_image(f"flag.{dh.locale_languages[lang[0]]}", parent="editing_window", pos=(10, lang[0]*45+25), width=30, height=20, tag=f"img.flag.{dh.locale_languages[lang[0]]}")
        else:
            ttip_parent = dpg.add_text(dh.locale_languages[lang[0]], parent="editing_window", pos=(10, lang[0]*45+25), tag=f"img.flag.{dh.locale_languages[lang[0]]}")

        with dpg.tooltip(ttip_parent):
            try:
                tip_lang = languages[dh.locale_languages[lang[0]]]
            except KeyError:
                tip_lang = "undefined"
            dpg.add_text(tip_lang)

        temp = dpg.add_input_text(hint=lang[1], parent="editing_window", width=dpg.get_item_width("editing_window")-15, height=65, pos=(55, lang[0]*45+25), callback=update_translation, tag=f"locale_field.{lang[1]}")
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

logger.debug("Starting Glee")
dh.data_load()

# Set Font + Unicode characters
with dpg.font_registry():
    with dpg.font("./fonts/ubuntu/Ubuntu-R.ttf", 16) as ubuntu_reg:
        dpg.add_font_range(0x0100, 0x25ff)
    dpg.bind_font(ubuntu_reg)
    

# Viewport
dpg.create_viewport(title='Glee - Localization Editor', width=1000, height=700, resizable=False)

# File Dialog
with dpg.file_dialog(directory_selector=False, show=False, callback=create_ui, id="file_dialog", width=700 ,height=400, modal=True, default_path=dh.get_last_path()):
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

# Main window
with dpg.window(label="Glee - Localization Editor", width=dpg.get_viewport_width(), height=dpg.get_viewport_height(), no_move=True, no_collapse=True, no_resize=True, no_title_bar=True) as main_window:
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Save", enabled=False, tag="savebutton", callback=dh.save_file)
            dpg.add_menu_item(label="Save as..", enabled=False, tag="saveasbutton")
            dpg.add_menu_item(label="Load locale .csv", callback=lambda: dpg.show_item("file_dialog"))
            dpg.add_menu_item(label="Close CSV File", callback=lambda: (dh.reset(), update_status("No CSV file loaded",1)))
            dpg.add_menu_item(label="Exit", callback=exit_app)
        with dpg.menu(label="Options"):
            dpg.add_menu_item(label="Preferences")
            
    dpg.add_text("String", pos=(125,25))
    dpg.add_text("No string selected", pos=(310,25), tag="string_key")
    dpg.add_text("Status:", pos=(10,dpg.get_viewport_height()-65))
    dpg.add_text("No CSV file loaded", color=(255,238,0),tag="status_text", pos=(60,dpg.get_viewport_height()-65))
    dpg.add_child_window(width=300,height=dpg.get_viewport_height()-115, pos=(0,50), tag="button_list")
    dpg.add_child_window(width=670,height=dpg.get_viewport_height()-115, pos=(305,50), tag="editing_window")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

