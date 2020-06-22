import unittest
import unittest.mock as mock
import random
from unittest.mock import patch

from flash_cards.flash_cards import FlashCards

class FlashCardsTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = FlashCards('file.json')

    # тестируем поведение add_word при неподходящих входных данных
    def test_flashcards_incorrect_add_word_input(self):
        for name, parsed_name in [
            (('watermelon', 'watermelon'), ('Cyrillic word is expected')),
            (('яблоко', 'apple'), ('яблоко already in the dictionaty'))]:
            self.assertEqual(self.parser.add_word(name[0], name[1]), parsed_name)
        words = ['яблоко', 'хурма', 'арбуз']
        self.parser.add_word('Арбуз', 'watermelon')
        self.assertEqual(self.parser._words, words)

    # тестируем поведение delete_word при неподходящих входных данных
    def test_flashcards_incorrect_delete_word_input(self):
        for name, parsed_name in [
            ('watermelon', 'Cyrillic word is expected'),
            ('виноград', 'виноград not in the dictionary'),
            ('яблоко', 'яблоко succesfully deleted')]:
            self.assertEqual(self.parser.delete_word(name), parsed_name)

    # тестируем поведение delete_word при неправильном типе входных данных
    def test_flashcard_delete_word_error(self):
        self.assertRaises(TypeError, self.parser.delete_word, 123)

    # тестируем поведение add_word при неправильном типе входных данных
    def test_flashcard_add_word_error(self):
        self.assertRaises(TypeError, self.parser.add_word, (123, 132))

    # тестируем атрибут words
    def test_flashcard_words(self):
        self.assertEqual(self.parser._words, ['яблоко', 'хурма'])

    # тестируем play()
    @patch('builtins.input')
    def test_play(self, mocked_input):
        random.seed(3741)
        mocked_input.side_effect = ['apple', 'persimmon']
        result = self.parser.play()
        self.assertEqual(result, 'Done! 2 of 2 words correct.')

    # # тестируем play()
    # @patch('builtins.input', return_value='apple')
    # def test_play(self):
    #   def my_random(values):
    #     return 'яблоко', 'хурма'
    #   with mock.patch('random.shuffle', my_random):
    #     def test_flashcard_play(self, mock_input):
    #       result = self.parser.play()
    #       self.assertEqual(result, 'Done! 2 of 2 words correct.')


# запустить все тесты
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)  # colab