import dearpygui.dearpygui as dpg

class Dialog:
    def __init__(self, tag: str, width: int, height: int, no_close: bool = True, user_data = None, callback=None, abort_callback=None,**kwargs) -> None:
        dpg.add_window(
            width=width,
            height=height,
            tag=tag,
            show=True,
            no_resize=True,
            no_close=no_close,
            user_data=user_data,
            modal=True,
            **kwargs)
        self.tag = tag
        self.width = width
        self.height = height
        self.callback = callback
        self.abort_callback=abort_callback

# diky ondro