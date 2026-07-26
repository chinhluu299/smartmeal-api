"""Gợi ý giáo án tập luyện theo hiện trạng cơ thể — RULE-BASED (minh bạch).

Toàn bộ luật dưới đây bám theo các khung lý thuyết chuẩn; mỗi luật gắn tag
[Txx] trỏ tới tài liệu trong thư mục `theory/` để kiểm chứng:

- [T04] ACSM FITT-VP + WHO 2020 + NSCA (tần suất, split, rep/cường độ kháng lực)
- [T05] Cường độ cardio: %HRR (ACSM) + Karvonen + HRmax Tanaka
- [T06] BMI (WHO) — phân loại & điều chỉnh low-impact
- [T07] MET / Compendium of Physical Activities (Ainsworth 2011) — calo tiêu hao

Hàm cốt lõi đều THUẦN (không gọi mạng/DB) để dễ test và giải thích được.
"""

# --- Nhóm body part của ExerciseDB dùng để phân bổ buổi tập ---------------
UPPER = ["chest", "back", "shoulders", "upper arms", "lower arms"]
LOWER = ["upper legs", "lower legs", "waist"]
PUSH = ["chest", "shoulders", "upper arms"]
PULL = ["back", "upper arms", "lower arms"]
LEGS = ["upper legs", "lower legs", "waist"]
FULL_BODY = ["chest", "back", "upper legs", "shoulders", "upper arms", "waist"]

# Cardio (equipment ExerciseDB) — tách low-impact vs mọi loại. [T06]
CARDIO_LOW_IMPACT = ["stationary bike", "elliptical machine", "walking", "swimming"]
CARDIO_MIXED = CARDIO_LOW_IMPACT + ["running", "rowing", "jump rope"]

# MET tham chiếu (Ainsworth 2011 Compendium) cho ước lượng calo. [T07]
MET_RESISTANCE = 5.0      # tập tạ cường độ vừa (code 02050 ~5.0)
MET_CARDIO_MODERATE = 6.0  # đạp xe/aerobic vừa
MET_CARDIO_VIGOROUS = 8.0  # chạy/aerobic mạnh

# Thiết bị "phổ thông" ưu tiên khi chọn bài (tránh máy lạ, ít gặp). Nhóm
# low-impact thiên về máy/cáp/tạ đơn/dây kháng lực để nhẹ khớp. [T04][T06]
_COMMON_EQUIP = {
    "barbell", "dumbbell", "cable", "body weight", "kettlebell",
    "leverage machine", "smith machine", "ez barbell", "band", "resistance band",
}
_LOW_IMPACT_EQUIP = {
    "cable", "leverage machine", "smith machine", "body weight",
    "band", "resistance band", "dumbbell",
}


def compute_bmi(height_cm: float, weight_kg: float):
    """BMI + phân loại theo WHO (TRS 894, 2000). [T06]"""
    h = (height_cm or 0) / 100
    if h <= 0 or not weight_kg:
        return None, "unknown"
    bmi = weight_kg / (h * h)
    if bmi < 18.5:
        cat = "underweight"
    elif bmi < 25:
        cat = "normal"
    elif bmi < 30:
        cat = "overweight"
    else:
        cat = "obese"
    return round(bmi, 1), cat


def estimate_calories_burned(met: float, weight_kg: float, minutes: float) -> float:
    """Calo tiêu hao ≈ MET × 3.5 × kg / 200 × phút (từ định nghĩa MET). [T07]"""
    if not (met and weight_kg and minutes):
        return 0.0
    return round(met * 3.5 * weight_kg / 200 * minutes, 1)


def _experience(activity_level: str) -> str:
    """Suy ra trình độ khởi điểm từ mức vận động (thận trọng). [T04]"""
    return "intermediate" if activity_level == "More Active" else "beginner"


def _intensity(goal: str, experience: str) -> dict:
    """Rep range / %1RM / sets / RPE theo mục tiêu (NSCA). [T04]

    - Gain Muscle (phì đại cơ): 6–12 reps, 67–85% 1RM.
    - Lose Fat: 8–15 reps, giữ cơ + chuyển hoá cao.
    - Maintain / thể lực chung: 8–12 reps.
    Người mới: giảm tải, RPE thấp hơn (chừa 2–3 rep dự trữ), tối đa 3 set.
    """
    if goal == "Gain Muscle":
        base = {"rep_range": [6, 12], "pct_1rm": [67, 85], "sets": [3, 4], "rpe": [7, 9]}
    elif goal == "Lose Fat":
        base = {"rep_range": [8, 15], "pct_1rm": [60, 75], "sets": [3, 4], "rpe": [7, 8]}
    else:  # Maintain
        base = {"rep_range": [8, 12], "pct_1rm": [60, 75], "sets": [2, 3], "rpe": [6, 8]}

    if experience == "beginner":
        base["sets"] = [2, min(3, base["sets"][1])]
        base["rpe"] = [6, 8]  # kỹ thuật là ưu tiên, chừa rep dự trữ
    return base


def _cardio_intensity(goal: str, experience: str, low_impact: bool, age):
    """Cường độ cardio theo %HRR (ACSM) + Karvonen; kèm BPM nếu có tuổi. [T05]

    - Vừa: 40–59% HRR; Mạnh: 60–89% HRR (ACSM).
    - Người mới / thừa cân / mục tiêu giảm mỡ: 50–70% HRR (bền vững, an toàn).
    """
    if experience == "beginner" or low_impact or goal == "Lose Fat":
        hrr = [50, 70]
    else:
        hrr = [60, 80]

    bpm = None
    if age:
        hr_max = round(208 - 0.7 * age)  # Tanaka 2001 (chuẩn hơn 220−tuổi) [T05]
        hr_rest = 70  # mặc định nếu chưa đo
        # Karvonen: HR = (HRmax − HRrest) × %HRR + HRrest
        bpm = [round((hr_max - hr_rest) * p / 100 + hr_rest) for p in hrr]
    return {"hrr_pct": hrr, "target_bpm": bpm}


def _weekly_plan(goal: str, experience: str):
    """Tần suất, split, số buổi kháng lực/cardio, tổng phút cardio/tuần.

    Mốc nền WHO 2020: ≥150 phút cardio vừa/tuần + ≥2 buổi kháng lực. [T04]
    Giảm mỡ: tăng khối lượng cardio (ACSM ~200–300 phút/tuần cho giảm cân). [T04]
    """
    if goal == "Gain Muscle":
        if experience == "beginner":
            return dict(days=3, split="Full body", resistance=3, cardio=1, cardio_min=150)
        return dict(days=4, split="Upper/Lower", resistance=4, cardio=1, cardio_min=150)
    if goal == "Lose Fat":
        if experience == "beginner":
            return dict(days=4, split="Full body", resistance=3, cardio=2, cardio_min=250)
        return dict(days=5, split="Upper/Lower", resistance=4, cardio=3, cardio_min=300)
    # Maintain
    if experience == "beginner":
        return dict(days=3, split="Full body", resistance=3, cardio=1, cardio_min=150)
    return dict(days=4, split="Upper/Lower", resistance=4, cardio=2, cardio_min=150)


def _sessions(split: str, resistance: int, cardio: int, cardio_type: str, cardio_min: int):
    """Sinh danh sách buổi trong tuần (thứ tự xen kẽ để hồi phục). [T04]"""
    if split == "Upper/Lower":
        res_focus = [("Upper body", UPPER), ("Lower body", LOWER)]
    elif split == "Push/Pull/Legs":
        res_focus = [("Push", PUSH), ("Pull", PULL), ("Legs", LEGS)]
    else:
        res_focus = [("Full body", FULL_BODY)]

    sessions = []
    for i in range(resistance):
        focus, parts = res_focus[i % len(res_focus)]
        sessions.append(
            {"type": "resistance", "focus": focus, "body_parts": parts}
        )
    per_cardio = round(cardio_min / cardio) if cardio else 0
    for _ in range(cardio):
        sessions.append(
            {
                "type": "cardio",
                "focus": "Cardio (%s)" % ("low-impact" if cardio_type == "low-impact" else "mixed"),
                "body_parts": ["cardio"],
                "equipment": CARDIO_LOW_IMPACT if cardio_type == "low-impact" else CARDIO_MIXED,
                "minutes": per_cardio,
            }
        )
    return sessions


# Phân bổ buổi vào các thứ trong tuần cho giãn cách hồi phục (0=T2 … 6=CN). [T04]
_WEEKDAY_SPREAD = {
    1: [0],
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 4, 5],
    6: [0, 1, 2, 3, 4, 5],
    7: [0, 1, 2, 3, 4, 5, 6],
}


def default_weekday_spread(days: int) -> list:
    """Gợi ý các thứ trong tuần cho `days` buổi, giãn cách để hồi phục."""
    return _WEEKDAY_SPREAD.get(max(1, min(7, days)), [0, 2, 4])


def _exercises_per_session(parts: list) -> int:
    """Số bài mỗi buổi kháng lực: ~1 bài/nhóm cơ, gói trong khoảng 4–6 bài."""
    return min(6, max(4, len(parts)))


def _select_for_session(body_parts: list, rotate: int, low_impact: bool) -> list:
    """Chọn bài tập CỤ THỂ cho 1 buổi, cân đối giữa các nhóm cơ (round-robin).

    - Ưu tiên thiết bị phổ thông (low-impact nếu cần bảo vệ khớp).
    - `rotate` lệch điểm bắt đầu để các buổi trùng nhóm (vd 2 buổi Upper/tuần)
      không ra cùng danh sách bài.
    Gọi DB bài tập (services/exercise); lỗi/không có DB thì trả [] để giáo án
    vẫn hiển thị theo nhóm cơ như trước.
    """
    from .exercise import get_exercises_by_body_part

    parts = [p for p in body_parts if p != "cardio"]
    if not parts:
        return []
    total = _exercises_per_session(parts)
    pref = _LOW_IMPACT_EQUIP if low_impact else _COMMON_EQUIP

    pools = {}
    for p in parts:
        try:
            pool = get_exercises_by_body_part(p, limit="60") or []
        except Exception:
            pool = []
        filtered = [e for e in pool if (e.get("equipment") or "").lower() in pref]
        pools[p] = filtered or pool

    picked, seen = [], set()
    cursor = {p: rotate for p in parts}
    while len(picked) < total:
        progressed = False
        for p in parts:
            if len(picked) >= total:
                break
            pool = pools.get(p) or []
            if not pool:
                continue
            for _ in range(len(pool)):  # tiến tới bài chưa chọn
                ex = pool[cursor[p] % len(pool)]
                cursor[p] += 1
                if ex.get("id") not in seen:
                    seen.add(ex.get("id"))
                    picked.append(ex)
                    progressed = True
                    break
        if not progressed:  # mọi pool đã cạn
            break
    return picked


def _attach_exercises(sessions: list, intensity: dict, low_impact: bool) -> None:
    """Điền bài tập cụ thể + liều lượng (set×rep) vào từng buổi kháng lực."""
    sets = intensity["sets"]
    reps = intensity["rep_range"]
    prescription = f"{sets[0]}–{sets[1]} set × {reps[0]}–{reps[1]} reps"
    seen_focus = {}
    for s in sessions:
        if s.get("type") != "resistance":
            continue
        rotate = seen_focus.get(s["focus"], 0)
        seen_focus[s["focus"]] = rotate + 1
        chosen = _select_for_session(s["body_parts"], rotate, low_impact)
        s["exercises"] = [
            {**ex, "sets": sets, "rep_range": reps, "prescription": prescription}
            for ex in chosen
        ]


def recommend_plan(
    *,
    height_cm: float,
    weight_kg: float,
    activity_level: str,
    goal: str,
    overweight: bool = False,
    sex: str | None = None,
    age: int | None = None,
) -> dict:
    """Sinh giáo án tuần rule-based + phần giải thích (rationale) có trích dẫn."""
    if goal not in ("Lose Fat", "Gain Muscle", "Maintain"):
        raise ValueError("goal không hợp lệ (Lose Fat | Gain Muscle | Maintain)")

    bmi, bmi_cat = compute_bmi(height_cm, weight_kg)
    experience = _experience(activity_level)
    # Ưu tiên tập tác động thấp nếu tự nhận thừa cân hoặc BMI ≥ 30 (béo phì). [T06]
    low_impact = bool(overweight) or (bmi is not None and bmi >= 30)
    cardio_type = "low-impact" if low_impact else "mixed"

    wp = _weekly_plan(goal, experience)
    intensity = _intensity(goal, experience)
    cardio = _cardio_intensity(goal, experience, low_impact, age)
    sessions = _sessions(
        wp["split"], wp["resistance"], wp["cardio"], cardio_type, wp["cardio_min"]
    )
    # Điền bài tập cụ thể vào mỗi buổi kháng lực (cần DB bài tập). Nếu lỗi/không
    # có DB, giáo án vẫn trả về theo nhóm cơ như cũ.
    try:
        _attach_exercises(sessions, intensity, low_impact)
    except Exception:
        pass

    # Calo tiêu hao ước tính cho TỪNG buổi (dùng khi đánh dấu hoàn thành). [T07]
    for s in sessions:
        if s["type"] == "cardio":
            met = MET_CARDIO_MODERATE if low_impact else MET_CARDIO_VIGOROUS
            s["est_calories"] = estimate_calories_burned(met, weight_kg, s.get("minutes") or 30)
        else:
            s["est_calories"] = estimate_calories_burned(MET_RESISTANCE, weight_kg, 45)

    # Ước lượng calo tiêu hao mẫu (45' kháng lực, 30' cardio) theo cân nặng. [T07]
    burn = {
        "resistance_45min": estimate_calories_burned(MET_RESISTANCE, weight_kg, 45),
        "cardio_30min": estimate_calories_burned(
            MET_CARDIO_MODERATE if low_impact else MET_CARDIO_VIGOROUS, weight_kg, 30
        ),
    }

    rationale = [
        f"[T06] BMI {bmi} → nhóm '{bmi_cat}' (phân loại WHO).",
        f"[T04] Mức vận động '{activity_level}' → trình độ '{experience}' "
        f"→ {wp['days']} buổi/tuần, split {wp['split']}.",
        f"[T04] Mục tiêu '{goal}' → {intensity['rep_range'][0]}–{intensity['rep_range'][1]} reps, "
        f"{intensity['pct_1rm'][0]}–{intensity['pct_1rm'][1]}% 1RM, "
        f"{intensity['sets'][0]}–{intensity['sets'][1]} set/bài (NSCA).",
        f"[T04] Nền WHO: {wp['cardio_min']} phút cardio/tuần + {wp['resistance']} buổi kháng lực.",
        f"[T05] Cardio {cardio['hrr_pct'][0]}–{cardio['hrr_pct'][1]}% HRR"
        + (f" ≈ {cardio['target_bpm'][0]}–{cardio['target_bpm'][1]} bpm (Karvonen/Tanaka)." if cardio["target_bpm"] else " (ACSM; thêm tuổi để ra nhịp tim mục tiêu)."),
    ]
    if low_impact:
        rationale.append(
            "[T06] Thừa cân/BMI cao → ưu tiên cardio TÁC ĐỘNG THẤP (đạp xe, elliptical, bơi) để bảo vệ khớp."
        )
    if experience == "beginner":
        rationale.append(
            "[T04] Người mới → khởi đầu khối lượng thấp, ưu tiên kỹ thuật, RPE 6–8 (chừa rep dự trữ)."
        )

    return {
        "profile": {
            "sex": sex,
            "age": age,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "bmi_category": bmi_cat,
            "experience": experience,
            "goal": goal,
        },
        "days_per_week": wp["days"],
        "split": wp["split"],
        "resistance_days": wp["resistance"],
        "cardio_days": wp["cardio"],
        "weekly_cardio_minutes": wp["cardio_min"],
        "low_impact": low_impact,
        "cardio_type": cardio_type,
        "resistance_intensity": intensity,
        "cardio_intensity": cardio,
        "sessions": sessions,
        "estimated_calories_burned": burn,
        "progression": (
            "[T04] Progressive overload: khi hoàn thành mức rep cao nhất với kỹ thuật tốt "
            "ở TẤT CẢ các set, tăng tải ~2.5–5% hoặc +1 rep. Deload/đánh giá lại mỗi 4–6 tuần."
        ),
        "disclaimer": (
            "Gợi ý mang tính giáo dục thể chất tổng quát, không thay thế tư vấn y tế. "
            "Nên sàng lọc PAR-Q và hỏi ý kiến bác sĩ nếu có bệnh nền/chấn thương."
        ),
        "rationale": rationale,
    }


def save_schedule(user_id: str, schedule: dict) -> dict:
    """Lưu lịch tập tuần (đã gán buổi vào các thứ) vào user. Trả user đã serialize.

    Import cục bộ để giữ các hàm tính giáo án ở trên thuần (không phụ thuộc DB).
    """
    from bson import ObjectId

    from ..core.database import get_users_collection
    from .user import serialize_user, get_user_by_id

    get_user_by_id(user_id)  # xác thực tồn tại (ném UserError nếu không)
    result = get_users_collection().find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": {"workout_schedule": schedule}},
        return_document=True,
    )
    return serialize_user(result)
