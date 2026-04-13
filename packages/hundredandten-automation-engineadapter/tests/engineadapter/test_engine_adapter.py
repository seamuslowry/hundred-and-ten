"""Test behavior of EngineAdapter.state_from_engine(game, )"""

from unittest import TestCase

from hundredandten.automation.engineadapter import EngineAdapter
from hundredandten.deck import Card, CardNumber, CardSuit, SelectableSuit, defined_cards
from hundredandten.engine.actions import Bid, Discard, Play, SelectTrump
from hundredandten.engine.constants import (
    HAND_SIZE,
    BidAmount,
    Status as EngineStatus,
)
from hundredandten.engine.player import player_after
from hundredandten.state import (
    AvailableBid,
    AvailableDiscard,
    AvailablePlay,
    AvailableSelectTrump,
    BidAmount as StateBidAmount,
    CompletedTrick,
    Discarded,
    InHand,
    Played,
    StateError,
    Status,
    Unknown,
)
from hundredandten.testing import arrange

SEED = "test-game-state-seed"


class TestGameStateBidding(TestCase):
    """Tests for game_state_for during the BIDDING phase"""

    def test_status_is_bidding(self):
        """State reflects bidding status"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.status, Status.BIDDING)

    def test_num_players(self):
        """State reflects the number of players"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.table.num_players, 4)

    def test_self_is_seat_zero(self):
        """The requesting player is always seat 0"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        for player in game.active_round.players:
            state = EngineAdapter.state_from_engine(game, player.identifier)
            # self is always seat 0 — verified through hand matching
            self.assertEqual(state.hand, tuple(player.hand))

    def test_dealer_seat_relative(self):
        """Dealer seat is relative to the requesting player"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        dealer = game.active_round.dealer
        players = game.active_round.players
        dealer_index = players.index(dealer)

        for i, player in enumerate(players):
            state = EngineAdapter.state_from_engine(game, player.identifier)
            expected_dealer_seat = (dealer_index - i) % len(players)
            self.assertEqual(state.table.dealer_seat, expected_dealer_seat)

    def test_hand_matches_player(self):
        """Hand in state matches the requesting player's actual hand"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        for player in game.active_round.players:
            state = EngineAdapter.state_from_engine(game, player.identifier)
            self.assertEqual(state.hand, tuple(player.hand))
            self.assertEqual(len(state.hand), HAND_SIZE)

    def test_cards_has_53_entries(self):
        """Card knowledge always has 53 entries"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.cards), 53)

    def test_own_hand_cards_are_in_hand(self):
        """Player's own cards show as InHand"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        in_hand_cards = [ck.card for ck in state.cards if isinstance(ck.status, InHand)]
        self.assertCountEqual(in_hand_cards, list(active.hand))

    def test_other_cards_are_unknown(self):
        """Cards not in player's hand are Unknown"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        unknown_cards = [ck for ck in state.cards if isinstance(ck.status, Unknown)]
        self.assertEqual(len(unknown_cards), 53 - HAND_SIZE)

    def test_no_bidder_during_bidding(self):
        """bidder_seat is None during bidding"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertIsNone(state.table.bidder_seat)

    def test_bid_history_empty_at_start(self):
        """No bids placed yet"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.bidding.bid_history), 0)

    def test_active_bid_none_at_start(self):
        """No active bid yet"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertIsNone(state.bidding.active_bid)

    def test_trump_none_during_bidding(self):
        """Trump is not yet selected"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertIsNone(state.bidding.trump)

    def test_no_tricks_during_bidding(self):
        """No tricks have been played"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.tricks.completed_tricks), 0)
        self.assertEqual(len(state.tricks.current_trick_plays), 0)

    def test_available_actions_for_active_player(self):
        """Active player has bid actions available"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertTrue(len(state.available_actions) > 0)
        self.assertTrue(
            all(isinstance(a, AvailableBid) for a in state.available_actions)
        )

    def test_inactive_player_sees_possible_actions(self):
        """Inactive player sees actions they could take on their turn"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        inactive = game.active_round.inactive_players[0]
        state = EngineAdapter.state_from_engine(game, inactive.identifier)

        self.assertGreater(len(state.available_actions), 0)
        self.assertTrue(
            all(isinstance(a, AvailableBid) for a in state.available_actions)
        )

    def test_available_bids_convenience(self):
        """available_bids property returns only Bid actions"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.available_bids, state.available_actions)

    def test_bid_history_after_bids(self):
        """Bid history records bids with relative seats"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        game.act(Bid(active.identifier, BidAmount.PASS))

        # now a different player is active
        new_active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, new_active.identifier)

        self.assertEqual(len(state.bidding.bid_history), 1)
        self.assertEqual(state.bidding.bid_history[0].amount, BidAmount.PASS)

    def test_scores_start_at_zero(self):
        """All scores start at 0"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.table.scores, (0, 0, 0, 0))


class TestGameStateTrumpSelection(TestCase):
    """Tests for game_state_for during TRUMP_SELECTION"""

    def test_status_is_trump_selection(self):
        """State reflects trump selection status"""
        game = arrange.game(EngineStatus.TRUMP_SELECTION, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.status, Status.TRUMP_SELECTION)

    def test_available_trump_selections(self):
        """Bidder has 4 trump selection options"""
        game = arrange.game(EngineStatus.TRUMP_SELECTION, seed=SEED)
        bidder = game.active_round.active_bidder
        assert bidder is not None
        state = EngineAdapter.state_from_engine(game, bidder.identifier)

        self.assertEqual(len(state.available_trump_selections), 4)
        self.assertTrue(
            all(
                isinstance(a, AvailableSelectTrump)
                for a in state.available_trump_selections
            )
        )

    def test_no_actions_for_non_bidder(self):
        """Non-bidder has no actions during trump selection"""
        game = arrange.game(EngineStatus.TRUMP_SELECTION, seed=SEED)
        non_bidder = game.active_round.inactive_players[0]
        state = EngineAdapter.state_from_engine(game, non_bidder.identifier)

        self.assertEqual(len(state.available_actions), 0)

    def test_bid_history_recorded(self):
        """Bid history has entries from the bidding phase"""
        game = arrange.game(EngineStatus.TRUMP_SELECTION, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertTrue(len(state.bidding.bid_history) > 0)

    def test_active_bid_set(self):
        """Active bid is set after bidding is complete"""
        game = arrange.game(EngineStatus.TRUMP_SELECTION, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertIsNotNone(state.bidding.active_bid)


class TestGameStateDiscard(TestCase):
    """Tests for game_state_for during DISCARD phase"""

    def test_status_is_discard(self):
        """State reflects discard status"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.status, Status.DISCARD)

    def test_trump_is_set(self):
        """Trump has been selected"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertIsNotNone(state.bidding.trump)

    def test_available_discards_for_active_player(self):
        """Active player has discard options (2^hand_size subsets)"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        discard_actions = state.available_discards
        # 2^5 = 32 subsets for a 5-card hand
        self.assertEqual(len(discard_actions), 2**HAND_SIZE)
        self.assertTrue(all(isinstance(a, AvailableDiscard) for a in discard_actions))

    def test_discard_includes_empty_set(self):
        """Discard options include keeping all cards (empty discard)"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        empty_discards = [d for d in state.available_discards if len(d.cards) == 0]
        self.assertEqual(len(empty_discards), 1)

    def test_discard_includes_full_hand(self):
        """Discard options include discarding entire hand"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        full_discards = [
            d for d in state.available_discards if len(d.cards) == HAND_SIZE
        ]
        self.assertEqual(len(full_discards), 1)

    def test_own_discards_visible_after_discard(self):
        """After discarding, own discarded cards show as Discarded"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        active = game.active_round.active_player
        discarded_cards = [active.hand[0], active.hand[1]]
        game.act(Discard(active.identifier, discarded_cards))

        state = EngineAdapter.state_from_engine(game, active.identifier)
        discarded_in_state = [
            ck.card for ck in state.cards if isinstance(ck.status, Discarded)
        ]
        self.assertCountEqual(discarded_in_state, discarded_cards)
        # Verify all discarded cards show seat=0 (own seat)
        for ck in state.cards:
            if isinstance(ck.status, Discarded):
                self.assertEqual(ck.status.seat, 0)

    def test_other_player_discards_not_visible(self):
        """Other players' discards appear as Unknown, not Discarded"""
        game = arrange.game(EngineStatus.DISCARD, seed=SEED)
        # First player discards
        first_active = game.active_round.active_player
        first_discarded = list(first_active.hand[:2])
        game.act(Discard(first_active.identifier, first_discarded))

        # Second player looks at state — should not see first player's discards
        second_active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, second_active.identifier)

        for card in first_discarded:
            ck = next(c for c in state.cards if c.card == card)
            self.assertIsInstance(ck.status, Unknown)


class TestGameStateTricks(TestCase):
    """Tests for game_state_for during TRICKS phase"""

    def test_status_is_tricks(self):
        """State reflects tricks status"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(state.status, Status.TRICKS)

    def test_available_plays(self):
        """Active player has play actions available"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertTrue(len(state.available_plays) > 0)
        self.assertTrue(
            all(isinstance(a, AvailablePlay) for a in state.available_plays)
        )

    def test_play_actions_match_hand(self):
        """Play actions correspond to cards in hand (when not bleeding)"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        play_cards = [p.card for p in state.available_plays]
        # When first to play (not bleeding), all hand cards are playable
        self.assertCountEqual(play_cards, list(state.hand))

    def test_played_cards_tracked(self):
        """After a card is played, it appears as Played in card knowledge"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        card_to_play = active.hand[0]
        game.act(Play(active.identifier, card_to_play))

        # Next player sees the played card
        next_active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, next_active.identifier)

        ck = next(c for c in state.cards if c.card == card_to_play)
        self.assertIsInstance(ck.status, Played)
        if isinstance(ck.status, Played):
            self.assertEqual(ck.status.trick_index, 0)

    def test_current_trick_plays_tracked(self):
        """Current trick plays show in-progress plays"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        active = game.active_round.active_player
        game.act(Play(active.identifier, active.hand[0]))

        next_active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, next_active.identifier)

        self.assertEqual(len(state.tricks.current_trick_plays), 1)

    def test_completed_trick_after_full_trick(self):
        """After all players play, trick moves to completed_tricks"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        arrange.play_trick(game)

        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.tricks.completed_tricks), 1)
        self.assertIsInstance(state.tricks.completed_tricks[0], CompletedTrick)
        self.assertEqual(len(state.tricks.completed_tricks[0].plays), 4)

    def test_completed_trick_has_winner(self):
        """Completed trick records the winner's relative seat"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        arrange.play_trick(game)

        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        winner_seat = state.tricks.completed_tricks[0].winner_seat
        self.assertGreaterEqual(winner_seat, 0)
        self.assertLess(winner_seat, 4)


class TestGameStateSeatNormalization(TestCase):
    """Tests that seat normalization is consistent"""

    def test_all_players_see_self_as_seat_zero(self):
        """Every player, when requesting their state, is seat 0"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        arrange.play_trick(game)

        for player in game.active_round.players:
            state = EngineAdapter.state_from_engine(game, player.identifier)
            # Verify hand matches (proving seat 0 = self)
            self.assertEqual(state.hand, tuple(player.hand))

    def test_dealer_seat_sums_correctly(self):
        """Different players see dealer at different relative seats that are consistent"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        players = game.active_round.players
        dealer = game.active_round.dealer
        dealer_abs = players.index(dealer)

        for i, player in enumerate(players):
            state = EngineAdapter.state_from_engine(game, player.identifier)
            expected = (dealer_abs - i) % len(players)
            self.assertEqual(
                state.table.dealer_seat,
                expected,
                f"Player {i} should see dealer at seat {expected}",
            )

    def test_bid_events_have_relative_seats(self):
        """Bid events use relative seats from the requesting player's perspective"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        game.act(Bid(active.identifier, BidAmount.PASS))

        # The player who just bid sees themselves as seat 0
        state_self = EngineAdapter.state_from_engine(game, active.identifier)
        self.assertEqual(state_self.bidding.bid_history[0].seat, 0)

        # A different player sees the bidder at a non-zero seat
        other = game.active_round.inactive_players[-1]
        if other.identifier != active.identifier:
            state_other = EngineAdapter.state_from_engine(game, other.identifier)
            self.assertNotEqual(state_other.bidding.bid_history[0].seat, 0)

    def test_played_card_seat_is_relative(self):
        """Played card's seat in card knowledge reflects the playing player's relative position"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        players = game.active_round.players
        first_player = game.active_round.active_player
        played_card = first_player.hand[0]
        game.act(Play(first_player.identifier, played_card))

        first_abs = list(players).index(first_player)
        for i, observer in enumerate(players):
            state = EngineAdapter.state_from_engine(game, observer.identifier)
            played_ck = next(ck for ck in state.cards if ck.card == played_card)
            assert isinstance(played_ck.status, Played)
            expected_seat = (first_abs - i) % len(players)
            self.assertEqual(played_ck.status.seat, expected_seat)

    def test_trick_play_seat_is_relative(self):
        """TrickPlay seat in current trick reflects the playing player's relative position"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        players = game.active_round.players
        first_player = game.active_round.active_player
        game.act(Play(first_player.identifier, first_player.hand[0]))

        first_abs = list(players).index(first_player)
        for i, observer in enumerate(players):
            state = EngineAdapter.state_from_engine(game, observer.identifier)
            self.assertEqual(len(state.tricks.current_trick_plays), 1)
            expected_seat = (first_abs - i) % len(players)
            self.assertEqual(state.tricks.current_trick_plays[0].seat, expected_seat)


class TestGameStateImmutability(TestCase):
    """Tests that GameState is immutable"""

    def test_frozen_dataclass(self):
        """GameState cannot be mutated"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        with self.assertRaises(AttributeError):
            state.status = Status.TRICKS  # type: ignore[misc]

    def test_cards_all_53(self):
        """Verify all 53 defined cards are represented"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        state_cards = [ck.card for ck in state.cards]
        self.assertCountEqual(state_cards, defined_cards)


class TestGameStateConvenienceProperties(TestCase):
    """Tests for convenience properties on GameState"""

    def test_available_plays_empty_during_bidding(self):
        """available_plays returns empty during bidding"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.available_plays), 0)

    def test_available_discards_empty_during_bidding(self):
        """available_discards returns empty during bidding"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.available_discards), 0)


class TestGameStateWon(TestCase):
    """Test GameState when game is won"""

    def test_status_is_won(self):
        """GameState.status reflects game WON status"""
        game = arrange.game(EngineStatus.WON, seed=SEED)
        state = EngineAdapter.state_from_engine(game, game.players[0].identifier)

        self.assertEqual(state.status, Status.WON)

    def test_available_actions_empty_when_won(self):
        """No actions available when game is won"""
        game = arrange.game(EngineStatus.WON, seed=SEED)
        state = EngineAdapter.state_from_engine(game, game.players[0].identifier)

        self.assertEqual(len(state.available_actions), 0)


class TestGameStateBiddingEdgeCases(TestCase):
    """Edge case tests for BIDDING available_actions"""

    def test_available_actions_include_pass(self):
        """PASS is always among available bids when no bids have been placed"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        state = EngineAdapter.state_from_engine(game, active.identifier)

        bid_amounts = [a.amount for a in state.available_bids]

        self.assertIn(StateBidAmount.PASS, bid_amounts)

    def test_already_passed_player_has_no_available_actions(self):
        """A player who has already passed sees no available actions"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player
        game.act(Bid(active.identifier, BidAmount.PASS))

        # The player who just passed now observes the state
        state = EngineAdapter.state_from_engine(game, active.identifier)

        self.assertEqual(len(state.available_actions), 0)

    def test_dealer_can_steal_active_bid(self):
        """Dealer can match (steal) the active bid as well as raise it"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)

        # Advance until only the dealer is left to bid (everyone else passes)
        arrange.pass_to_dealer(game)

        dealer = game.active_round.active_player
        active_bid_amount = game.active_round.active_bid
        state = EngineAdapter.state_from_engine(game, dealer.identifier)

        bid_amounts = [a.amount for a in state.available_bids]

        # Dealer must be able to match the current active bid (steal)
        self.assertIsNotNone(active_bid_amount)
        self.assertIn(StateBidAmount(active_bid_amount), bid_amounts)


class TestGameStateTricksBleedingLogic(TestCase):
    """Tests for bleeding (trump-lead) logic in available_plays"""

    def test_non_trump_lead_allows_full_hand(self):
        """When the lead card is not trump, all hand cards are playable"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        assert game.active_round.trump

        non_trump_suit = next(
            s for s in iter(SelectableSuit) if s != game.active_round.trump
        )
        active_player = game.active_round.active_player
        next_player = player_after(game.active_round.players, active_player.identifier)

        # Lead with a non-trump card
        active_player.hand[0] = Card(CardNumber.TWO, CardSuit[non_trump_suit.value])
        game.act(Play(active_player.identifier, active_player.hand[0]))

        # Next player has both trump and non-trump cards
        state = EngineAdapter.state_from_engine(game, next_player.identifier)
        play_cards = {p.card for p in state.available_plays}

        self.assertEqual(play_cards, set(next_player.hand))

    def test_trump_lead_restricts_to_trump_cards(self):
        """When the lead card is trump, only trump cards are playable (if held)"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        assert game.active_round.trump

        active_player = game.active_round.active_player
        next_player = player_after(game.active_round.players, active_player.identifier)
        non_trump_suit = next(
            s for s in iter(SelectableSuit) if s != game.active_round.trump
        )

        # Lead with a trump card to trigger bleeding
        active_player.hand[0] = Card(
            CardNumber.TEN, CardSuit[game.active_round.trump.value]
        )
        # Give next player a mix: some trump, some non-trump
        trump_card = Card(CardNumber.NINE, CardSuit[game.active_round.trump.value])
        non_trump_card = Card(CardNumber.TWO, CardSuit[non_trump_suit.value])
        next_player.hand = [non_trump_card] * 4 + [trump_card]

        game.act(Play(active_player.identifier, active_player.hand[0]))

        state = EngineAdapter.state_from_engine(game, next_player.identifier)
        play_cards = {p.card for p in state.available_plays}

        # Only the trump card should be available
        self.assertEqual(play_cards, {trump_card})

    def test_trump_lead_allows_full_hand_when_no_trumps_held(self):
        """When bleeding but player holds no trumps, full hand is playable"""
        game = arrange.game(EngineStatus.TRICKS, seed=SEED)
        assert game.active_round.trump

        active_player = game.active_round.active_player
        next_player = player_after(game.active_round.players, active_player.identifier)
        non_trump_suit = next(
            s for s in iter(SelectableSuit) if s != game.active_round.trump
        )

        # Lead with a trump card to trigger bleeding
        active_player.hand[0] = Card(
            CardNumber.TEN, CardSuit[game.active_round.trump.value]
        )
        # Give next player only non-trump cards
        next_player.hand = [Card(CardNumber.TWO, CardSuit[non_trump_suit.value])] * 5

        game.act(Play(active_player.identifier, active_player.hand[0]))

        state = EngineAdapter.state_from_engine(game, next_player.identifier)
        play_cards = {p.card for p in state.available_plays}

        self.assertEqual(play_cards, set(next_player.hand))


class TestEngineAdapterAvailableActionFromEngine(TestCase):
    """Tests for EngineAdapter.available_action_from_engine() conversion"""

    def test_bid_converts_to_available_bid(self):
        """Bid engine action converts to AvailableBid"""

        action = Bid(identifier="player-1", amount=BidAmount.FIFTEEN)
        result = EngineAdapter.available_action_from_engine(action)

        assert isinstance(result, AvailableBid)
        self.assertEqual(result.amount, StateBidAmount.FIFTEEN)

    def test_select_trump_converts_to_available_select_trump(self):
        """SelectTrump engine action converts to AvailableSelectTrump"""
        action = SelectTrump(identifier="player-1", suit=SelectableSuit.HEARTS)
        result = EngineAdapter.available_action_from_engine(action)

        assert isinstance(result, AvailableSelectTrump)
        self.assertEqual(result.suit, SelectableSuit.HEARTS)

    def test_discard_converts_to_available_discard(self):
        """Discard engine action converts to AvailableDiscard"""
        cards = [Card(CardNumber.ACE, CardSuit.HEARTS)]
        action = Discard(identifier="player-1", cards=cards)
        result = EngineAdapter.available_action_from_engine(action)

        assert isinstance(result, AvailableDiscard)
        self.assertEqual(result.cards, tuple(cards))

    def test_play_converts_to_available_play(self):
        """Play engine action converts to AvailablePlay"""
        card = Card(CardNumber.FIVE, CardSuit.SPADES)
        action = Play(identifier="player-1", card=card)
        result = EngineAdapter.available_action_from_engine(action)

        assert isinstance(result, AvailablePlay)
        self.assertEqual(result.card, card)


class TestAdapterActionFor(TestCase):
    """Tests for the adapter action_for, hepler to get an action from an engine generically"""

    def test_adapter_gets_action(self):
        """Adapter can help get an available action for the active player"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player

        action = EngineAdapter.action_for(
            game,
            active.identifier,
            lambda s: s.available_actions[0],
        )

        self.assertIsNotNone(action)
        self.assertIsInstance(action, AvailableBid)

    def test_adapter_checks_action(self):
        """Adapter raises StateError if the decision function returns an unavailable action"""
        game = arrange.game(EngineStatus.BIDDING, seed=SEED)
        active = game.active_round.active_player

        with self.assertRaises(StateError):
            EngineAdapter.action_for(
                game, active.identifier, lambda _: AvailableDiscard(cards=())
            )


class TestEngineAdapterAvailableActionForPlayer(TestCase):
    """Tests for EngineAdapter.available_action_for_player() — state→engine conversion"""

    def test_available_bid_converts_to_bid(self):
        """AvailableBid converts to a player-aware Bid"""
        action = AvailableBid(StateBidAmount.FIFTEEN)
        result = EngineAdapter.available_action_for_player(action, "player-1")

        assert isinstance(result, Bid)
        self.assertEqual(result.identifier, "player-1")
        self.assertEqual(result.amount, BidAmount.FIFTEEN)

    def test_available_select_trump_converts_to_select_trump(self):
        """AvailableSelectTrump converts to a player-aware SelectTrump"""
        action = AvailableSelectTrump(SelectableSuit.HEARTS)
        result = EngineAdapter.available_action_for_player(action, "player-1")

        assert isinstance(result, SelectTrump)
        self.assertEqual(result.identifier, "player-1")
        self.assertEqual(result.suit, SelectableSuit.HEARTS)

    def test_available_discard_converts_to_discard(self):
        """AvailableDiscard converts to a player-aware Discard"""
        cards = [Card(CardNumber.ACE, CardSuit.HEARTS)]
        action = AvailableDiscard(tuple(cards))
        result = EngineAdapter.available_action_for_player(action, "player-1")

        assert isinstance(result, Discard)
        self.assertEqual(result.identifier, "player-1")
        self.assertEqual(result.cards, cards)

    def test_available_play_converts_to_play(self):
        """AvailablePlay converts to a player-aware Play"""
        card = Card(CardNumber.FIVE, CardSuit.SPADES)
        action = AvailablePlay(card)
        result = EngineAdapter.available_action_for_player(action, "player-1")

        assert isinstance(result, Play)
        self.assertEqual(result.identifier, "player-1")
        self.assertEqual(result.card, card)
