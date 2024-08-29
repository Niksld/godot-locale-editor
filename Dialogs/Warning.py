from Dialogs.Dialog import Dialog
import dearpygui.dearpygui as dpg

class Warning(Dialog):
    def __init__(self,label: str = "Warning", msg: str = None, callback=None, abort_callback=None) -> None:
        super().__init__(tag="glee.window.warning",
                         width=450,
                         height=120,
                         no_close=False,
                         callback=callback,
                         abort_callback=abort_callback,
                         label=label,
                         on_close=abort_callback
                         )
        
        # Define Dialog box
        # nějakej img vlevo nahoru
        dpg.add_image("glee.icon.warning", parent=self.tag, pos=(10,25), width=70, height=70)
        dpg.add_text(f"{msg}", parent=self.tag, wrap=self.width-25, pos=(100,35))
        dpg.add_button(label="Yes", pos=(self.width-100,self.height-35), width=40, height=25 ,callback=self.callback, parent=self.tag)
        dpg.add_button(label="No", pos=(self.width-50,self.height-35),width=40, height=25, callback=self.abort_callback, parent=self.tag)
        
        dpg.focus_item(self.tag)
