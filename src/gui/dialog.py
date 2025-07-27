from widget import Widget

import dearpygui.dearpygui as dpg

class Dialog(Widget):
    def __init__(self, tag: str, width: int, height: int, label:str, no_close: bool = True, on_close: function | None = None, callback=None, abort_callback=None,**kwargs) -> None:
        dpg.add_window(
            width=width,
            height=height,
            tag=tag,
            show=True,
            no_resize=True,
            no_close=no_close,
            modal=True,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
            label=label,
            on_close=on_close, # type: ignore
            pos=[int(dpg.get_viewport_width()/2-width/2), int(dpg.get_viewport_height()/2-height/2)],
            **kwargs)
        self.tag = tag
        self.width = width
        self.height = height
        self.callback = callback
        self.abort_callback=abort_callback

# diky ondro