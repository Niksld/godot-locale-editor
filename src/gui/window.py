from abc import abstractmethod
from gui.widget import Widget

class Window(Widget):
    """ Abstract base class for Windows"""
    
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod
    def show(self) -> None:
        pass
    
    @abstractmethod
    def hide(self) -> None:
        pass