from window import Window
import dearpygui.dearpygui as dpg


class FileDialog(Window):
    def __init__(self):
        super().__init__()
        
        # File Dialog
        with dpg.file_dialog(label="Open file", directory_selector=False, show=False, callback=self.create_dialog_csv_properties, id="glee.window.open_file_dialog", width=700 ,height=400, modal=True, default_path=dh.get_last_path()):
            dpg.add_file_extension(".csv", color=(0, 255, 0, 255), custom_text="[CSV]")

    def create_dialog_csv_properties(se, appdata):
        if dh.file_exists(appdata):
            logger.debug("Creating CSV Properties dialog")
            update_status("Getting CSV properties...",1)
            dpg.split_frame()
            CsvPropertiesDialog(callback=lambda s, a, data:(dh.set_csv_properties(s, a, data), create_ui(se,appdata), dpg.delete_item("glee.window.csv_properties_dialog")),
                                abort_callback=lambda:(dh.reset(), dpg.delete_item("glee.window.csv_properties_dialog"), hide_edit_buttons()),
                            )