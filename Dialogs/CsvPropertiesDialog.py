from Dialogs.Dialog import Dialog
import dearpygui.dearpygui as dpg

class CsvPropertiesDialog(Dialog):
    def __init__(self, callback=None, abort_callback=None) -> None:
        super().__init__(tag="glee.window.csv_properties_dialog",
                         width=300,
                         height=220,
                         no_close=False,
                         callback=callback,
                         abort_callback=abort_callback,
                         label="Select CSV properties",
                         on_close=abort_callback
                         )
        
        self.delimiters = {
            "Semicolon":";",
            "Comma":",",
            "Tab":" "
        }
        
        set_csv_callback = lambda x:(
            self.callback(None, None, {"delimiter":self.delimiters[dpg.get_value(f"{self.tag}.delimiter")], 
                                       "quote":dpg.get_value(f"{self.tag}.quote"), 
                                       "dialect":dpg.get_value(f"{self.tag}.dialect")}),)
        
        # Define Dialog box
        # nějakej img vlevo nahoru
        dpg.add_text("If you're unsure about these settings, try opening the CSV in notepad.\n\n\n", parent=self.tag, wrap=self.width-25)
        dpg.add_combo(label="Delimiter", items=["Semicolon", "Comma","Tab"], width=100, default_value="Semicolon", tag=f"{self.tag}.delimiter", parent=self.tag)
        dpg.add_input_text(label="Quote Character", default_value="|", width=100, no_spaces=True, tag=f"{self.tag}.quote", parent=self.tag)
        dpg.add_combo(label="Dialect", items=["excel"], width=100, default_value="excel", tag=f"{self.tag}.dialect", parent=self.tag)
        dpg.add_button(label="OK", pos=(self.width-95,self.height-30) ,callback=set_csv_callback, parent=self.tag, tag=f"{self.tag}.OK")
        dpg.add_button(label="Cancel", pos=(self.width-60,self.height-30), callback=self.abort_callback, parent=self.tag)
