from __future__ import annotations

from enum import Enum


class TextType(Enum):
    
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    
    def __init__(self, text: str, text_type: TextType, url: str | None = None) -> None:
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str | None = url

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, TextNode):
            return NotImplemented
            
        return self.text == obj.text and self.text_type == obj.text_type and self.url == obj.url
    
    def __repr__(self) -> str:
        r_string = f"TextNode({self.text}, {self.text_type.value}, {self.url})"
        return r_string