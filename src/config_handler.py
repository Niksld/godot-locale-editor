from loguru import logger as log

TAG_PREFIX = "glee."

class ConfigHandler:
    
    def __init__(self) -> None:
        pass
    
    def save_config(self) -> bool:
        raise NotImplementedError