"""Chuẩn hoá tên lớp của 3 mô hình nhận diện về một bộ tên chung.

App chạy đồng thời 3 mô hình để bắt được nhiều vật thể hơn:

1. `best.pt`      — 120 lớp nguyên liệu, tự huấn luyện (100 epoch). Mạnh ở nguyên
   liệu thô: rau củ, đậu, thịt cá, gia vị.
2. `nw-90class.pt` — 90 lớp, mô hình của dự án Nutrition-Warrior. Phủ trái cây phổ
   thông, món phương Tây, hải sản, đồ uống và **10 món Việt**.
3. `reference.pt`  — YOLO11n gốc, 80 lớp MS-COCO. Vừa tìm vật tham chiếu để quy đổi
   kích thước, vừa bổ sung 10 lớp thực phẩm phổ thông.

Ba mô hình gọi cùng một thứ bằng những tên khác nhau ("Apple" / "Apple" / "apple",
"hot-dog" / "Hot-dog" / "hot dog"), và bộ 120 lớp còn kèm tên địa phương trong dấu
gạch ("Sponge Gourd -Ghiraula-"). Nếu không chuẩn hoá thì cùng một quả táo sẽ hiện
ra ba dòng khác nhau trong kết quả quét.

Module này là nguồn duy nhất quy định:
- `canonical()` — tên chung, dùng để gộp trùng và tra bảng khối lượng
- `display()`   — tên hiển thị trên app
- `edamam_query()` — chuỗi tiếng Anh để tra dinh dưỡng
"""

import re

# 10 lớp thực phẩm trong 80 lớp MS-COCO của `reference.pt`. Các lớp COCO còn lại
# không phải thực phẩm nên bỏ qua (trừ nhóm vật tham chiếu, xử lý riêng ở
# detector.py).
COCO_FOOD_CLASSES = frozenset({
    "apple", "banana", "orange", "broccoli", "carrot",
    "sandwich", "hot dog", "pizza", "donut", "cake",
})

# Các lớp "bao trùm" của mô hình Nutrition-Warrior: chỉ nói vật đó là đồ ăn chứ
# không nói là món gì, nên không tra được dinh dưỡng và cũng không giúp gì cho
# người dùng. Bỏ hẳn để khỏi làm rối kết quả quét.
GENERIC_CLASSES = frozenset({
    "food", "food-drinks", "Fruit", "Vegetable", "Baked-goods", "Dessert",
})

# Bộ 120 lớp đặt tên theo dữ liệu Nepal, phần lớn kèm tên địa phương ở cuối trong
# dấu gạch: "Sponge Gourd -Ghiraula-" -> "Sponge Gourd".
_LOCAL_NAME_SUFFIX = re.compile(r"\s*-[^-]*-\s*$")

# Tên lớp thô (của bất kỳ mô hình nào) -> tên chung. Chỉ liệt kê những tên mà
# việc chuẩn hoá tự động không ra tên thực phẩm tiếng Anh phổ thông.
ALIASES = {
    # --- tên vùng miền -> tên phổ thông ---
    "Brinjal": "eggplant",
    "Green Brinjal": "eggplant",
    "Capsicum": "bell pepper",
    "Ash Gourd -Kubhindo-": "winter melon",
    "Sponge Gourd -Ghiraula-": "ridge gourd",
    "Tree Tomato -Rukh Tamatar-": "tamarillo",
    "Long Beans -Bodi-": "yardlong beans",
    "Broad Beans -Bakullo-": "fava beans",
    "Coriander -Dhaniya-": "cilantro",
    "Green Mint -Pudina-": "mint",
    "Beaten Rice -Chiura-": "flattened rice",
    "Minced Meat": "ground beef",
    "Buff Meat": "buffalo meat",
    "noodle": "noodles",
    # --- tên thuần Nepal (hậu tố mới là tên tiếng Anh, hoặc không có tên Anh) ---
    "Akabare Khursani": "red chili pepper",
    "Palak -Indian Spinach-": "spinach",
    "Palungo -Nepali Spinach-": "spinach",
    "Lapsi -Nepali Hog Plum-": "hog plum",
    "Nutrela -Soya Chunks-": "soy chunks",
    "Sajjyun -Moringa Drumsticks-": "moringa drumsticks",
    "Soyabean -Bhatmas-": "soybeans",
    "Green Soyabean -Hariyo Bhatmas-": "edamame",
    "Bethu ko Saag": "lambsquarters",
    "Farsi ko Munta": "pumpkin leaves",
    "Rayo ko Saag": "mustard greens",
    "Tori ko Saag": "mustard greens",
    "Gundruk": "fermented mustard greens",
    "Rahar ko Daal": "pigeon peas",
    # --- lỗi chính tả / trùng lặp trong dữ liệu gốc ---
    "Cornflakec": "cornflakes",
    "Wallnut": "walnut",
    # --- mô hình Nutrition-Warrior ---
    "Common-fig": "fig",
    "Submarine-sandwich": "submarine sandwich",
    "Hamburger": "burger",
    "Doughnut": "donut",
    "Squash": "winter squash",
}

# Tên chung -> tên hiển thị, dùng khi `.title()` cho ra chữ không đẹp. Chủ yếu là
# 10 món Việt của mô hình Nutrition-Warrior: hiển thị đúng dấu tiếng Việt.
DISPLAY_OVERRIDES = {
    "banh mi": "Bánh mì",
    "banh trang tron": "Bánh tráng trộn",
    "banh xeo": "Bánh xèo",
    "bun bo hue": "Bún bò Huế",
    "bun dau": "Bún đậu",
    "com tam": "Cơm tấm",
    "goi cuon": "Gỏi cuốn",
    "pho": "Phở",
    "hu tieu": "Hủ tiếu",
    "xoi": "Xôi",
}

# Tên chung -> chuỗi tra Edamam. Chỉ khai những tên mà Edamam không nhận diện
# được, chủ yếu là món Việt: Edamam CHỈ hỗ trợ tiếng Anh nên "pho" không ra kết
# quả, phải hỏi bằng tên mô tả.
#
# LƯU Ý: đây là XẤP XỈ theo món tương đương gần nhất, không phải công thức thật
# của từng món — dinh dưỡng trả về chỉ nên coi là ước lượng thô.
EDAMAM_QUERY = {
    # "vietnamese sandwich" và "banh mi" đều tra hụt; "baguette sandwich" là chuỗi
    # gần nhất mà Edamam nhận diện được.
    "banh mi": "baguette sandwich",
    "banh trang tron": "rice paper salad",
    "banh xeo": "vietnamese pancake",
    "bun bo hue": "spicy beef noodle soup",
    "bun dau": "rice noodles with tofu",
    "com tam": "broken rice with grilled pork",
    "goi cuon": "fresh spring roll",
    "pho": "beef noodle soup",
    "hu tieu": "pork noodle soup",
    "xoi": "sticky rice",
}


def canonical(raw_name: str) -> str:
    """Tên lớp thô của một mô hình -> tên chung (chữ thường), dùng làm khoá."""
    alias = ALIASES.get(raw_name)
    if alias:
        return alias
    name = _LOCAL_NAME_SUFFIX.sub("", raw_name)
    name = name.replace("_", " ").replace("-", " ")
    name = re.sub(r"\s+", " ", name).strip().lower()
    return name or raw_name.strip().lower()


def display(canonical_name: str) -> str:
    """Tên chung -> dạng để hiển thị trên app."""
    return DISPLAY_OVERRIDES.get(canonical_name) or canonical_name.title()


def edamam_query(canonical_name: str) -> str:
    """Tên chung -> chuỗi tiếng Anh để tra dinh dưỡng Edamam."""
    return EDAMAM_QUERY.get(canonical_name, canonical_name)
