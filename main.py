import dearpygui.dearpygui as dpg
from loguru import logger
from os import _exit
from supported_languages import languages
import DataHandler as dh
from StatusHandler import update_status
from KeyboardWorkaround import letter_workaround
from Dialogs.CsvPropertiesDialog import CsvPropertiesDialog
from Dialogs.NewStringDialog import NewStringDialog
from Dialogs.Warning import Warning
from Errors import *

VIEWPORT_MIN_SIZE = [500,300]

button_list = []
is_maximized = False
viewport_max_size = []
unmaximized_res = (1000,730)
unmaximized_pos = []

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
        if dpg.does_alias_exist(f"glee.flag.{dh.locale_languages[lang[0]]}"):
            ttip_parent = dpg.add_image(f"glee.flag.{dh.locale_languages[lang[0]]}", parent="glee.window.edit", pos=(10, lang[0]*45+25), width=30, height=20, tag=f"glee.img.flag.{dh.locale_languages[lang[0]]}")
        else:
            ttip_parent = dpg.add_text(dh.locale_languages[lang[0]], parent="glee.window.edit", pos=(10, lang[0]*45+25), tag=f"glee.img.flag.{dh.locale_languages[lang[0]]}")

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
    logger.debug("Got request to end app")
    if dh.file_changed():
        logger.debug("File dialog here!") # popup file dialog to save
    else:
        logger.debug("File didnt change, no need to save!")
    _exit(0)

def string_dialog_callback(new_key, position):
    dh.add_new_string_key(new_key, position)
    dpg.delete_item("glee.window.new_string_dialog")
    regenerate_buttons()

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
            NewStringDialog(button_list, 
                            callback=lambda new_key, position:string_dialog_callback(new_key, position),
                            abort_callback=lambda:(dpg.delete_item("glee.window.new_string_dialog"))
                            )
        except NoStringKeyError:
            logger.error("No String Key supplied")
        except TakenStringKeyError:
            logger.error("String Key is already registered!")

def remove_string_callback():
    if dh.is_file_loaded():
        string = dpg.get_value("glee.text.string_key")
        if not dh.is_key_empty(string):
            Warning(label="Remove String Key?",
                    msg=f"Are you sure you want to delete:\n'{string}'  ?",
                    callback=lambda: (remove_string(string), dpg.delete_item("glee.window.warning")),
                    abort_callback=lambda: dpg.delete_item("glee.window.warning"))
        else:
            remove_string(string)

def remove_string(string: str):
    logger.debug(f"Removing String Key '{string}'")
    if not string in button_list:
        logger.error("Attempting to remove non-existant string key.")
        return
    
    button_last_position = button_list.index(string)
    dh.remove_string_key(string)
    regenerate_buttons()
    open_locale_for(button_list[button_last_position], None)

def close_file_callback():
    close_file = lambda: (dh.reset(), update_status("No CSV file loaded",1), hide_edit_buttons(), dpg.configure_item("glee.menu.close_file", enabled=False))

    if dh.file_changed():
        Warning(label="Discard unsaved changes?",
                msg="There are unsaved changed to the file.\nDiscard unsaved changes?",
                callback=lambda:(close_file(), dpg.delete_item("glee.window.warning")),
                abort_callback=lambda: dpg.delete_item("glee.window.warning")
                )
    else:
        close_file()
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
        
def toggle_windowed_max():
    global is_maximized, unmaximized_res, viewport_max_size, unmaximized_pos
    logger.debug(f"Changing window to {'maximized' if not is_maximized else 'windowed'} mode")
    
    if is_maximized:
        dpg.set_viewport_width(unmaximized_res[0])
        dpg.set_viewport_height(unmaximized_res[1])
        dpg.set_viewport_pos((unmaximized_pos[0],unmaximized_pos[1]))
    else:
        unmaximized_res = (dpg.get_viewport_width(), dpg.get_viewport_height())
        if not viewport_max_size:
            dpg.maximize_viewport()
            dpg.split_frame()
            viewport_max_size = [dpg.get_viewport_width(), dpg.get_viewport_height()]
            unmaximized_pos = dpg.get_viewport_pos()
        else:
            dpg.set_viewport_width(viewport_max_size[0])
            dpg.set_viewport_height(viewport_max_size[1])
            unmaximized_pos = dpg.get_viewport_pos()
            dpg.set_viewport_pos([0,0])
        
    is_maximized = not is_maximized
    
def on_resize():
    
    mouse_pos = dpg.get_mouse_pos()
    print(mouse_pos)
    if mouse_pos[1] in range(0,20) or mouse_pos[1] in range(-30,-20):
        dpg.set_item_height("glee.main_window", dpg.get_viewport_height())
        dpg.set_item_pos("glee.main_window", (0,30))
        dpg.split_frame(delay=1)
        return
    
    logger.debug(f"Resizing window! vp_size: [{dpg.get_viewport_width()}, {dpg.get_viewport_height()}]  w_size: [{dpg.get_item_width('glee.main_window')},{dpg.get_item_height('glee.main_window')}]")
    
    new_size = (dpg.get_item_width("glee.main_window"), dpg.get_item_height("glee.main_window"))
    
    if new_size[0] < VIEWPORT_MIN_SIZE[0]:
        dpg.set_viewport_width(VIEWPORT_MIN_SIZE[0])
    else:
        dpg.set_viewport_width(new_size[0])
        
    if new_size[1] < VIEWPORT_MIN_SIZE[1]:
        dpg.set_viewport_height(VIEWPORT_MIN_SIZE[1]+30)
    else:
        dpg.set_viewport_height(new_size[1]+30)
    
    dpg.set_item_width("glee.titlebar", dpg.get_item_width("glee.main_window"))
    
    if dpg.get_item_pos("glee.main_window") != (0,30):
        dpg.set_item_pos("glee.main_window", (0,30))
    
    # Re-adjust titlebar
    for offset, child in enumerate(dpg.get_item_children("glee.titlebar.group")[1]):
        if not dpg.get_item_alias(child) == "glee.titlebar.label":
            dpg.configure_item(child, pos=(dpg.get_item_width("glee.titlebar")-(dpg.get_item_width("glee.titlebar.x")+2)*offset-2, dpg.get_item_height("glee.titlebar")-dpg.get_item_height("glee.titlebar")/3.5))
    
    # Re-adjust all positions...
    #print("readjust the rest")
    
# Handle resizing
with dpg.item_handler_registry(tag="glee.handler.resize"):
    dpg.add_item_resize_handler(callback=on_resize)

logger.debug("Starting Glee...")
dh.data_load() # Attempt to load last path
dh.load_icons()

# Viewport
dpg.create_viewport(title=f'{dh.VIEWPORT_LABEL}', width=1000, height=700, min_width=500, resizable=True, decorated=False)

# File Dialog
with dpg.file_dialog(label="Open file", directory_selector=False, show=False, callback=create_dialog_csv_properties, id="glee.window.open_file_dialog", width=700 ,height=400, modal=True, default_path=dh.get_last_path()):
    dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

# Titlebar window
def drag_cb():
    vp_pos = dpg.get_viewport_pos()
    drag_delta = dpg.get_mouse_drag_delta()
    if any(dpg.is_item_active(i) for i in dpg.get_item_children(drag_vp_wnd, slot=1)):
        return

    if dpg.is_item_focused(drag_vp_wnd):
        dpg.set_viewport_pos([vp_pos[0] + drag_delta[0], vp_pos[1] + drag_delta[1]])
    
with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=drag_cb)

with dpg.window(no_move=True, no_resize=True, no_title_bar=True, pos=[0, -70], no_scroll_with_mouse=True, no_scrollbar=True, height=100, width=dpg.get_viewport_width(), tag="glee.titlebar") as drag_vp_wnd:
    with dpg.group(horizontal=True, tag="glee.titlebar.group"):
        dpg.add_text("Glee Localization Editor", pos=(10, dpg.get_item_height("glee.titlebar")-29), tag="glee.titlebar.label")
        dpg.add_button(label="X", pos=(dpg.get_item_width("glee.titlebar")-33, dpg.get_item_height("glee.titlebar")-27), width=30, height=25, callback=exit_app, tag="glee.titlebar.x")
        #dpg.add_button(label="+", pos=(dpg.get_item_width("glee.titlebar")-65, dpg.get_item_height("glee.titlebar")-27), width=30, height=25, callback=toggle_windowed_max, tag="glee.titlebar.max") 
        # Maximizing and resizing is buggy as all hell. Not touching that rn.
        dpg.add_button(label="-", pos=(dpg.get_item_width("glee.titlebar")-97, dpg.get_item_height("glee.titlebar")-27), width=30, height=25, callback=dpg.minimize_viewport, tag="glee.titlebar.min")

# Main window
with dpg.window(label="", width=dpg.get_viewport_width(), height=dpg.get_viewport_height()-30, no_move=True, no_collapse=True, no_resize=True, no_title_bar=True, pos=(0,30), tag="glee.main_window", min_size=VIEWPORT_MIN_SIZE):
    with dpg.menu_bar():
        with dpg.menu(label="File"):
            dpg.add_menu_item(label="Load locale .csv", callback=lambda: dpg.show_item("glee.window.open_file_dialog"))
            dpg.add_menu_item(label="Save", enabled=False, tag="glee.menu.save", callback=dh.save_file)
            dpg.add_menu_item(label="Save as..", enabled=False, tag="glee.menu.save_as")
            dpg.add_menu_item(label="Close CSV File", callback=close_file_callback, enabled=False, tag="glee.menu.close_file")
            dpg.add_menu_item(label="Exit", callback=exit_app)
        with dpg.menu(label="Options", enabled=False):
            dpg.add_menu_item(label="Preferences")
            
    dpg.add_text("String", pos=(dpg.get_item_width("glee.main_window")/7.5,dpg.get_item_height("glee.main_window")/24))
    dpg.add_button(label="+", show=False, pos=(dpg.get_item_width("glee.main_window")/3.5,dpg.get_item_height("glee.main_window")/26), height=23, width=25, tag="glee.button.add_string", callback=add_string)
    dpg.add_text("No string selected", pos=(dpg.get_item_width("glee.main_window")/3.1,dpg.get_item_height("glee.main_window")/24), tag="glee.text.string_key")
    dpg.add_button(label=" Delete String ", show=False, pos=(dpg.get_item_width("glee.main_window")/1.125,dpg.get_item_height("glee.main_window")/26), height=23, tag="glee.button.delete_string", callback=remove_string_callback)
    dpg.add_text("Status:", pos=(dpg.get_item_width("glee.main_window")/96,dpg.get_item_width("glee.main_window")/1.565))
    dpg.add_text("No CSV file loaded", color=(255,238,0),tag="glee.text.status", pos=(dpg.get_item_width("glee.main_window")/16,dpg.get_item_width("glee.main_window")/1.565))
    dpg.add_child_window(width=dpg.get_viewport_width()/3.3, height=dpg.get_item_height("glee.main_window")/1.145, pos=(dpg.get_viewport_width()/96,dpg.get_viewport_width()/20), tag="glee.window.buttons")
    dpg.add_child_window(width=dpg.get_viewport_width()/1.5, height=dpg.get_item_height("glee.main_window")/1.145, pos=(dpg.get_viewport_width()/3.1,dpg.get_viewport_width()/20), tag="glee.window.edit")

dpg.bind_item_handler_registry("glee.main_window", "glee.handler.resize")

# Rest of the DPG setup
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
else:
    dpg.destroy_context()