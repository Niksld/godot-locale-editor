from loguru import logger as log
from gui.window import Window

import dearpygui.dearpygui as dpg

class MainWindow(Window):
    
    def __init__(self) -> None:
        super().__init__()
        
        with dpg.window(label="", width=dpg.get_viewport_width(), height=dpg.get_viewport_height()-30, no_move=True, no_collapse=True, no_resize=True, no_title_bar=True, pos=(0,30), tag="glee.main_window"):
            with dpg.menu_bar():
                with dpg.menu(label="File"):
                    dpg.add_menu_item(label="Load locale .csv", callback=lambda: dpg.show_item("glee.window.open_file_dialog"))
                    dpg.add_menu_item(label="Save", enabled=False, tag="glee.menu.save", callback=lambda: print("dh.save_file()"))
                    dpg.add_menu_item(label="Save as..", enabled=False, tag="glee.menu.save_as")
                    dpg.add_menu_item(label="Close CSV File", callback=lambda: print("close_file_callback"), enabled=False, tag="glee.menu.close_file")
                    dpg.add_menu_item(label="Exit", callback=lambda: print("exit_app"))
                with dpg.menu(label="Options", enabled=True):
                    dpg.add_menu_item(label="Preferences", callback=lambda: (dpg.show_item('glee.window.preferences')))
                    
            dpg.add_text("String", pos=(dpg.get_item_width("glee.main_window")/7.5,dpg.get_item_height("glee.main_window")/24))
            dpg.add_button(label="+", show=False, pos=(dpg.get_item_width("glee.main_window")/3.5,dpg.get_item_height("glee.main_window")/26), height=23, width=25, tag="glee.button.add_string", callback=lambda: print("add_string"))
            dpg.add_text("No string selected", pos=(dpg.get_item_width("glee.main_window")/3.1,dpg.get_item_height("glee.main_window")/24), tag="glee.text.string_key")
            dpg.add_button(label=" Delete String ", show=False, pos=(dpg.get_item_width("glee.main_window")/1.125,dpg.get_item_height("glee.main_window")/26), height=23, tag="glee.button.delete_string", callback=lambda: print("remove_string_callback"))
            dpg.add_text("Status:", pos=(dpg.get_item_width("glee.main_window")/96,dpg.get_item_width("glee.main_window")/1.565))
            dpg.add_text("No CSV file loaded", color=(255,238,0),tag="glee.text.status", pos=(dpg.get_item_width("glee.main_window")/16,dpg.get_item_width("glee.main_window")/1.565))
            dpg.add_child_window(width=dpg.get_viewport_width()/3.3, height=dpg.get_item_height("glee.main_window")/1.145, pos=(dpg.get_viewport_width()/96,dpg.get_viewport_width()/20), tag="glee.window.buttons")
            dpg.add_child_window(width=dpg.get_viewport_width()/1.5, height=dpg.get_item_height("glee.main_window")/1.145, pos=(dpg.get_viewport_width()/3.1,dpg.get_viewport_width()/20), tag="glee.window.edit")
            
            dpg.bind_item_handler_registry("glee.main_window", "glee.handler.resize")
            
    def create_ui(self, s, appdata) -> None:
        global locale_csv, button_list
        """
        if  dh.load_file(appdata):
            generate_buttons(dh.locale_csv)
            generate_input_fields()
            open_locale_for(button_list[0], None)
            dpg.configure_item(f"{self.tag_prefix}.menu.close_file",enabled=True)
            dpg.set_viewport_title(f"{dh.VIEWPORT_LABEL} - {list(appdata['selections'].keys())[0]}")
            show_edit_buttons() """
            
    def show_edit_buttons(self) -> None:
        dpg.show_item(f"{self.tag_prefix}button.add_string")
        dpg.show_item(f"{self.tag_prefix}.button.delete_string")
    
    def hide_edit_buttons(self) -> None:
        dpg.hide_item(f"{self.tag_prefix}.button.add_string")
        dpg.hide_item(f"{self.tag_prefix}.button.delete_string")
        
    def show(self) -> None:
        pass
    
    def hide(self) -> None:
        pass
    
    def generate_buttons(csv: dict) -> None:
        """Generates buttons for each string key""" 
        global button_list
        log.debug("Creating buttons")
        if button_list != []:
            button_list = []
        for i in enumerate(csv.items()):
            key = i[1][0]
            
            if key[0] == "#" or key == "keys" or i[0] == 0:
                log.debug("Commment or header found, skipping...")
                continue
            
            if "[img]" in key:
                log.debug("Found Image tag in text, replacing with image if able (TODO)")
                pass # TODO
            
            # Label could be customized, but we still have to get the item name somehow. thus tag and label
            dpg.add_button(label=key, tag=f"glee.loaded_string.{key}",width=270, height=25, parent="glee.window.buttons", callback=open_locale_for)
            button_list.append(key) 

    def regenerate_buttons():
        scroll_amount = dpg.get_y_scroll("glee.window.buttons")
        log.debug("Regenerating buttons...")
        for item in dpg.get_item_children("glee.window.buttons")[1]:
            dpg.delete_item(item)
        
        #generate_buttons(dh.locale_csv)
        dpg.set_y_scroll("glee.window.buttons",scroll_amount)
                
    def generate_input_fields():
        """Generates input field for each language"""
        global languages
        log.debug("Creating input fields ...")
        """
        if dh.locale_languages == None:
            log.error("Locale header is none when generating input fields, cant generate...")
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
"""
"""
    def update_translation(sender, new_string, data):
        global locale_csv, letter_workaround
        
        # Workaround because DPG has a bug with input_text and Latin ext. characters 
        if any(letter in new_string for letter in list(letter_workaround.keys())):
            for corrupt_letter, correct_letter in letter_workaround.items():
                new_string = new_string.replace(corrupt_letter, correct_letter)
                
        dh.locale_csv[data["locale_string"]][data["lang_index"]] = new_string  
        dpg.set_value(sender, new_string)
        display_warnings_or_errors(dpg.get_value("glee.text.string_key"))
        """
"""
    def add_string():
        if not dh.is_file_loaded():
            log.debug("No file loaded, creating new empty CSV")
            log.debug("Not yet implemented, sorry!")
            # TODO
            # pop-up dialog to setup CSV file (dialect, filename and path)
            # pop-up dialog to setup languages
            # pop-up new key dialog
        else:
            log.debug("Adding new string...")
            try:
                NewStringDialog(button_list, 
                                callback=lambda new_key, position:string_dialog_callback(new_key, position),
                                abort_callback=lambda:(dpg.delete_item("glee.window.new_string_dialog"))
                                )
            except NoStringKeyError:
                log.error("No String Key supplied")
            except TakenStringKeyError:
                log.error("String Key is already registered!")
            
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
                
    def display_warnings_or_errors(string: str):
        if dpg.does_item_exist("glee.main_window.issue_tracker"):
            dpg.delete_item("glee.main_window.issue_tracker")
            dpg.delete_item("glee.main_window.issue_tracker.tooltip")
            dpg.split_frame(delay=1)
            
        issues = dh.get_warnings_or_errors(string)
        if issues is None:
            logger.debug("None found!")
            return
        
        dpg.add_image("glee.icon.warning" if len(issues["err"]) == 0 else "glee.icon.error", tag="glee.main_window.issue_tracker", height=32, width=32, parent="glee.main_window", pos=(dpg.get_item_width("glee.main_window")/3.1+len(dpg.get_value("glee.text.string_key"))*7,dpg.get_item_height("glee.main_window")/32))
        with dpg.tooltip(parent="glee.main_window.issue_tracker", tag="glee.main_window.issue_tracker.tooltip"):
            for messages in issues.values():
                if type(messages) == list:
                    for message in messages:
                        dpg.add_text(message)
                else:
                    dpg.add_text(messages)
                    
    def string_dialog_callback(new_key, position):
        dh.add_new_string_key(new_key, position)
        dpg.delete_item("glee.window.new_string_dialog")
        regenerate_buttons()
        
    def remove_string(string: str):
        logger.debug(f"Removing String Key '{string}'")
        if not string in button_list:
            logger.error("Attempting to remove non-existant string key.")
            return
        
        button_last_position = button_list.index(string)
        dh.remove_string_key(string)
        regenerate_buttons()
        open_locale_for(button_list[button_last_position], None)
"""