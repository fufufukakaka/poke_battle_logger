import pytest

from poke_battle_logger.batch.extractor import Extractor


class TestExtractor:
    """Test Extractor class methods."""

    @pytest.fixture
    def extractor(self):
        """Create an Extractor instance for testing."""
        return Extractor(lang="en")

    def test_correct_move_name_exact_match(self, extractor):
        """Test that exact matches return the same move name."""
        # Exact match should return the same name
        result = extractor.correct_move_name("Absorb")
        assert result == "Absorb"

        result = extractor.correct_move_name("Acid")
        assert result == "Acid"

        result = extractor.correct_move_name("Aerial Ace")
        assert result == "Aerial Ace"

    def test_correct_move_name_edit_distance_1(self, extractor):
        """Test correction with edit distance of 1."""
        # Missing one character
        result = extractor.correct_move_name("Asorb")
        assert result == "Absorb"

        # Extra character
        result = extractor.correct_move_name("Acidd")
        assert result == "Acid"

        # Wrong character
        result = extractor.correct_move_name("Acud")
        assert result == "Acid"

    def test_correct_move_name_edit_distance_2(self, extractor):
        """Test correction with edit distance of 2."""
        # Missing two characters
        result = extractor.correct_move_name("Asorbb")
        assert result == "Absorb"

        # Two wrong characters
        result = extractor.correct_move_name("Acrobatocs")
        assert result == "Acrobatics"

    def test_correct_move_name_no_correction_beyond_threshold(self, extractor):
        """Test that moves with edit distance > 2 are not corrected."""
        # Edit distance of 3 or more should return original name
        result = extractor.correct_move_name("Xyz")
        assert result == "Xyz"  # No correction applied

        result = extractor.correct_move_name("Completely Wrong")
        assert result == "Completely Wrong"  # No correction applied

    def test_correct_move_name_case_sensitive(self, extractor):
        """Test that correction is case-sensitive."""
        # Different case should be treated differently
        result = extractor.correct_move_name("absorb")
        # Edit distance of 1 per character case difference
        # 'a' vs 'A' is distance 1, so total is 1
        assert result == "Absorb"

    def test_correct_move_name_special_characters(self, extractor):
        """Test correction with special characters in move names."""
        # Test with special move names that have special characters
        result = extractor.correct_move_name("10,000,000 Volt Thunderbolt")
        assert result == "10,000,000 Volt Thunderbolt"

        # Test with typo in special character move
        result = extractor.correct_move_name("10,000,00 Volt Thunderbolt")
        assert result == "10,000,000 Volt Thunderbolt"

    def test_correct_move_name_closest_match(self, extractor):
        """Test that the closest match is selected when multiple candidates exist."""
        # "Acid Spray" vs "Acid Armor" vs "Acid"
        # "Acod Spray" has distance 1 from "Acid Spray"
        result = extractor.correct_move_name("Acod Spray")
        assert result == "Acid Spray"

        # "Acid Arnor" has distance 1 from "Acid Armor"
        result = extractor.correct_move_name("Acid Arnor")
        assert result == "Acid Armor"

    def test_correct_move_name_empty_string(self, extractor):
        """Test with empty string."""
        result = extractor.correct_move_name("")
        # Empty string will have edit distance equal to length of each move name
        # Since all move names are > 2 chars, edit distance > 2, so returns original
        assert result == ""

    def test_correct_move_name_common_ocr_errors(self, extractor):
        """Test common OCR misrecognition patterns."""
        # Common OCR errors: I/l, O/0, etc.
        # "Aeria1 Ace" (1 instead of l)
        result = extractor.correct_move_name("Aeria1 Ace")
        assert result == "Aerial Ace"

        # "Air S1ash" (1 instead of l)
        result = extractor.correct_move_name("Air S1ash")
        assert result == "Air Slash"

        # "Acu pressure" (missing p)
        result = extractor.correct_move_name("Acupresure")
        assert result == "Acupressure"
