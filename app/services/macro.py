"""Service tính TDEE (Total Daily Energy Expenditure).

Logic lấy theo method-1 của Nutrition Warrior:
    TDEE = weight(kg) * factor * KG_TO_LBS
"""

KG_TO_LBS = 2.20462262

# Hệ số calo theo mức vận động
ACTIVITY_FACTOR = {
    "Less Active": 14,
    "Not Sure": 16,
    "More Active": 18,
}


def calculate_tdee(weight: float, activity_level: str) -> float:
    factor = ACTIVITY_FACTOR.get(activity_level)
    if factor is None:
        raise ValueError("activity_level không hợp lệ")
    return weight * factor * KG_TO_LBS


def calculate_macros(
    goal: str,
    weight: float,
    tdee: float,
    *,
    overweight: bool = False,
    daily_protein_per_kg: float = 1.8,
    daily_protein_for_overweight_people: float = 0.0,
    daily_fat_percentage: float = 25.0,
    deficit_percentage: float = 0.0,
    surplus_percentage: float = 0.0,
) -> dict:
    """Tính mục tiêu macro theo TDEE và mục tiêu tập luyện (port từ NW).

    - goal "Lose Fat": ăn thiếu hụt `deficit_percentage`% so với TDEE.
    - goal "Gain Muscle": ăn dư `surplus_percentage`% so với TDEE.
    - goal "Maintain": ăn bằng TDEE.
    Protein theo kg cân nặng (hoặc giá trị cố định nếu thừa cân), chất béo theo
    % calo, carb là phần còn lại.
    """
    if goal == "Lose Fat":
        caloric_intake = tdee * (1 - deficit_percentage / 100)
    elif goal == "Gain Muscle":
        caloric_intake = tdee * (1 + surplus_percentage / 100)
    elif goal == "Maintain":
        caloric_intake = tdee
    else:
        raise ValueError("goal không hợp lệ (Lose Fat | Maintain | Gain Muscle)")

    if overweight:
        daily_protein = daily_protein_for_overweight_people
    else:
        daily_protein = daily_protein_per_kg * weight

    daily_fat = caloric_intake * daily_fat_percentage / 100 / 9
    daily_carb = (caloric_intake - (daily_protein * 4 + daily_fat * 9)) / 4

    return {
        "goal": goal,
        "caloric_intake_goal": caloric_intake,
        "daily_protein_goal": daily_protein,
        "daily_fat_goal": daily_fat,
        "daily_carb_goal": daily_carb,
    }
