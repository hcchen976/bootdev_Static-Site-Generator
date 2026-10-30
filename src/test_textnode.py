import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_eq_false(self):
        node = TextNode("This is a text node?", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)
    
    def test_url_none(self):
        node = TextNode("This is a text node", TextType.BOLD, url = None)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_text_type_false(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node,node2)
    
    def test_repr(self):
        node = TextNode("some text", TextType.LINK, "https://bootdev.fakeurl.dev")
        self.assertEqual(
            "TextNode(some text, link, https://bootdev.fakeurl.dev)", repr(node)
        )

if __name__ == "__main__":
    unittest.main()
