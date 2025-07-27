from loguru import logger
from gui.gui import GUI

import dearpygui.dearpygui as dpg
import DataHandler as dh

logger.debug("Starting Glee...")

gui = GUI()

#dh.data_load() # Attempt to load last path
#dh.load_icons()

# Viewport

# Rest of the DPG setup
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()
else:
    dpg.destroy_context()