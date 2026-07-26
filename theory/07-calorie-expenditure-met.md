# T07 — Calo tiêu hao khi tập (MET)

## App đang dùng gì

`services/workout.py::estimate_calories_burned`:

```
kcal = MET × 3.5 × weight(kg) / 200 × minutes
```

Công thức này suy trực tiếp từ định nghĩa MET (xem dưới). MET tham chiếu app
dùng (`MET_*`):

| Hoạt động | MET |
|-----------|-----|
| Tập tạ cường độ vừa | 5.0 |
| Cardio vừa (đạp xe/aerobic) | 6.0 |
| Cardio mạnh (chạy/aerobic mạnh) | 8.0 |

## Cơ sở

- **1 MET** = mức trao đổi chất lúc nghỉ ≈ **3.5 mL O₂/kg/phút** ≈ **1 kcal/kg/giờ**.
- Từ đó: `kcal/phút = MET × 3.5 × kg / 200` (vì 1 L O₂ ≈ 5 kcal).
- Giá trị MET của từng hoạt động tra trong **Compendium of Physical Activities**
  (Ainsworth và cộng sự, 2011; bản cập nhật 2024). Ví dụ trong Compendium:
  - Đi bộ 4.8 km/h ≈ 3.5 MET
  - Đạp xe nhẹ–vừa ≈ 6.8–8.0 MET
  - Chạy ~9.7 km/h ≈ 9.8 MET
  - Bơi ≈ 5.8–8.3 MET
  - Máy elliptical ≈ 5.0 MET
  - Tập kháng lực: vừa ~3.5–5.0, mạnh ~6.0 MET

## Vì sao quan trọng với SmartMeal

Đây là mắt xích nối **buổi tập → nhật ký dinh dưỡng** (Pha 2 của roadmap): tập
xong lấy MET của bài × cân nặng × thời lượng để ra calo tiêu hao, cộng vào
`daily_log` (tăng "calo được phép nạp" trong ngày). Nên gắn một trường `met`
cho mỗi bài khi mở rộng.

## Hạn chế

- MET là **giá trị trung bình quần thể**, không cá nhân hoá theo thể lực/hiệu
  suất; sai số có thể ±15–30%. Thiết bị đo nhịp tim/vòng đeo cho ước lượng tốt
  hơn nhưng vẫn xấp xỉ.

## Nguồn

- Ainsworth BE, và cộng sự. *2011 Compendium of Physical Activities: a second
  update of codes and MET values.* Med Sci Sports Exerc. 2011;43(8):1575–1581.
- Herrmann SD, và cộng sự. *2024 Adult Compendium of Physical Activities.*
  J Sport Health Sci. 2024. (bản cập nhật.)
- Jetté M, Sidney K, Blümchen G. *Metabolic equivalents (METS) in exercise
  testing…* Clin Cardiol. 1990;13(8):555–565. (nền tảng khái niệm MET.)
