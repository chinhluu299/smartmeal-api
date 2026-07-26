# T04 — Lập trình bài tập (FITT-VP, tần suất, split, cường độ kháng lực)

## Khung nền: FITT-VP (ACSM)

Mọi giáo án được mô tả bằng 6 biến (ACSM's Guidelines, 11th ed):

- **F**requency — số buổi/tuần
- **I**ntensity — cường độ (%1RM, RPE, %HRR)
- **T**ime — thời lượng buổi
- **T**ype — loại hình (kháng lực / cardio…)
- **V**olume — tổng khối lượng (set × rep × tải)
- **P**rogression — cách tăng tiến

## Mức khuyến nghị tối thiểu (dùng làm mặc định an toàn)

**WHO 2020** & **Physical Activity Guidelines for Americans (2018)** cho người
trưởng thành:
- Aerobic: **150–300 phút/tuần cường độ vừa** *hoặc* 75–150 phút mạnh.
- Kháng lực: **≥2 buổi/tuần** cho các nhóm cơ chính.

→ App đặt nền `cardio_min ≥ 150` và `resistance ≥ 2–3` buổi. Với **giảm cân**,
ACSM (Donnelly 2009) khuyến nghị **>250 phút/tuần** để giảm cân có ý nghĩa lâm
sàng → app nâng lên 250–300 phút cho goal Lose Fat.

## Rep range / cường độ kháng lực theo mục tiêu (NSCA)

Bảng tải–rep (NSCA Essentials, 4th ed; ACSM progression position stand):

| Mục tiêu | Rep | %1RM | Ghi chú |
|----------|-----|------|---------|
| Sức mạnh tối đa | ≤6 | ≥85% | ít rep, nghỉ dài |
| **Phì đại cơ (hypertrophy)** | **6–12** | **67–85%** | dùng cho Gain Muscle |
| Sức bền cơ | ≥12 | ≤67% | — |

App map: **Gain Muscle → 6–12 reps / 67–85%**; **Lose Fat → 8–15 reps / 60–75%**
(giữ cơ + chuyển hoá, khối lượng cao hơn chút); **Maintain → 8–12 / 60–75%**.
Set: người mới 2–3 set (ưu tiên kỹ thuật), tiến bộ hơn 3–4 set.

## Chia buổi (split) theo tần suất

- 3 buổi → **Full body** (mỗi nhóm cơ ~2–3 lần/tuần, tốt cho người mới).
- 4 buổi → **Upper/Lower**.
- 5–6 buổi → **Push/Pull/Legs**.
Cơ sở: tần suất tập mỗi nhóm cơ ~2 lần/tuần tối ưu hơn 1 lần cho phì đại
(Schoenfeld và cộng sự, 2016, meta-analysis).

## Tiến triển & chu kỳ hoá (Progression / Periodization)

- **Progressive overload:** khi đạt mức rep cao nhất với kỹ thuật tốt ở **tất
  cả** set → tăng tải ~2.5–5% hoặc +1 rep.
- **Deload / đánh giá lại mỗi 4–6 tuần**; luân phiên khối lượng–cường độ
  (periodization) để tránh chững và quá tải.

## Nguồn

- American College of Sports Medicine. *ACSM's Guidelines for Exercise Testing
  and Prescription.* 11th ed. Wolters Kluwer, 2021. (FITT-VP.)
- World Health Organization. *WHO Guidelines on Physical Activity and Sedentary
  Behaviour.* 2020.
- U.S. Dept. of Health and Human Services. *Physical Activity Guidelines for
  Americans.* 2nd ed. 2018.
- Haff GG, Triplett NT (eds). *Essentials of Strength Training and Conditioning.*
  4th ed. NSCA / Human Kinetics, 2016.
- Ratamess NA, và cộng sự. *ACSM Position Stand: Progression Models in
  Resistance Training for Healthy Adults.* Med Sci Sports Exerc. 2009;41(3):687–708.
- Donnelly JE, và cộng sự. *ACSM Position Stand: Appropriate Physical Activity
  Intervention Strategies for Weight Loss…* Med Sci Sports Exerc. 2009;41(2):459–471.
- Schoenfeld BJ, Ogborn D, Krieger JW. *Effects of resistance training frequency
  on measures of muscle hypertrophy: a meta-analysis.* Sports Med. 2016;46(11):1689–1697.
