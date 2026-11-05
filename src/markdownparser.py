import re

from textnode import TextNode, TextType


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    list_new_node: list[TextNode] = []
    for part in old_nodes:
        if part.text_type != TextType.TEXT:
            list_new_node.append(part)
            continue
        parts = part.text.split(sep=delimiter)

        if len(parts) % 2 == 0:
            raise Exception("no closing delimiter!")  # ruff: ignore[raise-vanilla-class]

        for i, part in enumerate(parts):
            if part == "":  # fix: odd index number are the target, evens are plain text, should loop by step=2
                continue
            kind = text_type if i % 2== 1 else TextType.TEXT
            list_new_node.append(TextNode(text=part, text_type=kind, url=None))
    return list_new_node

def extract_markdown_images(text: str) -> list[str] | list[tuple[str, str]]:
    matches = re.findall(r"!\[(.*?)\]\((.*?)\)", text)
    return matches

def extract_markdown_links(text: str) -> list[str] | list[tuple[str, str]]:
    matches = re.findall(r"(?<!!)\[(.*?)\]\((.*?)\)", text)
    return matches


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list_nodes: list[TextNode] = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_list_nodes.append(node)
            continue
        remaining = node.text
        for alt, url in extract_markdown_images(node.text):
            before, remaining = remaining.split(f"![{alt}]({url})", 1)
            if before != "":
                new_list_nodes.append(TextNode(before, TextType.TEXT))
            new_list_nodes.append(TextNode(alt, TextType.IMAGE, url))
        if remaining != "":
            new_list_nodes.append(TextNode(remaining, TextType.TEXT))
    return new_list_nodes

def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_list_nodes: list[TextNode] = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_list_nodes.append(node)
            continue
        remaining = node.text
        for href, url in extract_markdown_links(node.text):
            before, remaining = remaining.split(f"[{href}]({url})", 1)
            if before != "":
                new_list_nodes.append(TextNode(before, TextType.TEXT))
            new_list_nodes.append(TextNode(href, TextType.LINK, url))
        if remaining != "":
            new_list_nodes.append(TextNode(remaining, TextType.TEXT))
    return new_list_nodes

def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

    
def markdown_to_blocks(markdown: str) -> list[str]:
    list_str = markdown.split("\n\n")
    list_str = [string.strip("\n") for string in list_str ]
    list_str = [string.strip() for string in list_str]
    list_str = list(filter(None, list_str))
    return list_str