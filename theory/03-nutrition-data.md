# T03 — Nguồn số liệu dinh dưỡng thực phẩm

## App đang dùng gì

`services/nutrition.py` gọi **Edamam Nutrition Analysis API**
(`/api/nutrition-data`, truy vấn dạng `"100 g <tên>"`) để lấy dinh dưỡng
per-100g, rồi nhân theo khối lượng ước lượng để ra dinh dưỡng khẩu phần.

5 chỉ số dùng xuyên suốt app (mã tagname kiểu USDA/Edamam):

| Khoá | Ý nghĩa | Đơn vị |
|------|---------|--------|
| `ENERC_KCAL` | Năng lượng | kcal |
| `PROCNT` | Đạm (protein) | g |
| `FAT` | Chất béo | g |
| `CHOCDF` | Carbohydrate | g |
| `FIBTG` | Chất xơ | g |

## Cơ sở & mức độ uy tín

- **Edamam** tổng hợp dữ liệu chủ yếu từ **USDA** + nhãn sản phẩm. Là nguồn
  tiện cho tra cứu tự động theo tên.
- **Nguồn gốc uy tín nhất (primary source):** **USDA FoodData Central**
  (fdc.nal.usda.gov) — cơ sở dữ liệu thành phần thực phẩm chuẩn của Bộ Nông
  nghiệp Mỹ (SR Legacy, Foundation Foods, FNDDS). Nếu cần đối chiếu/kiểm định
  số liệu, tra trực tiếp tại đây bằng cùng bộ tagname ở trên.
- Việt Nam: **Bảng thành phần thực phẩm Việt Nam** (Viện Dinh dưỡng Quốc gia,
  NXB Y học) là nguồn nội địa cho món/nguyên liệu bản địa.

## Lưu ý độ chính xác

- Dinh dưỡng per-100g là **giá trị trung bình**; giống/giáp mùa/cách chế biến
  làm sai lệch. Khâu **ước lượng khối lượng (gram)** từ ảnh mới là nguồn sai số
  lớn nhất trong chuỗi (xem chú thích trong `services/detector.py`), không phải
  bảng dinh dưỡng.
- Hệ số quy đổi năng lượng dùng **Atwater tổng quát 4/4/9** (xem [T02](02-macros.md)).

## Nguồn

- U.S. Department of Agriculture, Agricultural Research Service.
  *FoodData Central.* fdc.nal.usda.gov.
- Edamam. *Nutrition Analysis API documentation.* developer.edamam.com.
- Viện Dinh dưỡng Quốc gia. *Bảng thành phần thực phẩm Việt Nam.* NXB Y học, 2007.
