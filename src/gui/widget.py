from abc import ABC, abstractmethod
from config_handler import TAG_PREFIX

class Widget(ABC):
    """ Abstract base class for Widgets"""
    tag_prefix: str = TAG_PREFIX