"""Tests for hundredandten-deck"""

from unittest import TestCase

from hundredandten.deck import (
    Card,
    CardInfo,
    CardNumber,
    CardSuit,
    Deck,
    SelectableSuit,
    bleeds,
    card_info,
    defined_cards,
    trumps,
)


class TestCardEnums(TestCase):
    """Unit tests for card enum types"""

    def test_card_suit_members(self):
        """CardSuit contains all expected suits"""
        suits = {s.value for s in CardSuit}
        self.assertIn("HEARTS", suits)
        self.assertIn("CLUBS", suits)
        self.assertIn("SPADES", suits)
        self.assertIn("DIAMONDS", suits)
        self.assertIn("JOKER", suits)

    def test_selectable_suit_members(self):
        """SelectableSuit contains only the four non-joker suits"""
        suits = {s.value for s in SelectableSuit}
        self.assertEqual(suits, {"HEARTS", "CLUBS", "SPADES", "DIAMONDS"})
        self.assertNotIn("JOKER", suits)

    def test_card_number_members(self):
        """CardNumber contains all expected values"""
        numbers = {n.value for n in CardNumber}
        self.assertIn("JOKER", numbers)
        self.assertIn("ACE", numbers)
        self.assertIn("TWO", numbers)
        self.assertEqual(len(numbers), 14)

    def test_suit_cross_type_equality(self):
        """CardSuit and SelectableSuit compare equal when values match (_Suit.__eq__)"""
        self.assertEqual(CardSuit.HEARTS, SelectableSuit.HEARTS)
        self.assertEqual(CardSuit.CLUBS, SelectableSuit.CLUBS)
        self.assertNotEqual(CardSuit.HEARTS, SelectableSuit.CLUBS)

    def test_suit_cross_type_hash(self):
        """CardSuit and SelectableSuit have matching hashes when values match"""
        self.assertEqual(hash(CardSuit.HEARTS), hash(SelectableSuit.HEARTS))
        self.assertEqual(hash(CardSuit.SPADES), hash(SelectableSuit.SPADES))

    def test_suit_not_equal_to_non_enum(self):
        """_Suit.__eq__ returns NotImplemented for non-Enum types"""
        result = CardSuit.HEARTS.__eq__("HEARTS")
        self.assertEqual(result, NotImplemented)


class TestCardInfo(TestCase):
    """Unit tests for CardInfo dataclass"""

    def test_card_info_creation(self):
        """CardInfo stores trump_value, weak_trump_value, and always_trump"""
        info = CardInfo(trump_value=5, weak_trump_value=3)
        self.assertEqual(info.trump_value, 5)
        self.assertEqual(info.weak_trump_value, 3)
        self.assertFalse(info.always_trump)

    def test_card_info_always_trump(self):
        """CardInfo always_trump flag works"""
        info = CardInfo(trump_value=10, weak_trump_value=10, always_trump=True)
        self.assertTrue(info.always_trump)


class TestCard(TestCase):
    """Unit tests for Card"""

    def test_card_repr(self):
        """Card __repr__ is human readable"""
        card = Card(CardNumber.ACE, CardSuit.HEARTS)
        self.assertNotIn("Card", repr(card))
        self.assertIn("ACE", repr(card))
        self.assertIn("HEARTS", repr(card))

    def test_joker_always_trump(self):
        """Joker is always trump"""
        joker = Card(CardNumber.JOKER, CardSuit.JOKER)
        self.assertTrue(joker.always_trump)

    def test_ace_of_hearts_always_trump(self):
        """Ace of Hearts is always trump"""
        ace_of_hearts = Card(CardNumber.ACE, CardSuit.HEARTS)
        self.assertTrue(ace_of_hearts.always_trump)

    def test_regular_card_not_always_trump(self):
        """A regular card is not always trump"""
        two_of_clubs = Card(CardNumber.TWO, CardSuit.CLUBS)
        self.assertFalse(two_of_clubs.always_trump)

    def test_trump_value_red_number_card(self):
        """Trump value for red number card comes from card_info"""
        card = Card(CardNumber.FIVE, CardSuit.HEARTS)
        self.assertEqual(
            card.trump_value, card_info[CardSuit.HEARTS][CardNumber.FIVE].trump_value
        )

    def test_trump_value_five_is_fourteen(self):
        """Five has trump_value of 14 (highest) in all suits"""
        for suit in (
            CardSuit.HEARTS,
            CardSuit.DIAMONDS,
            CardSuit.SPADES,
            CardSuit.CLUBS,
        ):
            card = Card(CardNumber.FIVE, suit)
            self.assertEqual(card.trump_value, 14)

    def test_trump_value_jack_is_thirteen(self):
        """Jack has trump_value of 13 in all suits"""
        for suit in (
            CardSuit.HEARTS,
            CardSuit.DIAMONDS,
            CardSuit.SPADES,
            CardSuit.CLUBS,
        ):
            card = Card(CardNumber.JACK, suit)
            self.assertEqual(card.trump_value, 13)

    def test_trump_value_joker_is_twelve(self):
        """Joker has trump_value of 12"""
        joker = Card(CardNumber.JOKER, CardSuit.JOKER)
        self.assertEqual(joker.trump_value, 12)

    def test_trump_value_black_number_card(self):
        """Trump value for black number card (reversed ordering) from card_info"""
        card = Card(CardNumber.TWO, CardSuit.SPADES)
        self.assertEqual(
            card.trump_value, card_info[CardSuit.SPADES][CardNumber.TWO].trump_value
        )

    def test_weak_trump_value(self):
        """Weak trump value comes from card_info"""
        card = Card(CardNumber.THREE, CardSuit.DIAMONDS)
        self.assertEqual(
            card.weak_trump_value,
            card_info[CardSuit.DIAMONDS][CardNumber.THREE].weak_trump_value,
        )

    def test_card_frozen(self):
        """Card is immutable (frozen dataclass)"""
        card = Card(CardNumber.ACE, CardSuit.SPADES)
        with self.assertRaises((AttributeError, TypeError)):
            card.number = CardNumber.TWO  # type: ignore[misc]


class TestDefinedCards(TestCase):
    """Unit tests for defined_cards"""

    def test_defined_cards_length(self):
        """There are exactly 53 defined cards (52 + Joker)"""
        self.assertEqual(len(defined_cards), 53)

    def test_defined_cards_contains_joker(self):
        """defined_cards contains the Joker"""
        joker = Card(CardNumber.JOKER, CardSuit.JOKER)
        self.assertIn(joker, defined_cards)

    def test_defined_cards_contains_ace_of_hearts(self):
        """defined_cards contains Ace of Hearts"""
        ace_of_hearts = Card(CardNumber.ACE, CardSuit.HEARTS)
        self.assertIn(ace_of_hearts, defined_cards)


class TestDeck(TestCase):
    """Unit tests for Deck"""

    def test_card_repr_override(self):
        """Card representation via deck draw is human readable"""
        deck = Deck()
        self.assertFalse("Card" in str(deck.draw(1)[0]))

    def test_shuffling_without_seed(self):
        """Shuffling without the same seed produces different results"""
        deck_1 = Deck()
        deck_2 = Deck()
        self.assertNotEqual(deck_1.draw(53), deck_2.draw(53))

    def test_shuffling_with_seed(self):
        """Shuffling with the same seed produces the same result"""
        seed = "deck-test-seed"
        self.assertEqual(Deck(seed).draw(53), Deck(seed).draw(53))

    def test_draw_happy_path(self):
        """draw(n) returns n distinct cards and advances pulled"""
        deck = Deck()
        first = deck.draw(5)
        second = deck.draw(5)
        self.assertNotEqual(first, second)
        self.assertEqual(deck.pulled, 10)

    def test_draw_zero(self):
        """draw(0) returns an empty list"""
        deck = Deck()
        self.assertEqual(deck.draw(0), [])
        self.assertEqual(deck.pulled, 0)

    def test_draw_raises_on_negative(self):
        """draw with a negative amount raises ValueError"""
        deck = Deck()
        with self.assertRaises(ValueError):
            deck.draw(-1)

    def test_draw_raises_on_overdraw_at_once(self):
        """draw past the full deck at once raises ValueError"""
        deck = Deck()
        with self.assertRaises(ValueError):
            deck.draw(54)

    def test_draw_raises_on_overdraw_incrementally(self):
        """draw past the full deck in steps raises ValueError"""
        deck = Deck()
        deck.draw(53)
        with self.assertRaises(ValueError):
            deck.draw(1)

    def test_initialize_with_pulled(self):
        """Initializing with pulled skips cards consistently"""
        amt = 5
        deck_1 = Deck()
        deck_2 = Deck(seed=deck_1.seed, pulled=amt)
        deck_1.draw(amt)
        self.assertEqual(deck_1.draw(amt), deck_2.draw(amt))


class TestTrumps(TestCase):
    """Unit tests for trumps()"""

    def test_returns_only_trump_cards(self):
        """trumps() returns only cards matching trump suit or always-trump"""
        hand = [
            Card(CardNumber.ACE, CardSuit.HEARTS),  # always trump
            Card(CardNumber.TWO, CardSuit.SPADES),  # trump suit
            Card(CardNumber.TWO, CardSuit.HEARTS),  # non-trump (SPADES is trump)
            Card(CardNumber.JOKER, CardSuit.JOKER),  # always trump
        ]
        result = trumps(hand, SelectableSuit.SPADES)
        self.assertIn(Card(CardNumber.ACE, CardSuit.HEARTS), result)
        self.assertIn(Card(CardNumber.TWO, CardSuit.SPADES), result)
        self.assertIn(Card(CardNumber.JOKER, CardSuit.JOKER), result)
        self.assertNotIn(Card(CardNumber.TWO, CardSuit.HEARTS), result)

    def test_returns_empty_when_no_trumps(self):
        """trumps() returns empty when hand has no trump cards"""
        hand = [
            Card(CardNumber.TWO, CardSuit.HEARTS),
            Card(CardNumber.THREE, CardSuit.DIAMONDS),
        ]
        result = trumps(hand, SelectableSuit.CLUBS)
        self.assertEqual(list(result), [])

    def test_always_trump_included_regardless_of_suit(self):
        """Ace of Hearts and Joker are always included regardless of trump suit"""
        hand = [
            Card(CardNumber.ACE, CardSuit.HEARTS),
            Card(CardNumber.JOKER, CardSuit.JOKER),
        ]
        for suit in SelectableSuit:
            result = list(trumps(hand, suit))
            self.assertEqual(len(result), 2)

    def test_trumps_with_none_returns_only_always_trump(self):
        """trumps(hand, None) returns only always-trump cards (Ace of Hearts, Joker)"""
        hand = [
            Card(CardNumber.ACE, CardSuit.HEARTS),  # always trump
            Card(CardNumber.JOKER, CardSuit.JOKER),  # always trump
            Card(CardNumber.FIVE, CardSuit.SPADES),  # not always trump
            Card(CardNumber.TWO, CardSuit.CLUBS),  # not always trump
        ]
        result = trumps(hand, None)
        self.assertIn(Card(CardNumber.ACE, CardSuit.HEARTS), result)
        self.assertIn(Card(CardNumber.JOKER, CardSuit.JOKER), result)
        self.assertNotIn(Card(CardNumber.FIVE, CardSuit.SPADES), result)
        self.assertNotIn(Card(CardNumber.TWO, CardSuit.CLUBS), result)


class TestBleeds(TestCase):
    """Unit tests for bleeds()"""

    def test_bleeds_for_matching_suit(self):
        """bleeds() returns True when card suit matches trump"""
        card = Card(CardNumber.TWO, CardSuit.CLUBS)
        self.assertTrue(bleeds(card, SelectableSuit.CLUBS))

    def test_bleeds_for_always_trump(self):
        """bleeds() returns True for always-trump cards"""
        ace_of_hearts = Card(CardNumber.ACE, CardSuit.HEARTS)
        joker = Card(CardNumber.JOKER, CardSuit.JOKER)
        self.assertTrue(bleeds(ace_of_hearts, SelectableSuit.SPADES))
        self.assertTrue(bleeds(joker, SelectableSuit.DIAMONDS))

    def test_does_not_bleed_for_non_trump(self):
        """bleeds() returns False for non-trump, non-always-trump cards"""
        card = Card(CardNumber.TWO, CardSuit.HEARTS)
        self.assertFalse(bleeds(card, SelectableSuit.CLUBS))
