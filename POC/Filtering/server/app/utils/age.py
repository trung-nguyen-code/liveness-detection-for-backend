from datetime import date


def is_valid_range(age_begin, age_end):
    if age_begin >= age_end:
        return False
    if abs(age_begin - age_end) > 40:
        return False
    if age_begin <= 18 or age_end >= 99:
        return False
    return True


def calculateAge(birthDate):
    today = date.today()
    age = (
        today.year
        - birthDate.year
        - ((today.month, today.day) < (birthDate.month, birthDate.day))
    )

    return age