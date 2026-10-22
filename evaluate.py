
from sample_data import generate_data
from matching import compare_records


def evaluate():
    records = generate_data()

    true_positive = 0
    true_negative = 0
    false_positive = 0
    false_negative = 0
    abstentions = 0

    for record in records:
        result = compare_records(record["citizen"], record["asset"])
        actual_match = bool(record["actual_match"])

        # Cases needing human review are not automatic predictions.
        if result["result"] in ("Needs review", "Insufficient data"):
            abstentions += 1

        elif result["result"] == "High similarity":
            if actual_match:
                true_positive += 1
            else:
                false_positive += 1

        else:
            if actual_match:
                false_negative += 1
            else:
                true_negative += 1

    total = len(records)
    decided = total - abstentions

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0
    )

    accuracy = (
        (true_positive + true_negative) / decided
        if decided else 0
    )

    print("Civify - synthetic evaluation")
    print("=" * 34)
    print(f"Total cases:       {total}")
    print(f"Decided cases:     {decided}")
    print(f"Abstentions:       {abstentions}")
    print(
        f"Decision coverage: {decided / total:.1%}"
        if total else "Decision coverage: n/a"
    )
    print()
    print(f"True positives:    {true_positive}")
    print(f"True negatives:    {true_negative}")
    print(f"False positives:   {false_positive}")
    print(f"False negatives:   {false_negative}")
    print()
    print(f"Precision:         {precision:.1%}")
    print(f"Recall:            {recall:.1%}")
    print(f"Accuracy:          {accuracy:.1%} (decided cases only)")
    print()
    print("These results apply only to the generated synthetic dataset.")
    print("Abstentions are cases that require review or have insufficient data.")


if __name__ == "__main__":
    evaluate()
