"""Deterministic synthetic records for local demos and repeatable evaluation."""

from copy import deepcopy


PEOPLE = [
    ("Aarav Sharma", "2004-02-18", "12 Lake View Road"),
    ("Ananya Verma", "2003-11-07", "8 Green Park"),
    ("Ishaan Mehta", "2005-06-21", "44 Rose Avenue"),
    ("Meera Iyer", "2004-09-13", "17 Temple Street"),
    ("Kabir Singh", "2003-04-29", "5 Market Lane"),
    ("Sana Khan", "2005-01-30", "29 Station Road"),
    ("Rohan Gupta", "2004-12-02", "61 Garden Colony"),
    ("Diya Patel", "2003-07-16", "3 River View"),
    ("Arjun Rao", "2005-03-08", "22 Hill Road"),
    ("Nisha Das", "2004-05-25", "10 School Lane"),
    ("Vivaan Joshi", "2003-08-19", "7 Central Avenue"),
    ("Aditi Nair", "2005-10-04", "18 Orchard Street"),
    ("Reyansh Kumar", "2004-01-11", "33 New Colony"),
    ("Tara Bose", "2003-12-27", "14 Park Street"),
    ("Dev Malhotra", "2005-04-14", "9 Sunrise Road"),
    ("Pooja Reddy", "2004-06-06", "25 Canal Road"),
    ("Neel Shah", "2003-02-03", "16 Ashok Nagar"),
    ("Simran Kaur", "2005-08-22", "52 College Road"),
    ("Aditya Sen", "2004-10-31", "6 Rose Garden"),
    ("Kavya Menon", "2003-05-12", "31 Lake Road"),
]

ISSUES = [
    "Name variation", "Date of birth conflict", "Address mismatch",
    "Missing field", "Similar names", "Consistent records",
]


def _record(person):
    return {"name": person[0], "date_of_birth": person[1], "address": person[2]}


def generate_data():
    """Return 100 labelled citizen/asset pairs. All data is fictional."""
    cases = []
    for i in range(100):
        person_index = i % len(PEOPLE)
        person = PEOPLE[person_index]
        citizen = _record(person)
        asset = deepcopy(citizen)
        actual_match = True
        issue = "Consistent records"

        # A predictable mix of clean pairs, legitimate-looking variations,
        # conflicts, missing values, and pairs belonging to different people.
        pattern = i % 10
        if pattern == 0:
            asset["name"] = person[0].replace("a", "aa", 1)
            issue = "Name variation"
        elif pattern == 1:
            asset["date_of_birth"] = f"{person[1][:4]}-{person[1][5:7]}-{int(person[1][8:]) % 28 + 1:02d}"
            issue = "Date of birth conflict"
        elif pattern == 2:
            asset["address"] = person[2].replace("Road", "Rd")
            issue = "Address mismatch"
        elif pattern == 3:
            asset["address"] = ""
            issue = "Missing field"
        elif pattern == 4:
            other = PEOPLE[(person_index + 1) % len(PEOPLE)]
            asset = _record(other)
            actual_match = False
            issue = "Similar names"
        elif pattern == 5:
            asset["name"] = person[0]
            asset["date_of_birth"] = person[1]
            asset["address"] = person[2]
            issue = "Consistent records"
        elif pattern == 6:
            other = PEOPLE[(person_index + 7) % len(PEOPLE)]
            asset = _record(other)
            actual_match = False
            issue = "Different person"
        elif pattern == 7:
            asset["name"] = person[0].split()[0]
            issue = "Partial name"
        elif pattern == 8:
            asset["date_of_birth"] = ""
            issue = "Missing field"
        else:
            asset["address"] = person[2].replace(" ", "")
            issue = "Address formatting"

        cases.append({
            "case_id": f"CASE-{i + 1:03d}",
            "citizen": citizen,
            "asset": asset,
            "actual_match": actual_match,
            "issue": issue,
        })
    return cases
