from Dialogs.Dialog import Dialog
import dearpygui.dearpygui as dpg

class CsvPropertiesDialog(Dialog):
    def __init__(self, callback=None, abort_callback=None) -> None:
        super().__init__(tag="glee.window.csv_properties_dialog",
                         width=400,
                         height=250,
                         no_close=True,
                         user_data=None,
                         callback=callback,
                         abort_callback=abort_callback
                         )
        
        self.delimiters = {
            "Semicolon":";",
            "Comma":",",
            "Tab":" "
        }
        
        # Define Dialog box
        
        # nějakej img vlevo nahoru
        dpg.add_text("Select CSV properties\n\nIf you don't know what anything here means, try the defaults or ask your devs.", parent=self.tag)
        dpg.add_combo(label="Delimiter", items=["Semicolon", "Comma","Tab"], default_value="Semicolon", tag=f"{self.tag}.delimiter", parent=self.tag)
        dpg.add_input_text(label="Quote Character", default_value="|", no_spaces=True, tag=f"{self.tag}.quote", parent=self.tag)
        dpg.add_combo(label="Dialect", items=["excel"], default_value="excel", tag=f"{self.tag}.dialect", parent=self.tag)
        dpg.add_button(label="OK", pos=(300,230) ,callback=self.callback, user_data={"delimiter":dpg.get_value(f"{self.tag}.delimiter"), "quote":f"{self.tag}.quote", "dialect":f"{self.tag}.dialect"}, parent=self.tag)
        dpg.add_button(label="Cancel", pos=(350,230), callback=self.abort_callback, parent=self.tag)
        