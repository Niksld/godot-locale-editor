import dearpygui.dearpygui as dpg

class Preferences:
    def __init__(self) -> None:
        self.width = dpg.get_viewport_width()-10
        self.height = dpg.get_viewport_height()-100
        self.tag = "glee.window.preferences"
        self.default_settings = {
                "General":{"Test Value":1},
                "Layout": {
                            "Resolution":[1000,700],
                            "Test Value":2
                        },
                "Locale": {"Language":"en"}
            }
        self.settings = self.default_settings
        
        self.settings_widgets = {
            "General": {
                "Test Value": lambda: dpg.add_input_int(label="Test Value", default_value=1, parent="glee.window.preferences.settings", width=dpg.get_item_width("glee.window.preferences.settings")-300)
            },
            "Layout": {
                "Resolution": lambda: dpg.add_combo(label="Resolution",items=["1000x700","1500x1050"], default_value=0, parent="glee.window.preferences.settings", width=dpg.get_item_width("glee.window.preferences.settings")-300),
                "Test Value": lambda: dpg.add_drag_int(label="Test Value",default_value=2, width=dpg.get_item_width("glee.window.preferences.settings")-300, parent="glee.window.preferences.settings")
            },
            "Locale": {
                "Language": lambda: dpg.add_combo(items=["en","cs"], default_value="en", label="Language", parent="glee.window.preferences.settings", width=dpg.get_item_width("glee.window.preferences.settings")-300)
            }
        }
        
        dpg.add_int_value
        
        with dpg.window(
            width=self.width,
            height=self.height,
            tag=self.tag,
            show=False,
            no_resize=True,
            no_move=True,
            modal=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
            label="Preferences",
            pos=(5,30),
            ):
        
        # Define Dialog box
        # nějakej img vlevo nahoru
            with dpg.child_window(parent=self.tag, width=self.width/6, height=self.height/1.125, pos=(10,35),tag=f"glee.window.preferences.categories"):
                for category in self.default_settings.keys():
                    dpg.add_button(label=str(category), width=self.width/6-15, tag=f"glee.window.preferences.category_button.{str(category)}", callback=self.load_category)
            
            dpg.add_child_window(parent=self.tag, width=self.width/1.2, height=self.height/1.125, tag="glee.window.preferences.settings", pos=(30+dpg.get_item_width("glee.window.preferences.categories"),35))
        
        dpg.focus_item(self.tag)
        
    def load_category(self, sender, app_data):
        category = sender.split(".")[-1]
        # delete previous children if they exist
        for item in dpg.get_item_children("glee.window.preferences.settings")[1]:
            dpg.delete_item(item)
            
        # populate the window with new widgets
        for setting in self.default_settings[category]:
            self.settings_widgets[str(category)][str(setting)]()
            
        