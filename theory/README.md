# SmartMeal — Cơ sở lý thuyết & trích dẫn

Thư mục này ghi lại **toàn bộ công thức, hằng số và luật** mà SmartMeal dùng —
từ tính năng lượng/dinh dưỡng đến gợi ý giáo án tập — kèm **nguồn uy tín để
bạn kiểm chứng**. Mỗi tài liệu nêu rõ: (1) app đang dùng gì, (2) công thức &
nguồn, (3) hạn chế / phương án chuẩn hơn.

## Mục lục

| Tag | Tài liệu | Nội dung | Code liên quan |
|-----|----------|----------|----------------|
| T01 | [01-energy-tdee.md](01-energy-tdee.md) | TDEE / năng lượng duy trì | `services/macro.py::calculate_tdee` |
| T02 | [02-macros.md](02-macros.md) | Chia macro (đạm/béo/carb), thâm hụt/dư | `services/macro.py::calculate_macros` |
| T03 | [03-nutrition-data.md](03-nutrition-data.md) | Nguồn số liệu dinh dưỡng thực phẩm | `services/nutrition.py` |
| T04 | [04-exercise-programming.md](04-exercise-programming.md) | FITT-VP, tần suất, split, rep/cường độ | `services/workout.py` |
| T05 | [05-cardio-intensity.md](05-cardio-intensity.md) | %HRR, Karvonen, HRmax, RPE | `services/workout.py::_cardio_intensity` |
| T06 | [06-body-composition.md](06-body-composition.md) | BMI, phân loại, low-impact | `services/workout.py::compute_bmi` |
| T07 | [07-calorie-expenditure-met.md](07-calorie-expenditure-met.md) | MET, calo tiêu hao khi tập | `services/workout.py::estimate_calories_burned` |
| T08 | [08-recommender-rules.md](08-recommender-rules.md) | Bảng luật rule-based (map code ↔ lý thuyết) | `services/workout.py::recommend_plan` |
| — | [references.md](references.md) | Thư mục tham khảo đầy đủ | — |

## Quy ước

- Trong code, mỗi luật gắn tag `[Txx]` trỏ tới tài liệu tương ứng ở trên
  (ví dụ `[T04]` cho lập trình bài tập). Tìm tag trong `08-recommender-rules.md`
  để thấy luật ↔ dòng code ↔ trích dẫn.
- ⚠️ **Miễn trừ y tế:** Các nội dung ở đây phục vụ giáo dục thể chất & dinh
  dưỡng tổng quát cho người trưởng thành khoẻ mạnh; **không thay thế tư vấn y
  tế**. Người có bệnh nền/chấn thương nên hỏi ý kiến chuyên môn (xem PAR-Q).
