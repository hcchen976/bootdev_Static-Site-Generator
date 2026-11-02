from __future__ import annotations

from enum import Enum
from typing import assert_never

from htmlnode import LeafNode


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

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    text_type = text_node.text_type
    match text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text, None)
        case TextType.BOLD:
            return LeafNode("b", text_node.text, None)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text, None)
        case TextType.CODE:
            return LeafNode("code", text_node.text, None)
        case TextType.LINK:
            if text_node.url is None:
                raise ValueError("LINK node requires a url")
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            if text_node.url is None:
                raise ValueError("IMAGE node requires a url")
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _ as unreachable:
            assert_never(unreachable)

