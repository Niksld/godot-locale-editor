import dearpygui.dearpygui as dpg
from loguru import logger

def update_status(message: str, severity: str | int = None) -> None:
    """
    Update status of the app
    message - str: message to display
    severity - List[str, int] - color the text by severity name or number.
    \n0 - low / 4 - very high
    """
    color = None
    
    if not dpg.is_dearpygui_running():
        logger.debug(f"Cannot update status! DPG not yet started...\nMessage:\n{message}")
        return
    
    match severity:
        case "very high" | 4:
            color = [255,0,0]
        case "high" | 3:
            color = [255,94,0]
        case "medium" | 2:
            color = [245,114,0]
        case "low" | 1:
            color = [255,238,0]
        case "success" | -1:
            color = [0,255,0]
        case _:
            color = [255,255,255]

    dpg.set_value("glee.text.status", message)
    dpg.configure_item("glee.text.status", color=color)
