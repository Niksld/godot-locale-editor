from typing import List
from loguru import logger as log
from config_handler import ConfigHandler

import DataHandler as dh
import dearpygui.dearpygui as dpg
from gui.main_window import MainWindow
from gui.titlebar import Titlebar
from gui.error import Error

class GUI:
    
    def __init__(self, width: int = 1000, height: int = 730, min_dims: List[int,int] = [500, 400]) -> None:
        
        self.width: int  = width
        self.height: int = height
        self.min_dims: List[int, int] = min_dims
        
        dpg.create_context()
        
        # Set Font + Unicode characters
        with dpg.font_registry():
            with dpg.font("src/fonts/ubuntu/Ubuntu-R.ttf", 16) as ubuntu_reg:
                dpg.add_font_range(0x0100, 0x25ff)
            dpg.bind_font(ubuntu_reg)

        with dpg.handler_registry():
            dpg.add_key_down_handler(dpg.mvKey_LControl, callback=self.shortcut_handler)
            
        # Handle resizing
        with dpg.item_handler_registry(tag="glee.handler.resize"):
            dpg.add_item_resize_handler(callback=self.on_resize)
            
        
        dpg.create_viewport(title=f'{dh.VIEWPORT_LABEL}', width=self.width, height=self.height, min_width=self.min_dims[0], min_height=self.min_dims[1], decorated=False)
        self.titlebar = Titlebar(self.exit_app, self.toggle_windowed_max)
        self.main_window = MainWindow()
        
    def shortcut_handler(self) -> None:
        """	 Handles keyboard shortcuts.
        
        ### Args:
            None  
        ### Returns:
            None
        """
        if dpg.is_key_pressed(dpg.mvKey_S):
            dh.save_file()
            
    def open_locale_for(item_string: str, a: dict) -> None:
        """
        Opens locale for given item string
        
        Args:
            item_string (str): sender, their tags correspond to item strings in the CSV
            appdata (Any): DearPyGui argument
        """
        global locale_csv
        
        item_string = item_string.removeprefix("glee.loaded_string.")    
        log.debug(f"Switching to string '{item_string}'")
        dpg.set_value("glee.text.string_key", item_string) # Set title for right pane to item string
        
        for index, lang in enumerate(dh.locale_languages):
            dpg.set_value(f"glee.locale_field.{lang}", dh.locale_csv[item_string][index])
            dpg.configure_item(f"glee.locale_field.{lang}", hint=dh.locale_csv[item_string][index])
            dpg.set_item_user_data(f"glee.locale_field.{lang}", {"locale_string":item_string,"language":dh.locale_languages[index], "lang_index":index})
        
        display_warnings_or_errors(item_string)
    
    def exit_app(self, x):
        log.debug("Got request to end app")
        if dh.file_changed():
            log.debug("File dialog here!") # popup file dialog to save
        else:
            log.debug("File didnt change, no need to save!")
        exit(0)
        
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
        
    def toggle_windowed_max():
        global is_maximized, unmaximized_res, viewport_max_size, unmaximized_pos
        log.debug(f"Changing window to {'maximized' if not is_maximized else 'windowed'} mode")
        
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
    
    def on_resize(self, x):
        print(x)
        
        mouse_pos = dpg.get_mouse_pos()
        print(mouse_pos)
        if mouse_pos[1] in range(0,20) or mouse_pos[1] in range(-30,-20):
            dpg.set_item_height("glee.main_window", dpg.get_viewport_height())
            dpg.set_item_pos("glee.main_window", (0,30))
            dpg.split_frame(delay=1)
            return
        
        log.debug(f"Resizing window! vp_size: [{dpg.get_viewport_width()}, {dpg.get_viewport_height()}]  w_size: [{dpg.get_item_width('glee.main_window')},{dpg.get_item_height('glee.main_window')}]")
        
        new_size = (dpg.get_item_width("glee.main_window"), dpg.get_item_height("glee.main_window"))
        
        if new_size[0] < self.min_dims[0]:
            dpg.set_viewport_width(self.min_dims[0])
        else:
            dpg.set_viewport_width(new_size[0])
            
        if new_size[1] < self.min_dims[1]:
            dpg.set_viewport_height(self.min_dims[1]+30)
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
        
    def show_error(self, msg: str, callback=lambda: dpg.delete_item("glee.window.error")) -> None:
        Error(label="Error", msg=msg, callback=callback)
        