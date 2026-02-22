from gui.widget import Widget
import dearpygui.dearpygui as dpg

class Titlebar(Widget):
    def __init__(self, on_exit: function, on_maxmin: function) -> None:
        super().__init__()
        self.on_exit: function = on_exit
        self.on_maxmin: function = on_maxmin
        
        with dpg.handler_registry():
            dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=self.drag_cb)
        
        with dpg.window(
            no_move=True,
            no_resize=True,
            no_title_bar=True,
            pos=[0, -70],
            no_scroll_with_mouse=True,
            no_scrollbar=True,
            height=100,
            width=dpg.get_viewport_width(),
            tag=f"{self.tag_prefix}titlebar"
            ) as self.drag_vp_wnd:
            with dpg.group(horizontal=True, tag=f"{self.tag_prefix}titlebar.group"):
                dpg.add_text("Glee Localization Editor", pos=(10, dpg.get_item_height(f"{self.tag_prefix}titlebar")-29), tag=f"{self.tag_prefix}titlebar.label")
                dpg.add_button(label="X", pos=(dpg.get_item_width(f"{self.tag_prefix}titlebar")-33, dpg.get_item_height(f"{self.tag_prefix}titlebar")-27), width=30, height=25, callback=self.on_exit, tag=f"{self.tag_prefix}titlebar.x")
                dpg.add_button(label="+", pos=(dpg.get_item_width(f"{self.tag_prefix}titlebar")-65, dpg.get_item_height(f"{self.tag_prefix}titlebar")-27), width=30, height=25, callback=self.on_maxmin, tag=f"{self.tag_prefix}titlebar.max") 
                # Maximizing and resizing is buggy as all hell. Not touching that rn.
                dpg.add_button(label="-", pos=(dpg.get_item_width(f"{self.tag_prefix}titlebar")-97, dpg.get_item_height(f"{self.tag_prefix}titlebar")-27), width=30, height=25, callback=self.on_maxmin, tag=f"{self.tag_prefix}titlebar.min")
                
    def drag_cb(self) -> None:
        vp_pos = dpg.get_viewport_pos()
        drag_delta = dpg.get_mouse_drag_delta()
        if any(dpg.is_item_active(i) for i in dpg.get_item_children(self.drag_vp_wnd, slot=1)):
            return

        if dpg.is_item_focused(self.drag_vp_wnd):
            dpg.set_viewport_pos([vp_pos[0] + drag_delta[0], vp_pos[1] + drag_delta[1]])