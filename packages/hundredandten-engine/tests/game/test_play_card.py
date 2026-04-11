"""Test behavior of the Game when playing a card"""

from unittest import TestCase

from hundredandten.deck import CardNumber, CardSuit, SelectableSuit
from hundredandten.engine.actions import Play
from hundredandten.engine.constants import (
    HAND_SIZE,
    Status,
)
from hundredandten.engine.deck import Card
from hundredandten.engine.errors import HundredAndTenError
from hundredandten.engine.player import player_after
from hundredandten.testing import arrange


class TestPlayCard(TestCase):
    """Unit tests for playing a card in a trick"""

    def test_non_trick_game(self):
        """A game not ready for tricks has no active trick"""

        game = arrange.game(Status.BIDDING)

        self.assertRaises(HundredAndTenError, lambda: game.active_round.active_trick)

    def test_play_first_card_of_round(self):
        """The player after the bidder plays the first card of the round"""

        game = arrange.game(Status.TRICKS)

        assert game.active_round.active_bidder
        self.assertEqual(
            game.active_round.active_player,
            player_after(
                game.active_round.players, game.active_round.active_bidder.identifier
            ),
        )

        original_active_player = game.active_round.active_player
        play = Play(original_active_player.identifier, original_active_player.hand[0])

        game.act(play)

        self.assertEqual(HAND_SIZE - 1, len(original_active_player.hand))
        self.assertNotIn(play.card, original_active_player.hand)
        self.assertNotEqual(original_active_player, game.active_round.active_player)
        self.assertEqual(play, game.actions[-1])

    def test_cannot_play_twice_in_a_trick(self):
        """Each person can only play once per trick"""

        game = arrange.game(Status.TRICKS)

        active_player = game.active_round.active_player
        play = Play(active_player.identifier, active_player.hand[0])

        game.act(play)
        self.assertRaises(HundredAndTenError, game.act, play)

    def test_cannot_play_other_players_card(self):
        """A player can only play their own cards"""

        game = arrange.game(Status.TRICKS)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Play(
                game.active_round.active_player.identifier,
                game.active_round.inactive_players[0].hand[0],
            ),
        )

    def test_cannot_play_non_trump_when_bleeding(self):
        """A player can only play trumps while the trick is bleeding"""

        game = arrange.game(Status.TRICKS)
        assert game.active_round.trump

        non_trump = next(
            s for s in iter(SelectableSuit) if s != game.active_round.trump
        )

        active_player = game.active_round.active_player
        next_player = player_after(game.active_round.players, active_player.identifier)

        # overwrite to ensure this trick will bleed
        active_player.hand[0] = Card(
            CardNumber.TEN, CardSuit[game.active_round.trump.value]
        )
        # overwrite to ensure next player breaks rules
        next_player.hand = [Card(CardNumber.TWO, CardSuit[non_trump.value])] * 4 + [
            Card(CardNumber.NINE, CardSuit[game.active_round.trump.value])
        ]

        self.assertFalse(game.active_round.active_trick.bleeding)

        game.act(Play(active_player.identifier, active_player.hand[0]))

        self.assertTrue(game.active_round.active_trick.bleeding)

        self.assertRaises(
            HundredAndTenError,
            game.act,
            Play(
                game.active_round.active_player.identifier,
                game.active_round.active_player.hand[0],
            ),
        )

    def test_can_play_non_trump_when_bleeding(self):
        """A player can play non-trumps while the trick is bleeding if they have no trumps"""

        game = arrange.game(Status.TRICKS)
        assert game.active_round.trump

        non_trump = next(
            s for s in iter(SelectableSuit) if s != game.active_round.trump
        )

        active_player = game.active_round.active_player
        next_player = player_after(game.active_round.players, active_player.identifier)

        # overwrite to ensure this trick will bleed
        active_player.hand[0] = Card(
            CardNumber.TEN, CardSuit[game.active_round.trump.value]
        )
        # overwrite to ensure next player breaks rules
        next_player.hand = [Card(CardNumber.TWO, CardSuit[non_trump.value])] * 5

        self.assertFalse(game.active_round.active_trick.bleeding)

        game.act(Play(active_player.identifier, active_player.hand[0]))

        self.assertTrue(game.active_round.active_trick.bleeding)

        game.act(
            Play(
                game.active_round.active_player.identifier,
                game.active_round.active_player.hand[0],
            )
        )

        self.assertTrue(game.active_round.active_trick.bleeding)
        self.assertEqual(2, len(game.active_round.active_trick.plays))

    def test_play_through_trick(self):
        """A new trick is created after all players have played"""

        game = arrange.game(Status.TRICKS, arrange.play_trick)

        winning_play = game.active_round.tricks[-2].winning_play

        self.assertEqual(2, len(game.active_round.tricks))
        self.assertEqual(
            winning_play.identifier, game.active_round.active_player.identifier
        )

    def test_play_through_round(self):
        """A new round is created after all tricks are played"""

        game = arrange.game(Status.TRICKS, arrange.play_round)

        self.assertEqual(2, len(game.rounds))

    def test_all_cards_available_when_not_bleeding(self):
        """Any card can be played when not bleeding"""

        game = arrange.game(Status.TRICKS)

        self.assertEqual(5, len(game.available_actions(game.active_player.identifier)))
        self.assertTrue(
            all(
                isinstance(a, Play)
                for a in game.available_actions(game.active_player.identifier)
            )
        )

    def test_only_trumps_when_bleeding(self):
        """Only trump cards can be played while the trick is bleeding"""

        game = arrange.game(Status.TRICKS)
        assert game.active_round.trump

        non_trump = next(
            s for s in iter(SelectableSuit) if s != game.active_round.trump
        )

        active_player = game.active_round.active_player
        next_player = player_after(game.active_round.players, active_player.identifier)

        # overwrite to ensure this trick will bleed
        active_player.hand[0] = Card(
            CardNumber.TEN, CardSuit[game.active_round.trump.value]
        )
        # overwrite to ensure next player breaks rules
        next_player.hand = [
            Card(CardNumber.TWO, CardSuit[non_trump.value]),
            Card(CardNumber.THREE, CardSuit[non_trump.value]),
            Card(CardNumber.FOUR, CardSuit[non_trump.value]),
            Card(CardNumber.SEVEN, CardSuit[game.active_round.trump.value]),
            Card(CardNumber.EIGHT, CardSuit[game.active_round.trump.value]),
        ]

        game.act(Play(active_player.identifier, active_player.hand[0]))
        self.assertTrue(game.active_round.active_trick.bleeding)

        self.assertEqual(2, len(game.available_actions(game.active_player.identifier)))
