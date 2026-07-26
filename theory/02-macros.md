# T02 — Chia macro (đạm / béo / carb) & thâm hụt / dư calo

## App đang dùng gì

`services/macro.py::calculate_macros`:

```
# 1) Calo mục tiêu theo goal
Lose Fat     : caloric = TDEE × (1 − deficit% / 100)
Gain Muscle  : caloric = TDEE × (1 + surplus% / 100)
Maintain     : caloric = TDEE

# 2) Đạm
bình thường  : protein(g) = daily_protein_per_kg × weight(kg)
thừa cân     : protein(g) = daily_protein_for_overweight_people (cố định)

# 3) Béo (theo % calo)
fat(g) = caloric × daily_fat_percentage / 100 / 9

# 4) Carb = phần còn lại
carb(g) = (caloric − (protein×4 + fat×9)) / 4
```

Hằng số **4 / 4 / 9** = **hệ số Atwater**: 1 g đạm = 4 kcal, 1 g carb = 4 kcal,
1 g béo = 9 kcal (rượu 7 kcal).

## Cơ sở & khoảng giá trị khuyến nghị (app cho chỉnh trong màn survey)

**Đạm** — ISSN: **1.4–2.0 g/kg/ngày** để xây/giữ cơ; giai đoạn cắt mỡ có thể
tới 2.3–3.1 g/kg **khối nạc**. App preset 1.6–2.7 g/kg → nằm trong vùng này.
Người thừa cân dùng mục tiêu **cố định (g)** thay vì theo cân nặng hiện tại vì
cân nặng gồm nhiều mỡ → nhân theo kg sẽ ra đạm quá cao (nên tính theo cân nặng
mục tiêu / khối nạc).

**Béo** — AMDR (IOM): **20–35%** năng lượng; tối thiểu ~0.5–1 g/kg cho nội tiết.
App preset 20–30%.

**Carb** — AMDR **45–65%** năng lượng; ở đây để "phần còn lại" sau đạm & béo.

**Thâm hụt (Lose Fat)** — thường **10–25% TDEE** (hoặc 300–500 kcal/ngày) để
giảm ~0.25–0.5 kg/tuần. App preset 5–15%.

**Dư (Gain Muscle)** — **~10–20% TDEE** (hoặc 250–500 kcal) để tăng cơ, hạn chế
tăng mỡ (Iraki và cộng sự, cho lean bulking). App preset 5–15%.

## Lưu ý về quy tắc "3500 kcal = 0.45 kg"

Quy tắc Wishnofsky (1958) tiện để ước lượng nhanh nhưng **overestimate** giảm
cân dài hạn vì bỏ qua thích nghi chuyển hoá; mô hình động của Hall (2011) chính
xác hơn. Dùng như xấp xỉ, không tuyệt đối.

## Nguồn

- Jäger R, và cộng sự. *ISSN Position Stand: protein and exercise.*
  J Int Soc Sports Nutr. 2017;14:20.
- Thomas DT, Erdman KA, Burke LM. *ACSM/AND/DC Joint Position Statement:
  Nutrition and Athletic Performance.* Med Sci Sports Exerc. 2016;48(3):543–568.
- Institute of Medicine. *Dietary Reference Intakes for Energy, Carbohydrate,
  Fiber, Fat, Fatty Acids, Cholesterol, Protein, and Amino Acids (Macronutrients).*
  2005. (AMDR: béo 20–35%, carb 45–65%, đạm 10–35%.)
- Iraki J, và cộng sự. *Nutrition Recommendations for Bodybuilders in the
  Off-Season.* Sports (Basel). 2019;7(7):154. (thặng dư ~10–20%.)
- Merrill AL, Watt BK. *Energy Value of Foods: Basis and Derivation.* USDA
  Agriculture Handbook No. 74 (hệ số Atwater).
- Wishnofsky M. *Caloric equivalents of gained or lost weight.* Am J Clin Nutr.
  1958;6(5):542–546. — và phản biện: Hall KD, và cộng sự. Lancet. 2011;378(9793):826–837.
