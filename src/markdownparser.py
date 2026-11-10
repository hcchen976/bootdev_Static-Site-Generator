import re
from enum import Enum

from htmlnode import HTMLNode, ParentNode
from textnode import TextNode, TextType, text_node_to_html_node


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


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
            if part == "":
                continue
            kind = text_type if i % 2 == 1 else TextType.TEXT
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
    list_str = [string.strip("\n") for string in list_str]
    list_str = [string.strip() for string in list_str]
    list_str = list(filter(None, list_str))
    return list_str


def block_to_block_type(block: str) -> BlockType:
    if re.search(r"^#{1,6} ", block):
        return BlockType.HEADING
    if re.search(r"^```\n", block) and re.search(r"```$", block):
        return BlockType.CODE
    if re.search(r"^>", block):
        lines = block.split("\n")
        if all(re.search(r"^>", line) for line in lines):
            return BlockType.QUOTE
    if re.search(r"^- ", block):
        lines = block.split("\n")
        if all(re.search(r"^- ", line) for line in lines):
            return BlockType.UNORDERED_LIST
    if re.search(r"^\d+\. ", block):
        lines = block.split("\n")
        is_valid = all(
            re.search(rf"^{i}\. ", line) for i, line in enumerate(lines, start=1)
        )
        if is_valid:
            return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH


def markdown_to_html_node(markdown: str) -> HTMLNode:
    blocks = markdown_to_blocks(markdown=markdown)
    list_children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            list_children.append(paragraph_to_html_node(block))
        if block_type == BlockType.HEADING:
            list_children.append(heading_to_html_node(block))
        if block_type == BlockType.CODE:
            list_children.append(code_to_html_node(block))
        if block_type == BlockType.QUOTE:
            list_children.append(quote_to_html_node(block))
        if block_type == BlockType.UNORDERED_LIST:
            list_children.append(ulist_to_html_node(block))
        if block_type == BlockType.ORDERED_LIST:
            list_children.append(olist_to_html_node(block))
    return ParentNode(tag="div", children=list_children)


def paragraph_to_html_node(block: str) -> HTMLNode:
    lines = block.split("\n")
    text = " ".join(lines)
    nodes = text_to_textnodes(text)
    children: list[HTMLNode] = []
    for node in nodes:
        children.append(text_node_to_html_node(node))
    return ParentNode(tag="p", children=children)


def heading_to_html_node(block):
    match = re.search(r"^(#{1,6}) ", block)
    if match is None:
        raise AttributeError
    hashes = match.group(1)
    level = hashes.count("#")
    text = block[match.end() :]
    children: list[HTMLNode] = [
        text_node_to_html_node(n) for n in text_to_textnodes(text)
    ]
    return ParentNode(tag=f"h{level}", children=children)


def code_to_html_node(block: str):
    block = block.removeprefix("```\n").removesuffix("```")
    interim_node = TextNode(text=block, text_type=TextType.CODE)
    code_node = text_node_to_html_node(interim_node)
    return ParentNode(tag="pre", children=[code_node])


def quote_to_html_node(block: str):
    lines = block.split("\n")
    quote_strings = []
    for line in lines:
        line = line.lstrip("> ")
        quote_strings.append(line)
    quote = "\n".join(quote_strings)
    nodes = text_to_textnodes(quote)
    children: list[HTMLNode] = [text_node_to_html_node(node) for node in nodes]
    return ParentNode(tag="blockquote", children=children)


def ulist_to_html_node(block: str):
    lines = block.split("\n")
    html_nodes: list[HTMLNode] = []
    for line in lines:
        line = line[2:]
        text_nodes = text_to_textnodes(line)
        leafs: list[HTMLNode] = []
        for node in text_nodes:
            leafs.append(text_node_to_html_node(node))
        html_nodes.append(ParentNode(tag="li", children=leafs))
    return ParentNode(tag="ul", children=html_nodes)


def olist_to_html_node(block):
    lines = block.split("\n")
    html_nodes: list[HTMLNode] = []
    for line in lines:
        line = re.sub(pattern=r"^\d+\. ", repl="", string=line)
        text_nodes = text_to_textnodes(line)
        leafs: list[HTMLNode] = []
        for node in text_nodes:
            leafs.append(text_node_to_html_node(node))
        html_nodes.append(ParentNode(tag="li", children=leafs))
    return ParentNode(tag="ol", children=html_nodes)
