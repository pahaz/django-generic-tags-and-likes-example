from __future__ import unicode_literals, print_function, generators, division
import unittest
from django.test import TestCase
from tags.utils import parse_tag_input, join_tags

__author__ = 'pahaz'


class TestParseTagInput(TestCase):
    def test_with_simple_space_delimited_tags(self):
        self.assertEquals(parse_tag_input('one'), ['one'])
        self.assertEquals(parse_tag_input('one two'), ['one two'])
        self.assertEquals(parse_tag_input('one two three'),
                          ['one two three'])

    def test_with_simple_comma_delimited_tags(self):
        self.assertEquals(parse_tag_input(',one'), ['one'])
        self.assertEquals(parse_tag_input('Black, Vintage'),
                          ['Black', 'Vintage'])
        self.assertEquals(parse_tag_input(',one two'), ['one two'])
        self.assertEquals(parse_tag_input(',one two three'),
                          ['one two three'])
        self.assertEquals(parse_tag_input('a-one, a-two and a-three'),
                          ['a-one', 'a-two and a-three'])
        self.assertEquals(parse_tag_input('one, one, two, two'),
                          ['one', 'two'])

    @unittest.skip("Not implemented")
    def test_with_double_quoted_tags(self):
        self.assertEquals(parse_tag_input('"one'), ['"one'])
        self.assertEquals(parse_tag_input('"one two'), ['"one two'])
        self.assertEquals(parse_tag_input('"one two three'),
                          ['one two three'])
        self.assertEquals(parse_tag_input('"one two"'), ['one two'])
        self.assertEquals(parse_tag_input('a-one "a-two and a-three"'),
                          ['a-one "a-two and a-three"'])

    @unittest.skip("Not implemented")
    def test_with_no_loose_commas(self):
        self.assertEquals(parse_tag_input('one two "thr,ee"'),
                          ['one', 'two', 'thr,ee'])

    @unittest.skip("Not implemented")
    def test_with_loose_commas(self):
        self.assertEquals(parse_tag_input('"one", two three'),
                          ['one', 'two three'])

    @unittest.skip("Not implemented")
    def test_tags_with_double_quotes_can_contain_commas(self):
        self.assertEquals(parse_tag_input('a-one "a-two, and a-three"'),
                          ['a-one', 'a-two, and a-three'])
        self.assertEquals(parse_tag_input('"two", one, one, two, "one"'),
                          ['two', 'one'])

    def test_with_naughty_input(self):
        self.assertEquals(parse_tag_input(None), [])
        self.assertEquals(parse_tag_input(''), [])
        self.assertEquals(parse_tag_input(',,,,,,'), [])

    @unittest.skip("Not implemented")
    def test_with_naughty_input_with_commas(self):
        self.assertEquals(parse_tag_input('"'), [])
        self.assertEquals(parse_tag_input('""'), [])
        self.assertEquals(parse_tag_input('"' * 7), [])
        self.assertEquals(parse_tag_input('",",",",",",","'), [','])
        self.assertEquals(parse_tag_input('a-one "a-two" and "a-three'),
                          ['a-one', 'a-two', 'and', 'a-three'])


class TestJoinTags(TestCase):
    def test_simple_join_tags(self):
        self.assertEquals(join_tags(['one']), 'one')
        self.assertEquals(join_tags(['one', 'two']), 'one, two')
        self.assertEquals(join_tags(['one', 'two', '3']), 'one, two, 3')
        self.assertEquals(join_tags(['Black', 'Vintage']), 'Black, Vintage')

    def test_simple_join_tags_with_space(self):
        self.assertEquals(join_tags(['one two']), 'one two')
        self.assertEquals(join_tags(['one two', '3']), 'one two, 3')

    @unittest.skip("Not implemented")
    def test_with_commas(self):
        self.assertEquals(join_tags(['one', 'two', 'thr,ee']),
                          'one, two, "thr,ee"')

    @unittest.skip("Not implemented")
    def test_with_commas_and_double_quote(self):
        self.assertEquals(join_tags(['a-one', 'a-two, "Super"']),
                          'a-one, \'a-two, "Super"\'')
        self.assertEquals(join_tags(['a-one', 'a-"two, Super"']),
                          'a-one, \'a-"two, Super"\'')

    def test_with_naughty_input(self):
        self.assertEquals(join_tags(None), '')
        self.assertEquals(join_tags([]), '')
