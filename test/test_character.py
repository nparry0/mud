from unittest import TestCase
from character import Stat


class TestStat(TestCase):
    def test_no_mod(self):
        stat = Stat(20)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 20)

    # Numbers
    def test_number_mod(self):
        stat = Stat(20)
        stat.add_modifier(10, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 30)

    def test_multi_number_mod(self):
        stat = Stat(20)
        stat.add_modifier(10, False)
        stat.add_modifier(5, False)
        stat.add_modifier(-12, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 23)

    def test_number_mod_below_zero(self):
        stat = Stat(20)
        stat.add_modifier(-15, False)
        stat.add_modifier(-15, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 0)

    def test_multi_number_remove_mod(self):
        stat = Stat(20)
        stat.add_modifier(10, False)
        stat.add_modifier(5, False)
        stat.add_modifier(-12, False)
        stat.remove_modifier(10, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 13)

    # Percents
    def test_percent_mod(self):
        stat = Stat(20)
        stat.add_modifier(0.5, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 30)

    def test_multi_percent_mod(self):
        stat = Stat(20)
        stat.add_modifier(0.5, True)
        stat.add_modifier(0.2, True)
        stat.add_modifier(-0.3, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 28)

    def test_percent_mod_below_zero(self):
        stat = Stat(20)
        stat.add_modifier(-0.6, True)
        stat.add_modifier(-0.6, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 0)

    def test_multi_percent_remove_mod(self):
        stat = Stat(20)
        stat.add_modifier(0.5, True)
        stat.add_modifier(0.2, True)
        stat.add_modifier(-0.3, True)
        stat.remove_modifier(0.2, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 24)

    def test_percent_round_up(self):
        stat = Stat(3)
        stat.add_modifier(0.5, True)
        self.assertEqual(stat.get_base(), 3)
        self.assertEqual(stat.get_modified(), 5)

    def test_percent_round_down(self):
        stat = Stat(3)
        stat.add_modifier(0.4, True)
        self.assertEqual(stat.get_base(), 3)
        self.assertEqual(stat.get_modified(), 4)

    # Both numbers and percents
    def test_remove_nothing(self):
        stat = Stat(20)
        stat.add_modifier(10, False)
        stat.remove_modifier(20, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 30)

    def test_multi_add_remove(self):
        stat = Stat(20)

        stat.add_modifier(0.5, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 30)

        stat.add_modifier(-0.3, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 24)

        stat.add_modifier(15, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 42)

        stat.add_modifier(-5, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 36)

        stat.remove_modifier(300, False) # Shouldn't do anything
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 36)

        stat.remove_modifier(0.5, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 21)

        stat.remove_modifier(-5, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 25)

        stat.remove_modifier(15, False)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 14)

        stat.remove_modifier(-0.3, True)
        self.assertEqual(stat.get_base(), 20)
        self.assertEqual(stat.get_modified(), 20)
