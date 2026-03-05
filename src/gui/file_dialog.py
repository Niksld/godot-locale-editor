from gui.window import Window
from loguru import logger

import dearpygui.dearpygui as dpg
import DataHandler as dh

class FileDialog(Window):
    def __init__(self, 
                title:str = "Open file", 
                width: int = 400, 
                height:int = 300, 
                file_types: list[str]=["*.*"]):
        super().__init__()
        
        # File Dialog
        with dpg.file_dialog(label=title, directory_selector=False, show=False, callback=self.create_dialog_csv_properties, id="glee.window.file_dialog", width=width ,height=height, modal=True, default_path=dh.get_last_path()):
            for extension in file_types:
                dpg.add_file_extension(extension, color=(0, 255, 0, 255), custom_text=f"[{extension if extension != '*.*' else 'All files'}]")
        dpg.show_item("glee.window.file_dialog")
        
    def create_dialog_csv_properties(se, appdata):
        if dh.file_exists(appdata):
            logger.debug("Creating CSV Properties dialog")
            update_status("Getting CSV properties...",1)
            dpg.split_frame()
            CsvPropertiesDialog(callback=lambda s, a, data:(dh.set_csv_properties(s, a, data), create_ui(se,appdata), dpg.delete_item("glee.window.csv_properties_dialog")),
                                abort_callback=lambda:(dh.reset(), dpg.delete_item("glee.window.csv_properties_dialog"), hide_edit_buttons()),
                            )
            
    def show(self) -> None:
        dpg.show_item("glee.window.file_dialog")
    def hide(self) -> None:
        dpg.delete_item("glee.window.file_dialog")