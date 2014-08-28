# coding=utf-8
import unittest
from common.utilities.string_utilities import *

__author__ = 'jsternberg'

class StringUtilitiesTest(unittest.TestCase):

    def test_replace_words_in_string(self):

        self.assertEqual(replace_words_in_string("ham and spamalot",{"ham":"jam"}),"jam and spamalot")
        self.assertEqual(replace_words_in_string("ham and spamalot",{"ham":""})," and spamalot")


    def test_replace_word_in_string(self):

        self.assertEqual(replace_word_in_string("ham and spamalot","ham","jam"),"jam and spamalot")
        self.assertEqual(replace_word_in_string("ham and spamalot","ham","")," and spamalot")


    def test_remove_whitespace(self):

        self.assertEqual(remove_whitespace("okee dokee"),"okeedokee")
        self.assertEqual(remove_whitespace("okeedokee"),"okeedokee")


    def test_remove_punctuations(self):

        self.assertEqual(remove_punctuations(None),None)
        punctuations = ('.', '-', ')', '(', ',', '#', ':', '&')
        for p in punctuations:
            test_word = "spam" + p + "ham"
            self.assertEqual(remove_punctuations(test_word), "spam ham")


    def test_is_ascii(self):

        self.assertTrue(is_ascii("123456"))
        self.assertTrue(is_ascii("abcdefg"))
        self.assertTrue(is_ascii("abc def"))

        self.assertFalse(is_ascii(u"ab¢ def"))
        self.assertFalse(is_ascii("ab¢ def"))
        self.assertFalse(is_ascii(u"abcdef–ghi"))
        self.assertFalse(is_ascii(u"abcdefghi"))
        self.assertFalse(is_ascii(u"½⅞⅓⅔¾⅕⅛⅘"))
        self.assertFalse(is_ascii(u"Fred’s©™"))

        self.assertRaisesRegexp(TypeError, None, is_ascii, (None,))


    def test_module_name_to_class_name(self):

        munged = module_name_to_class_name("this_is_it")
        self.assertEqual(munged, "ThisIsIt")

        munged = module_name_to_class_name("thisisit")
        self.assertEqual(munged, "Thisisit")


    def test_underscore_to_title(self):

        munged = underscore_to_title("this_is_it")
        self.assertEqual(munged, "This Is It")

        munged = underscore_to_title("thisisit")
        self.assertEqual(munged, "Thisisit")

        # this is kind of weird behavior, but it's right if you think about it.
        munged = underscore_to_title("This Is It")
        self.assertEqual(munged, "This is it")

        munged = underscore_to_title("This_Is_It")
        self.assertEqual(munged, "This Is It")


    def test_titlecase(self):

        munged = titlecase("this is it")
        self.assertEqual(munged, "This Is It")

        munged = titlecase("This Is It")
        self.assertEqual(munged, "This Is It")


    def test_remove_leading_trailing_char(self):

        munged = remove_leading_trailing_char('"blah"','"')
        self.assertEqual(munged, 'blah')

        munged = remove_leading_trailing_char('blah','z')
        self.assertEqual(munged, 'blah')

        munged = remove_leading_trailing_char('"bl"ah"','"')
        self.assertEqual(munged, 'bl"ah')

        munged = remove_leading_trailing_char('blah','b')
        self.assertEqual(munged, 'lah')

        munged = remove_leading_trailing_char('blah','h')
        self.assertEqual(munged, 'bla')

if __name__ == '__main__':
    unittest.main()
