
from difflib import SequenceMatcher
from datetime import datetime

FIELDS = {
    "name": {"label": "Full name", "weight": 0.40},
    "date_of_birth": {"label": "Date of birth", "weight": 0.35},
    "address": {"label": "Address", "weight": 0.25},
}

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d.%m.%Y",
    "%d %B %Y",
    "%d %b %Y",
    "%m/%d/%Y",
)


def normalize(value):
    """Make text comparisons less sensitive to case and punctuation."""
    if value is None:
        return ""

    return " ".join(
        str(value).lower().strip().replace(",", " ").split()
    )


def parse_date(value):
    """Parse supported date formats into a calendar date."""
    text = str(value).strip()

    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue

    return None


def similarity(left, right):
    left = normalize(left)
    right = normalize(right)

    if not left or not right:
        return None

    if left == right:
        return 100.0

    return round(
        SequenceMatcher(None, left, right).ratio() * 100, 1
    )


def compare_records(citizen, asset):
    """Compare records and return a score, result, and explanations."""
    details = []
    weighted_score = 0.0
    available_weight = 0.0
    reasons = []
    conflicts = 0
    missing = 0
    critical_conflict = False

    for field, config in FIELDS.items():
        left = citizen.get(field, "")
        right = asset.get(field, "")
        score = similarity(left, right)

        if score is None:
            status = "Missing data"
            missing += 1
            reasons.append(
                f"{config['label']}: one or both records are missing a value."
            )

        elif field == "date_of_birth":
            left_date = parse_date(left)
            right_date = parse_date(right)

            if left_date is None or right_date is None:
                status = "Invalid date"
                missing += 1
                reasons.append(
                    "Date of birth: a date could not be parsed. "
                    "Human verification is required."
                )
            else:
                score = 100.0 if left_date == right_date else 0.0
                weighted_score += score * config["weight"]
                available_weight += config["weight"]

                if left_date == right_date:
                    status = "Match"
                else:
                    status = "Conflict"
                    conflicts += 1
                    critical_conflict = True
                    reasons.append(
                        "Date of birth conflict: the dates differ. "
                        "Human verification is required."
                    )

        else:
            weighted_score += score * config["weight"]
            available_weight += config["weight"]

            if score == 100:
                status = "Match"
            elif score >= 65:
                status = "Possible variation"
                reasons.append(
                    f"{config['label']}: values are similar but not identical."
                )
            else:
                status = "Conflict"
                conflicts += 1
                reasons.append(
                    f"{config['label']}: values differ substantially."
                )

        details.append({
            "field": field,
            "left": left,
            "right": right,
            "similarity": score if score is not None else 0,
            "status": status,
        })

    score = (
        round(weighted_score / available_weight, 1)
        if available_weight else 0.0
    )

    if available_weight < 0.60:
        result = "Insufficient data"
    elif critical_conflict:
        result = "Needs review"
    elif missing or conflicts or score < 90:
        result = "Needs review" if score >= 45 else "Low similarity"
    elif score >= 90:
        result = "High similarity"
    else:
        result = "Needs review"

    return {
        "score": score,
        "result": result,
        "conflicts": conflicts,
        "details": details,
        "reasons": reasons,
    }


if __name__ == "__main__":
    print("Run the unit tests with: python -m unittest test_matching.py -v")
