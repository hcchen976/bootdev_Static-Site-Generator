from textnode import TextNode, TextType


def main():
    text_obj = TextNode("This is some anchor text", TextType.LINK, "https://bootdev.dev")
    print(text_obj)
if __name__ == "__main__":
    main()