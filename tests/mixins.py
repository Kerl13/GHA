import unittest

from writer.common import RichTextList, RichTextMixin


class RichInt(RichTextMixin):
    TEMPLATE = "{(n: int)}"

    def __init__(self, n):
        assert isinstance(n, int)
        self.n = n


class TestRichTextList(unittest.TestCase):
    def setUp(self):
        self.list = list(RichInt(x) for x in range(20))
        self.rich_list = RichTextList(self.list)

    def test_length(self):
        self.assertEqual(len(self.rich_list), len(self.list))

    def test_access(self):
        self.assertEqual(self.rich_list[7], self.list[7])

    def test_slice(self):
        slices = [
            (self.rich_list[:5], self.list[:5]),
            (self.rich_list[7:], self.list[7:]),
            (self.rich_list[:-6], self.list[:-6]),
            (self.rich_list[-13:], self.list[-13:])
        ]

        for iut, gold in slices:
            self.assertIsInstance(iut, RichTextList)
            self.assertEqual(iut.lines, gold)
