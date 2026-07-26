# T01 — Năng lượng tiêu hao hằng ngày (TDEE)

## App đang dùng gì

`services/macro.py::calculate_tdee` (method-1, port từ Nutrition Warrior):

```
TDEE = weight(kg) × factor × 2.20462
factor = 14 (Less Active) | 16 (Not Sure) | 18 (More Active)
```

Bản chất `weight × 2.20462` = cân nặng đổi ra **pound (lb)**, nên công thức là:

```
TDEE ≈ (14 | 16 | 18) kcal cho mỗi pound thể trọng / ngày
```

## Cơ sở & mức độ uy tín

Đây là **heuristic "calo trên mỗi pound thể trọng"** (14/16/18 kcal/lb cho mức
vận động thấp/vừa/cao) — một quy tắc thực hành phổ biến trong huấn luyện thể
hình/dinh dưỡng. **Ưu điểm:** đơn giản, chỉ cần cân nặng. **Hạn chế:** không
tính chiều cao, tuổi, giới, thành phần cơ thể → kém chính xác cho người rất gầy
/ béo, và không có nguồn peer-review trực tiếp.

## Phương án chuẩn hơn (khuyến nghị nếu muốn nâng cấp)

Tính **RMR/BMR** bằng phương trình đã kiểm định, rồi nhân **hệ số vận động (PAL)**:

**Mifflin–St Jeor (1990)** — chính xác nhất cho người khoẻ mạnh không béo phì:
```
Nam : RMR = 10·W + 6.25·H − 5·A + 5
Nữ  : RMR = 10·W + 6.25·H − 5·A − 161      (W: kg, H: cm, A: tuổi)
TDEE = RMR × PAL
```
PAL thường dùng: ít vận động 1.2 · nhẹ 1.375 · vừa 1.55 · nhiều 1.725 · rất nhiều 1.9.

Phương án khác: **Harris–Benedict** (1919; hiệu chỉnh Roza–Shizgal 1984),
**Katch–McArdle** (dựa trên khối nạc: `RMR = 370 + 21.6·LBM(kg)` — tốt khi biết % mỡ).

## Nguồn

- Mifflin MD, St Jeor ST, và cộng sự. *A new predictive equation for resting
  energy expenditure in healthy individuals.* Am J Clin Nutr. 1990;51(2):241–247.
- Harris JA, Benedict FG. *A Biometric Study of Basal Metabolism in Man.*
  Carnegie Institution, 1919. (Hiệu chỉnh: Roza AM, Shizgal HM. Am J Clin Nutr. 1984;40(1):168–182.)
- Frankenfield D, và cộng sự. *Comparison of predictive equations for resting
  metabolic rate…* J Am Diet Assoc. 2005;105(5):775–789. (Kết luận Mifflin–St Jeor tin cậy nhất.)
- FAO/WHO/UNU. *Human energy requirements.* 2004 (khái niệm PAL).
