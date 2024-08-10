from Dialogs.Dialog import Dialog
import dearpygui.dearpygui as dpg
from Errors import *


class NewStringDialog(Dialog):
    def __init__(self, string_keys_list:list, callback=None, abort_callback=None) -> None:
        super().__init__(tag="glee.window.new_string_dialog",
                         width=500,
                         height=160,
                         no_close=False,
                         callback=callback,
                         abort_callback=abort_callback,
                         label="Add new String Key",
                         on_close=abort_callback
                         )
        self.string_keys_list = string_keys_list
        button_callback = lambda: self.callback(dpg.get_value(f"{self.tag}.string_key"),
                                                self.get_string_offset())
        
        # Define Dialog box
        dpg.add_input_text(label="String Key", hint="New String Key", width=300, tag=f"{self.tag}.string_key", parent=self.tag)
        dpg.add_radio_button(label="Insert", items=["Before","After"], default_value="After", parent=self.tag, tag=f"{self.tag}.radio")
        dpg.add_combo(default_value=dpg.get_value("glee.text.string_key"), items=[], tag=f"{self.tag}.combo", parent=self.tag)
        dpg.add_button(label="OK", pos=(self.width-95,self.height-30) ,callback=button_callback, parent=self.tag, tag=f"{self.tag}.OK")
        dpg.add_button(label="Cancel", pos=(self.width-60,self.height-30), callback=self.abort_callback, parent=self.tag)

        dpg.configure_item(f"{self.tag}.combo", items=string_keys_list)
        
    def get_string_offset(self) -> int:
        index_base = self.string_keys_list.index(dpg.get_value(f"{self.tag}.combo"))
        match dpg.get_value(f"{self.tag}.radio").lower():
            case "before":
                print(self.string_keys_list)
                return index_base
            case "after":
                return index_base + 1 