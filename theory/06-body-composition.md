# T06 — Thành phần cơ thể (BMI) & điều chỉnh low-impact

## App đang dùng gì

`services/workout.py::compute_bmi`:

```
BMI = weight(kg) / height(m)²
```

Phân loại + hệ quả:

| BMI | Nhóm (WHO) | Ảnh hưởng tới giáo án |
|-----|------------|-----------------------|
| < 18.5 | Thiếu cân | — |
| 18.5–24.9 | Bình thường | — |
| 25.0–29.9 | Thừa cân | — |
| ≥ 30.0 | Béo phì | → bật **low-impact** |

Luật: `low_impact = (người dùng tự nhận thừa cân) OR (BMI ≥ 30)` → chọn cardio
**tác động thấp** (đạp xe, elliptical, bơi, đi bộ) thay vì chạy/nhảy, nhằm giảm
tải lên khớp gối/hông; đồng thời khởi đầu khối lượng thận trọng hơn.

## Cơ sở

- Phân loại BMI theo **WHO** (Technical Report Series 894, 2000): các ngưỡng
  18.5 / 25 / 30; béo phì chia độ I (30–34.9), II (35–39.9), III (≥40).
- **Người béo phì nên ưu tiên bài tác động thấp** để giảm nguy cơ chấn thương
  khớp do chịu lực (ACSM's Guidelines — quần thể đặc biệt: overweight/obese).

## Hạn chế của BMI (nên biết)

- BMI **không phân biệt mỡ và cơ** → người nhiều cơ có thể bị xếp "thừa cân" oan.
- Nên bổ sung **vòng eo** hoặc **tỉ lệ eo/chiều cao (WHtR)** để đánh giá mỡ nội
  tạng; hoặc đo **% mỡ cơ thể**.
- **Ngưỡng cho người châu Á thấp hơn** (WHO 2004): thừa cân từ BMI ≥ 23, béo phì
  ≥ 27.5 — cân nhắc dùng khi đối tượng chủ yếu là người Việt.

## Nguồn

- World Health Organization. *Obesity: Preventing and Managing the Global
  Epidemic.* WHO Technical Report Series 894. Geneva, 2000.
- WHO Expert Consultation. *Appropriate body-mass index for Asian populations…*
  Lancet. 2004;363(9403):157–163.
- American College of Sports Medicine. *ACSM's Guidelines for Exercise Testing
  and Prescription.* 11th ed. 2021. (mục quần thể thừa cân/béo phì.)
