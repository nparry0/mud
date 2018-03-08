import pytest
from character import Stat, StatTable


class TestStat:

    ADD = 0
    REM = 1

    @pytest.mark.parametrize("starting_base,mods,expected_base,expected_modified", [
        (20, [], 20, 20),
        (20, [(ADD, 10, False)],                                                        20, 30),
        (20, [(ADD, 10, False), (ADD, 5, False), (ADD, -12, False)],                    20, 23),
        (20, [(ADD, -15, False), (ADD, -15, False)],                                    20, 0),
        (20, [(ADD, 10, False), (ADD, 5, False), (ADD, -12, False), (REM, 10, False)],  20, 13),
        (20, [(ADD, 0.5, True)],                                                        20, 30),
        (20, [(ADD, 0.5, True), (ADD, 0.2, True), (ADD, -0.3, True)],                   20, 28),
        (20, [(ADD, -0.6, True), (ADD, -0.6, True)],                                    20, 0),
        (20, [(ADD, 0.5, True), (ADD, 0.2, True), (ADD, -0.3, True), (REM, 0.2, True)], 20, 24),
        (3,  [(ADD, 0.5, True)],                                                        3, 5),  # round up
        (3,  [(ADD, 0.4, True)],                                                        3, 4),  # round down
        (20, [(ADD, 10, False),  (REM, 20, False)],                                     20, 30),  # remove nothing
    ])
    def test_stat(self, starting_base, mods, expected_base, expected_modified):
        stat = Stat(starting_base)
        for mod in mods:
            if mod[0] == TestStat.ADD:
                stat.add_modifier(mod[1], mod[2])
            else:
                stat.remove_modifier(mod[1], mod[2])
        assert stat.base == expected_base
        assert stat.modified == expected_modified

    def test_multi_add_remove(self):
        stat = Stat(20)

        def check_stat(expected_base, expected_modified):
            assert stat.base == expected_base
            assert stat.modified == expected_modified

        stat.add_modifier(0.5, True)
        check_stat(20, 30)
        stat.add_modifier(-0.3, True)
        check_stat(20, 24)
        stat.add_modifier(15, False)
        check_stat(20, 42)
        stat.add_modifier(-5, False)
        check_stat(20, 36)
        stat.remove_modifier(300, False)  # Shouldn't do anything
        check_stat(20, 36)
        stat.remove_modifier(0.5, True)
        check_stat(20, 21)
        stat.remove_modifier(-5, False)
        check_stat(20, 25)
        stat.remove_modifier(15, False)
        check_stat(20, 14)
        stat.remove_modifier(-0.3, True)
        check_stat(20, 20)


class TestStatTable:

    @pytest.mark.parametrize("starting,mods,expects", [
        # Basic test
        (
            {Stat.SPEED: 1, Stat.INTELLIGENCE: 2},
            [],
            [(Stat.STRENGTH, 0), (Stat.SPEED, 1), (Stat.INTELLIGENCE, 2)]
        ),
        # Test combined
        (
            {Stat.STRENGTH: 1, Stat.MELEE: 1},
            [],
            [(Stat.STRENGTH, 1), (Stat.MELEE, 2)],
        ),
        # Combined and modified
        (
            {Stat.INTELLIGENCE: 10, Stat.STRENGTH: 10, Stat.MELEE: 10},
            [
                (Stat.INTELLIGENCE, 10, False),
                (Stat.INTELLIGENCE, .5, True),
                (Stat.STRENGTH, -5, False),
                (Stat.STRENGTH, .5, True),
                (Stat.MELEE, 20, False),
                (Stat.MELEE, -.7, True),
            ],
            [(Stat.INTELLIGENCE, 30), (Stat.STRENGTH, 8), (Stat.MELEE, 17)]
        )
    ])
    def test_get_combined_modified(self, starting, mods, expects):
        table = StatTable(starting)
        for mod in mods:
            table._stats[mod[0]].add_modifier(mod[1], mod[2])
        for expect in expects:
            actual = table.get_combined_modified(expect[0])
            assert actual == expect[1], '{}: expected {}, but got {}'.format(Stat.names[expect[0]], expect[1], actual)

    @pytest.mark.parametrize("starting,expected", [
        (
           {},
           [
               Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
               Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME
           ]
        ),
        (
            {Stat.CAST_FLAME: 4},
            [
                Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
                Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME
            ]
        ),
        (
            {Stat.CAST_FLAME: 5},
            [
                Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
                Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME,
                Stat.CAST_HEAL
            ]
        ),
        (
            {Stat.CAST_FLAME: 5, Stat.CAST_HEAL: 4},
            [
                Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
                Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME,
                Stat.CAST_HEAL
            ]
        ),
        (
            {Stat.CAST_FLAME: 5, Stat.CAST_HEAL: 5},
            [
                Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
                Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME,
                Stat.CAST_HEAL, Stat.CAST_CHILL
            ]
        ),
        (
            {Stat.CAST_FLAME: 5, Stat.MELEE: 9},
            [
                Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
                Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME,
                Stat.CAST_HEAL
            ]
        ),
        (
            {Stat.CAST_FLAME: 5, Stat.MELEE: 10},
            [
                Stat.STRENGTH, Stat.SPEED, Stat.INTELLIGENCE,
                Stat.MELEE, Stat.RANGED, Stat.CAST_FLAME,
                Stat.CAST_HEAL, Stat.CAST_FLAMING_SWORD
            ]
        ),
    ])
    def test_get_available_stats(self, starting, expected):
        table = StatTable(starting)
        actual = table.get_available_stats()
        actual.sort()
        expected.sort()
        assert actual == expected
