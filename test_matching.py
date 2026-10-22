import unittest

from matching import compare_records, normalize, similarity


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.same = {
            "name": "Ishaan Mehta",
            "date_of_birth": "2005-06-21",
            "address": "44 Rose Avenue",
        }

    def test_normalize_ignores_case_and_extra_spaces(self):
        self.assertEqual(
            normalize("  ISHAAN   Mehta "),
            "ishaan mehta",
        )

    def test_exact_values_have_full_similarity(self):
        self.assertEqual(
            similarity("Ishaan Mehta", "Ishaan Mehta"),
            100.0,
        )

    def test_missing_value_has_no_similarity_score(self):
        self.assertIsNone(
            similarity("", "Ishaan Mehta"),
        )

    def test_exact_records_are_high_similarity(self):
        result = compare_records(self.same, dict(self.same))

        self.assertEqual(result["result"], "High similarity")
        self.assertEqual(result["score"], 100.0)

    def test_different_person_with_dob_conflict_needs_review(self):
        other = {
            "name": "Rohan Singh",
            "date_of_birth": "1999-01-01",
            "address": "90 Far Road",
        }

        result = compare_records(self.same, other)

        self.assertEqual(result["result"], "Needs review")
        self.assertEqual(result["conflicts"], 3)

    def test_missing_data_is_sent_for_review(self):
        asset = dict(self.same)
        asset["address"] = ""

        result = compare_records(self.same, asset)

        self.assertEqual(result["result"], "Needs review")
        self.assertTrue(result["reasons"])

    def test_details_cover_each_field(self):
        result = compare_records(self.same, dict(self.same))

        self.assertEqual(len(result["details"]), 3)

    def test_similar_name_with_conflicting_dob_needs_review(self):
        asset = dict(self.same)
        asset["name"] = "Ishaan Mehta"
        asset["date_of_birth"] = "1999-01-01"

        result = compare_records(self.same, asset)

        self.assertEqual(result["result"], "Needs review")

    def test_multiple_missing_fields_are_insufficient(self):
        asset = {
            "name": "",
            "date_of_birth": "",
            "address": "44 Rose Avenue",
        }

        result = compare_records(self.same, asset)

        self.assertEqual(result["result"], "Insufficient data")

    def test_empty_records_are_insufficient(self):
        result = compare_records({}, {})

        self.assertEqual(result["result"], "Insufficient data")
        self.assertEqual(result["score"], 0.0)

    def test_address_difference_is_detected(self):
        asset = dict(self.same)
        asset["address"] = "90 Far Road"

        result = compare_records(self.same, asset)

        self.assertNotEqual(result["details"][2]["status"], "Match")
        self.assertNotEqual(result["result"], "High similarity")

    def test_small_name_variation_does_not_count_as_exact_match(self):
        asset = dict(self.same)
        asset["name"] = "Ishaan Mehtaa"

        result = compare_records(self.same, asset)

        self.assertLess(
            result["details"][0]["similarity"],
            100.0,
        )
        self.assertNotEqual(result["details"][0]["status"], "Match")

    def test_dob_conflict_is_explained(self):
        asset = dict(self.same)
        asset["date_of_birth"] = "1999-01-01"

        result = compare_records(self.same, asset)

        self.assertEqual(result["result"], "Needs review")
        self.assertTrue(
            any("Date of birth" in reason for reason in result["reasons"])
        )

    def test_missing_dob_is_not_treated_as_a_match(self):
        asset = dict(self.same)
        asset["date_of_birth"] = ""

        result = compare_records(self.same, asset)

        self.assertEqual(result["details"][1]["status"], "Missing data")
        self.assertNotEqual(result["result"], "High similarity")

    def test_different_person_is_not_accepted_as_high_similarity(self):
        other = {
            "name": "Rohan Singh",
            "date_of_birth": "1999-01-01",
            "address": "90 Far Road",
        }

        result = compare_records(self.same, other)

        self.assertNotEqual(result["result"], "High similarity")

    def test_all_field_details_include_status(self):
        result = compare_records(self.same, dict(self.same))

        for detail in result["details"]:
            self.assertIn("field", detail)
            self.assertIn("similarity", detail)
            self.assertIn("status", detail)


if __name__ == "__main__":
    unittest.main(verbosity=2)