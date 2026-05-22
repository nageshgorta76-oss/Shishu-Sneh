VACCINE_SCHEDULE = [
    {
        "code": "BCG",
        "due_month": 0.0,
        "due_label": "at_birth",
        "disease_key": "tuberculosis",
    },
    {
        "code": "Polio",
        "due_month": 1.5,
        "due_label": "six_weeks",
        "disease_key": "polio",
    },
    {
        "code": "Hepatitis B",
        "due_month": 1.5,
        "due_label": "six_weeks",
        "disease_key": "hepatitis_b",
    },
    {
        "code": "DPT",
        "due_month": 2.5,
        "due_label": "ten_weeks",
        "disease_key": "dpt_combo",
    },
    {
        "code": "MMR",
        "due_month": 9.0,
        "due_label": "nine_months",
        "disease_key": "mmr_combo",
    },
]


def get_vaccine_guidance(age_months):
    due_now = []
    due_soon = []
    upcoming = []

    for vaccine in VACCINE_SCHEDULE:
        due_month = vaccine["due_month"]

        if due_month == 0 and age_months == 0:
            due_now.append(vaccine)
        elif due_month > 0 and due_month <= age_months < due_month + 1:
            due_now.append(vaccine)
        elif 0 < due_month - age_months <= 1:
            due_soon.append(vaccine)
        elif due_month > age_months:
            upcoming.append(vaccine)

    return {
        "due_now": due_now,
        "due_soon": due_soon,
        "upcoming": upcoming,
    }
