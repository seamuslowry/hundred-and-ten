"""Test behavior of GameState.from_game(game, )"""

from unittest import TestCase

from hundredandten.engine.actions import Bid, Discard, Play

from hundredandten.engine.constants import (
    HAND_SIZE,
    BidAmount,
    RoundStatus,
)
from hundredandten.engine.deck import defined_cards
from hundredandten.automation.state import (
    GameState,
    CompletedTrick,
    Discarded,
    InHand,
    Played,
    Unknown,
    AutomatedBid,
    AutomatedDiscard,
    AutomatedSelectTrump,
    AutomatedPlay
)
from hundredandten.testing import arrange

SEED = "test-game-state-seed"


class TestGameStateBidding(TestCase):
    """Tests for game_state_for during the BIDDING phase"""

    def test_status_is_bidding(self):
        """State reflects bidding status"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.status, RoundStatus.BIDDING)

    def test_num_players(self):
        """State reflects the number of players"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.num_players, 4)

    def test_self_is_seat_zero(self):
        """The requesting player is always seat 0"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        for player in game.active_round.players:
            state = GameState.from_game(game, player.identifier)
            # self is always seat 0 — verified through hand matching
            self.assertEqual(state.hand, tuple(player.hand))

    def test_dealer_seat_relative(self):
        """Dealer seat is relative to the requesting player"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        dealer = game.active_round.dealer
        players = game.active_round.players
        dealer_index = players.index(dealer)

        for i, player in enumerate(players):
            state = GameState.from_game(game, player.identifier)
            expected_dealer_seat = (dealer_index - i) % len(players)
            self.assertEqual(state.dealer_seat, expected_dealer_seat)

    def test_hand_matches_player(self):
        """Hand in state matches the requesting player's actual hand"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        for player in game.active_round.players:
            state = GameState.from_game(game, player.identifier)
            self.assertEqual(state.hand, tuple(player.hand))
            self.assertEqual(len(state.hand), HAND_SIZE)

    def test_cards_has_53_entries(self):
        """Card knowledge always has 53 entries"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(len(state.cards), 53)

    def test_own_hand_cards_are_in_hand(self):
        """Player's own cards show as InHand"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        in_hand_cards = [
            ck.card for ck in state.cards if isinstance(ck.status, InHand)]
        self.assertCountEqual(in_hand_cards, list(active.hand))

    def test_other_cards_are_unknown(self):
        """Cards not in player's hand are Unknown"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        unknown_cards = [
            ck for ck in state.cards if isinstance(ck.status, Unknown)]
        self.assertEqual(len(unknown_cards), 53 - HAND_SIZE)

    def test_no_bidder_during_bidding(self):
        """bidder_seat is None during bidding"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertIsNone(state.bidder_seat)

    def test_bid_history_empty_at_start(self):
        """No bids placed yet"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(len(state.bid_history), 0)

    def test_active_bid_none_at_start(self):
        """No active bid yet"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertIsNone(state.active_bid)

    def test_trump_none_during_bidding(self):
        """Trump is not yet selected"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertIsNone(state.trump)

    def test_no_tricks_during_bidding(self):
        """No tricks have been played"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(len(state.completed_tricks), 0)
        self.assertEqual(len(state.current_trick_plays), 0)

    def test_available_actions_for_active_player(self):
        """Active player has bid actions available"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertTrue(len(state.available_actions) > 0)
        self.assertTrue(all(isinstance(a, AutomatedBid)
                        for a in state.available_actions))

    def test_no_actions_for_inactive_player(self):
        """Inactive player has no available actions"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        inactive = game.active_round.inactive_players[0]
        state = GameState.from_game(game, inactive.identifier)

        self.assertEqual(len(state.available_actions), 0)

    def test_available_bids_convenience(self):
        """available_bids property returns only Bid actions"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.available_bids, state.available_actions)

    def test_bid_history_after_bids(self):
        """Bid history records bids with relative seats"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        game.act(Bid(active.identifier, BidAmount.PASS))

        # now a different player is active
        new_active = game.active_round.active_player
        state = GameState.from_game(game, new_active.identifier)

        self.assertEqual(len(state.bid_history), 1)
        self.assertEqual(state.bid_history[0].amount, BidAmount.PASS)

    def test_scores_start_at_zero(self):
        """All scores start at 0"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.scores, (0, 0, 0, 0))

    def test_is_bidder_false_during_bidding(self):
        """is_bidder is False when no bidder determined yet"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertFalse(state.is_bidder)


class TestGameStateTrumpSelection(TestCase):
    """Tests for game_state_for during TRUMP_SELECTION"""

    def test_status_is_trump_selection(self):
        """State reflects trump selection status"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.status, RoundStatus.TRUMP_SELECTION)

    def test_bidder_seat_is_zero_for_bidder(self):
        """The bidder sees themselves as seat 0"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        bidder = game.active_round.active_bidder
        assert bidder is not None
        state = GameState.from_game(game, bidder.identifier)

        self.assertEqual(state.bidder_seat, 0)
        self.assertTrue(state.is_bidder)

    def test_bidder_seat_nonzero_for_non_bidder(self):
        """Non-bidder sees the bidder at a non-zero seat"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        non_bidder = game.active_round.inactive_players[0]
        state = GameState.from_game(game, non_bidder.identifier)

        self.assertNotEqual(state.bidder_seat, 0)
        self.assertFalse(state.is_bidder)

    def test_available_trump_selections(self):
        """Bidder has 4 trump selection options"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        bidder = game.active_round.active_bidder
        assert bidder is not None
        state = GameState.from_game(game, bidder.identifier)

        self.assertEqual(len(state.available_trump_selections), 4)
        self.assertTrue(all(isinstance(a, AutomatedSelectTrump)
                        for a in state.available_trump_selections))

    def test_no_actions_for_non_bidder(self):
        """Non-bidder has no actions during trump selection"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        non_bidder = game.active_round.inactive_players[0]
        state = GameState.from_game(game, non_bidder.identifier)

        self.assertEqual(len(state.available_actions), 0)

    def test_bid_history_recorded(self):
        """Bid history has entries from the bidding phase"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertTrue(len(state.bid_history) > 0)

    def test_active_bid_set(self):
        """Active bid is set after bidding is complete"""
        game = arrange.game(RoundStatus.TRUMP_SELECTION, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertIsNotNone(state.active_bid)


class TestGameStateDiscard(TestCase):
    """Tests for game_state_for during DISCARD phase"""

    def test_status_is_discard(self):
        """State reflects discard status"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.status, RoundStatus.DISCARD)

    def test_trump_is_set(self):
        """Trump has been selected"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertIsNotNone(state.trump)

    def test_available_discards_for_active_player(self):
        """Active player has discard options (2^hand_size subsets)"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        discard_actions = state.available_discards
        # 2^5 = 32 subsets for a 5-card hand
        self.assertEqual(len(discard_actions), 2**HAND_SIZE)
        self.assertTrue(all(isinstance(a, AutomatedDiscard)
                        for a in discard_actions))

    def test_discard_includes_empty_set(self):
        """Discard options include keeping all cards (empty discard)"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        empty_discards = [
            d for d in state.available_discards if len(d.cards) == 0]
        self.assertEqual(len(empty_discards), 1)

    def test_discard_includes_full_hand(self):
        """Discard options include discarding entire hand"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        full_discards = [
            d for d in state.available_discards if len(d.cards) == HAND_SIZE]
        self.assertEqual(len(full_discards), 1)

    def test_own_discards_visible_after_discard(self):
        """After discarding, own discarded cards show as Discarded"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        discarded_cards = [active.hand[0], active.hand[1]]
        game.act(Discard(active.identifier, discarded_cards))

        state = GameState.from_game(game, active.identifier)
        discarded_in_state = [
            ck.card for ck in state.cards if isinstance(ck.status, Discarded)]
        self.assertCountEqual(discarded_in_state, discarded_cards)

    def test_other_player_discards_not_visible(self):
        """Other players' discards appear as Unknown, not Discarded"""
        game = arrange.game(RoundStatus.DISCARD, seed=SEED)
        # First player discards
        first_active = game.active_round.active_player
        first_discarded = list(first_active.hand[:2])
        game.act(Discard(first_active.identifier, first_discarded))

        # Second player looks at state — should not see first player's discards
        second_active = game.active_round.active_player
        state = GameState.from_game(game, second_active.identifier)

        for card in first_discarded:
            ck = next(c for c in state.cards if c.card == card)
            self.assertIsInstance(ck.status, Unknown)


class TestGameStateTricks(TestCase):
    """Tests for game_state_for during TRICKS phase"""

    def test_status_is_tricks(self):
        """State reflects tricks status"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(state.status, RoundStatus.TRICKS)

    def test_available_plays(self):
        """Active player has play actions available"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertTrue(len(state.available_plays) > 0)
        self.assertTrue(all(isinstance(a, AutomatedPlay)
                        for a in state.available_plays))

    def test_play_actions_match_hand(self):
        """Play actions correspond to cards in hand (when not bleeding)"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        play_cards = [p.card for p in state.available_plays]
        # When first to play (not bleeding), all hand cards are playable
        self.assertCountEqual(play_cards, list(state.hand))

    def test_played_cards_tracked(self):
        """After a card is played, it appears as Played in card knowledge"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        card_to_play = active.hand[0]
        game.act(Play(active.identifier, card_to_play))

        # Next player sees the played card
        next_active = game.active_round.active_player
        state = GameState.from_game(game, next_active.identifier)

        ck = next(c for c in state.cards if c.card == card_to_play)
        self.assertIsInstance(ck.status, Played)
        if isinstance(ck.status, Played):
            self.assertEqual(ck.status.trick_index, 0)

    def test_current_trick_plays_tracked(self):
        """Current trick plays show in-progress plays"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        game.act(Play(active.identifier, active.hand[0]))

        next_active = game.active_round.active_player
        state = GameState.from_game(game, next_active.identifier)

        self.assertEqual(len(state.current_trick_plays), 1)

    def test_completed_trick_after_full_trick(self):
        """After all players play, trick moves to completed_tricks"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        arrange.play_trick(game)

        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(len(state.completed_tricks), 1)
        self.assertIsInstance(state.completed_tricks[0], CompletedTrick)
        self.assertEqual(len(state.completed_tricks[0].plays), 4)

    def test_completed_trick_has_winner(self):
        """Completed trick records the winner's relative seat"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        arrange.play_trick(game)

        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        winner_seat = state.completed_tricks[0].winner_seat
        self.assertGreaterEqual(winner_seat, 0)
        self.assertLess(winner_seat, 4)


class TestGameStateSeatNormalization(TestCase):
    """Tests that seat normalization is consistent"""

    def test_all_players_see_self_as_seat_zero(self):
        """Every player, when requesting their state, is seat 0"""
        game = arrange.game(RoundStatus.TRICKS, seed=SEED)
        arrange.play_trick(game)

        for player in game.active_round.players:
            state = GameState.from_game(game, player.identifier)
            # Verify hand matches (proving seat 0 = self)
            self.assertEqual(state.hand, tuple(player.hand))

    def test_dealer_seat_sums_correctly(self):
        """Different players see dealer at different relative seats that are consistent"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        players = game.active_round.players
        dealer = game.active_round.dealer
        dealer_abs = players.index(dealer)

        for i, player in enumerate(players):
            state = GameState.from_game(game, player.identifier)
            expected = (dealer_abs - i) % len(players)
            self.assertEqual(
                state.dealer_seat,
                expected,
                f"Player {i} should see dealer at seat {expected}",
            )

    def test_bid_events_have_relative_seats(self):
        """Bid events use relative seats from the requesting player's perspective"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        game.act(Bid(active.identifier, BidAmount.PASS))

        # The player who just bid sees themselves as seat 0
        state_self = GameState.from_game(game, active.identifier)
        self.assertEqual(state_self.bid_history[0].seat, 0)

        # A different player sees the bidder at a non-zero seat
        other = game.active_round.inactive_players[-1]
        if other.identifier != active.identifier:
            state_other = GameState.from_game(game, other.identifier)
            self.assertNotEqual(state_other.bid_history[0].seat, 0)


class TestGameStateImmutability(TestCase):
    """Tests that GameState is immutable"""

    def test_frozen_dataclass(self):
        """GameState cannot be mutated"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        with self.assertRaises(AttributeError):
            state.status = RoundStatus.TRICKS  # type: ignore[misc]

    def test_cards_all_53(self):
        """Verify all 53 defined cards are represented"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        state_cards = [ck.card for ck in state.cards]
        self.assertCountEqual(state_cards, defined_cards)


class TestGameStateConvenienceProperties(TestCase):
    """Tests for convenience properties on GameState"""

    def test_is_dealer_true_for_dealer(self):
        """is_dealer returns True for the dealer"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        dealer = game.active_round.dealer
        state = GameState.from_game(game, dealer.identifier)

        self.assertTrue(state.is_dealer)

    def test_is_dealer_false_for_non_dealer(self):
        """is_dealer returns False for non-dealers"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        non_dealer = next(
            p for p in game.active_round.players if p != game.active_round.dealer)
        state = GameState.from_game(game, non_dealer.identifier)

        self.assertFalse(state.is_dealer)

    def test_available_plays_empty_during_bidding(self):
        """available_plays returns empty during bidding"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(len(state.available_plays), 0)

    def test_available_discards_empty_during_bidding(self):
        """available_discards returns empty during bidding"""
        game = arrange.game(RoundStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = GameState.from_game(game, active.identifier)

        self.assertEqual(len(state.available_discards), 0)
