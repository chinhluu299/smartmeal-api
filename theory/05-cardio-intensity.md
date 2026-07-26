# T05 — Cường độ cardio (%HRR, Karvonen, HRmax, RPE)

## App đang dùng gì

`services/workout.py::_cardio_intensity` trả về khoảng **%HRR** và (nếu có
tuổi) khoảng **nhịp tim mục tiêu (bpm)** theo Karvonen:

```
HRmax   = 208 − 0.7 × tuổi           # Tanaka 2001
HRrest  = 70                          # mặc định nếu chưa đo
Target HR = (HRmax − HRrest) × %HRR + HRrest     # Karvonen
```

Quy tắc chọn %HRR:
- Người mới / thừa cân / mục tiêu giảm mỡ → **50–70% HRR** (vừa, bền vững).
- Trung cấp mục tiêu duy trì/tăng cơ → **60–80% HRR**.

## Cơ sở

**Phân loại cường độ theo %HRR / %VO₂R (ACSM):**

| Mức | %HRR (hoặc %VO₂R) |
|-----|-------------------|
| Nhẹ | 30–39% |
| **Vừa** | **40–59%** |
| **Mạnh** | **60–89%** |

**HRmax:**
- `220 − tuổi` (Fox, 1971) — phổ biến nhưng sai số lớn (±10–12 bpm).
- **`208 − 0.7 × tuổi` (Tanaka và cộng sự, 2001)** — chính xác hơn trên dải tuổi
  rộng → app dùng cái này.

**Karvonen (Heart Rate Reserve):** dùng HRR = HRmax − HRrest cho mục tiêu cá
nhân hoá hơn %HRmax thuần. HRrest lý tưởng là đo lúc mới ngủ dậy; app mặc định
70 bpm khi chưa có.

**RPE (thay thế khi không đo nhịp tim):** thang **Borg 6–20** (hoặc CR10). Vừa ≈
12–13 ("hơi gắng sức"), mạnh ≈ 14–17. "Talk test": còn nói được câu ngắn = vừa.

## Ghi chú triển khai

- App **không thu thập tuổi trong survey** → mặc định chỉ hiện %HRR + RPE; nếu
  truyền `age` vào `/workout/recommend` sẽ ra luôn khoảng bpm. Muốn dùng đầy đủ
  nên thêm câu hỏi tuổi (và lý tưởng là HR nghỉ) vào survey.

## Nguồn

- Tanaka H, Monahan KD, Seals DR. *Age-predicted maximal heart rate revisited.*
  J Am Coll Cardiol. 2001;37(1):153–156.
- Karvonen MJ, Kentala E, Mustala O. *The effects of training on heart rate; a
  longitudinal study.* Ann Med Exp Biol Fenn. 1957;35(3):307–315.
- American College of Sports Medicine. *ACSM's Guidelines for Exercise Testing
  and Prescription.* 11th ed. 2021. (bảng phân loại cường độ.)
- Borg GA. *Psychophysical bases of perceived exertion.* Med Sci Sports Exerc.
  1982;14(5):377–381.
