# T08 — Bảng luật rule-based (map code ↔ lý thuyết)

Tài liệu này liệt kê **chính xác các luật** trong
`services/workout.py::recommend_plan` để bạn kiểm chứng từng dòng. Đầu vào lấy
từ survey: `height, weight, activity_level, overweight, goal` (+ `sex, age` tuỳ
chọn).

## B1. Trình độ khởi điểm ← mức vận động  · `_experience` · [T04]

| activity_level | experience |
|----------------|------------|
| Less Active / Not Sure | beginner |
| More Active | intermediate |

> Thận trọng: chưa có test thể lực nên suy từ mức vận động, mặc định về beginner.

## B2. Tần suất / split / số buổi · `_weekly_plan` · [T04]

| goal | exp | days | split | kháng lực | cardio | phút cardio/tuần |
|------|-----|------|-------|-----------|--------|------------------|
| Gain Muscle | beginner | 3 | Full body | 3 | 1 | 150 |
| Gain Muscle | intermediate | 4 | Upper/Lower | 4 | 1 | 150 |
| Lose Fat | beginner | 4 | Full body | 3 | 2 | 250 |
| Lose Fat | intermediate | 5 | Upper/Lower | 4 | 3 | 300 |
| Maintain | beginner | 3 | Full body | 3 | 1 | 150 |
| Maintain | intermediate | 4 | Upper/Lower | 4 | 2 | 150 |

> Nền WHO (≥150′ cardio + ≥2 buổi kháng lực). Lose Fat nâng cardio 250–300′ theo
> ACSM/Donnelly 2009. Split theo tần suất (3→full body, 4→U/L). [T04]

## B3. Cường độ kháng lực ← goal · `_intensity` · [T04]

| goal | reps | %1RM | sets | RPE |
|------|------|------|------|-----|
| Gain Muscle | 6–12 | 67–85 | 3–4 | 7–9 |
| Lose Fat | 8–15 | 60–75 | 3–4 | 7–8 |
| Maintain | 8–12 | 60–75 | 2–3 | 6–8 |

Override **beginner**: `sets → 2–3`, `RPE → 6–8` (ưu tiên kỹ thuật, chừa rep dự
trữ). Nguồn: bảng tải–rep NSCA. [T04]

## B4. Cường độ cardio ← goal/exp/thể trạng · `_cardio_intensity` · [T05]

- `beginner` **hoặc** `low_impact` **hoặc** goal `Lose Fat` → **50–70% HRR**.
- còn lại → **60–80% HRR**.
- Nếu có `age`: bpm = Karvonen với HRmax = 208 − 0.7·age (Tanaka), HRrest = 70.

## B5. Điều chỉnh tác động thấp ← BMI/thừa cân · [T06]

```
low_impact = overweight == True  OR  BMI ≥ 30
cardio_type = "low-impact" nếu low_impact, ngược lại "mixed"
```
- low-impact: đạp xe tĩnh, elliptical, đi bộ, bơi.
- mixed: thêm chạy, rowing, nhảy dây.

## B6. Phân bổ nhóm cơ theo split · `_sessions` · [T04]

| split | các buổi kháng lực (body parts của ExerciseDB) |
|-------|-----------------------------------------------|
| Full body | chest, back, upper legs, shoulders, upper arms, waist |
| Upper/Lower | Upper: chest, back, shoulders, upper arms, lower arms · Lower: upper legs, lower legs, waist |
| Push/Pull/Legs | Push: chest, shoulders, upper arms · Pull: back, upper arms, lower arms · Legs: upper legs, lower legs, waist |

Buổi cardio: body_part = `cardio`, kèm danh sách equipment theo `cardio_type`.

## B7. Calo tiêu hao mẫu · [T07]

- 45′ kháng lực (MET 5.0) và 30′ cardio (MET 6.0 nếu low-impact, 8.0 nếu mixed),
  nhân theo cân nặng người dùng.

## B8. Tiến triển & miễn trừ

- Progressive overload + deload mỗi 4–6 tuần. [T04]
- Kèm `disclaimer` y tế trong output (khuyến nghị sàng lọc PAR-Q).

---

### Cách kiểm chứng nhanh
Mọi hàm trong `_*` đều **thuần** (không mạng/DB). Có thể chạy:
```python
from app.services.workout import recommend_plan
recommend_plan(height_cm=168, weight_kg=95, activity_level="Not Sure",
               goal="Lose Fat", overweight=True, age=35)
```
và đối chiếu output với các bảng trên + trích dẫn trong từng file [Txx].
