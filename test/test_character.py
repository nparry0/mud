from unittest import TestCase
from character import Stat, StatTable


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

        stat.remove_modifier(300, False)  # Shouldn't do anything
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


class TestStatTable(TestCase):

    def test_init(self):
        table = StatTable({
            Stat.STAT_SPEED: 1,
            Stat.STAT_INTELLIGENCE: 2,
        })
        self.assertEqual(table.get_combined_modified(Stat.STAT_STRENGTH), 0)
        self.assertEqual(table.get_combined_modified(Stat.STAT_SPEED), 1)
        self.assertEqual(table.get_combined_modified(Stat.STAT_INTELLIGENCE), 2)

    def test_combined(self):
        table = StatTable({
            Stat.STAT_STRENGTH: 1,
            Stat.STAT_MELEE: 1
        })
        self.assertEqual(table.get_combined_modified(Stat.STAT_STRENGTH), 1)
        self.assertEqual(table.get_combined_modified(Stat.STAT_MELEE), 2)

    def test_combined_modified(self):
        table = StatTable({
            Stat.STAT_INTELLIGENCE: 10,
            Stat.STAT_STRENGTH: 10,
            Stat.STAT_MELEE: 10
        })

        table.stats[Stat.STAT_INTELLIGENCE].add_modifier(10, False)
        table.stats[Stat.STAT_INTELLIGENCE].add_modifier(.5, True)
        table.stats[Stat.STAT_STRENGTH].add_modifier(-5, False)
        table.stats[Stat.STAT_STRENGTH].add_modifier(.5, True)
        table.stats[Stat.STAT_MELEE].add_modifier(20, False)
        table.stats[Stat.STAT_MELEE].add_modifier(-.7, True)

        self.assertEqual(table.get_combined_modified(Stat.STAT_INTELLIGENCE), 30)
        self.assertEqual(table.get_combined_modified(Stat.STAT_STRENGTH), 8)
        self.assertEqual(table.get_combined_modified(Stat.STAT_MELEE), 17)

    def test_get_available_stats(self):
        table = StatTable()
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
        ])

    def test_get_available_stats_not_at_level(self):
        table = StatTable()
        table.stats[Stat.STAT_CAST_FLAME].value += 4
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
        ])

    def test_get_available_stats_at_level(self):
        table = StatTable()
        table.stats[Stat.STAT_CAST_FLAME].value += 5
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
            Stat.STAT_CAST_HEAL
        ])

    def test_get_available_stats_deep_not_at_level(self):
        table = StatTable()
        table.stats[Stat.STAT_CAST_FLAME].value += 5
        table.stats[Stat.STAT_CAST_HEAL].value += 4
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
            Stat.STAT_CAST_HEAL
        ])

    def test_get_available_stats_deep_at_level(self):
        table = StatTable()
        table.stats[Stat.STAT_CAST_FLAME].value += 5
        table.stats[Stat.STAT_CAST_HEAL].value += 5
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
            Stat.STAT_CAST_HEAL, Stat.STAT_CAST_CHILL
        ])

    def test_get_available_stats_wide_not_at_level(self):
        table = StatTable()
        table.stats[Stat.STAT_CAST_FLAME].value += 5
        table.stats[Stat.STAT_MELEE].value += 9
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
            Stat.STAT_CAST_HEAL
        ])

    def test_get_available_stats_wide_at_level(self):
        table = StatTable()
        table.stats[Stat.STAT_CAST_FLAME].value += 5
        table.stats[Stat.STAT_MELEE].value += 10
        self.assertItemsEqual(table.get_available_stats(), [
            Stat.STAT_STRENGTH, Stat.STAT_SPEED, Stat.STAT_INTELLIGENCE,
            Stat.STAT_MELEE, Stat.STAT_RANGED, Stat.STAT_CAST_FLAME,
            Stat.STAT_CAST_HEAL, Stat.STAT_CAST_FLAMING_SWORD
        ])
