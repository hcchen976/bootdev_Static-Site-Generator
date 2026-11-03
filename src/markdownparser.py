from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    list_new_node: list[TextNode] = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            list_new_node.append(node)
            continue
        parts = node.text.split(sep=delimiter)

        if len(parts) % 2 == 0:
            raise Exception("no closing delimiter!")  # ruff: ignore[raise-vanilla-class]
        
        list_new_node.append(TextNode(text=parts.pop(0), text_type=TextType.TEXT, url=None))
        for split_node in parts:
            if split_node != "": #fix: odd index number are the target, evens are plain text, should loop by step=2
                if parts.index(split_node) % 2 == 0:
                    list_new_node.append(TextNode(text=split_node, text_type=text_type, url=None)) 
                else:
                    list_new_node.append(TextNode(text=split_node, text_type=TextType.TEXT, url=None))
            else:
                continue
    return list_new_node


