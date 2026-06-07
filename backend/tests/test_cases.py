"""
tests/test_cases.py
────────────────────
35 test cases thực tế — 5 per city.
Dữ liệu tham khảo từ batdongsan.com.vn, nhatot.com, alonhadat.com.vn
(Q1-Q2 2024). expected_range là khoảng thực tế thị trường, không phải
expected output của model.

Chạy:
  python tests/test_cases.py                     # localhost:8000
  python tests/test_cases.py http://IP:8000
"""

import json, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

TEST_CASES = [

  # ══════════════════════════════════════════════════════════════════
  # HÀ NỘI — 5 cases
  # Nguồn: batdongsan.com.vn tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "HAN-L-01",
    "note": "Đất mặt phố Hoàn Kiếm — mặt tiền kinh doanh trung tâm phố cổ",
    "city": "hanoi", "modelType": "land",
    "district": "Hoàn Kiếm", "ward": "Hàng Đào",
    "area": 42.0, "propertyType": "Đất thổ cư",
    "street": "Hàng Đào",
    "description": (
      "Đất mặt phố Hàng Đào, trung tâm phố cổ Hoàn Kiếm. "
      "Mặt tiền 4.5m, sổ hồng chính chủ, không quy hoạch. "
      "Vị trí kinh doanh đắc địa, ô tô tránh nhau thoải mái, "
      "gần hồ Hoàn Kiếm 200m. Nở hậu 5.2m."
    ),
    "expected_range": (12_000_000_000, 30_000_000_000),
  },

  {
    "id": "HAN-L-02",
    "note": "Phố Linh Đường Hoàng Liệt Chính Chủ Bán Mảnh Đất",
    "city": "hanoi", "modelType": "land",
    "district": "Hoàng Mai", "ward": "Hoàng Liệt",
    "area": 50.0, "propertyType": "Đất thổ cư",
    "street": "Linh Đường",
    "description": (
      "Phố Linh Đường - Hoàng Liệt Sát Hồ Linh Đàm: Chính Chủ Bá,n Mảnh Đất 50m - MT4m Ô Tô Dừng Đỗ Ngõ Thông Kinh Doanh "
      "Sổ vuông vắn , chủ rất cần bán gấp trong tháng. "
      "Mảnh Đất Lô Góc Hiếm Giá khu Vực ACE Nhanh Chân."
      "Chỉ 200m ra QL1A mở rộng đường 90m tiềm năng tăng giá mạnh"
    ),
    "expected_range": (7_200_000_000, 10_800_000_000),
  },

  {
    "id": "HAN-L-03",
    "note": "Hiếm! Bán đất Hồ Tùng Mậu - Mai Dịch - Cầu Giấy - 42m2 - Vuông vắn - đầu tư đỉnh",
    "city": "hanoi", "modelType": "land",
    "district": "Cầu Giấy", "ward": "Mai Dịch",
    "area": 42.0, "propertyType": "Đất thổ cư",
    "street": "Hồ Tùng Mậu",
    "description": (
      "Mảnh đất rất phù hợp cho khách mua giữ tiền, xây ở, xây CHDV. Hộ khẩu quận Cầu Giấy. Gần ngay các trường Đại Học lớn, nếu xây cho thuê luôn kín phòng. "
      "Đất sạch không có tranh chấp, quy hoạch. "
      "Hiện trạng là đất trống đã xây tường bao quanh, 2 bên nhà đã xây nhà 5 tầng kiên cố."
      "Sổ đỏ chính chủ vuông đẹp sẵn sàng giao dịch cho khách mua."
    ),
    "expected_range": (7_300_000_000, 10_900_000_000),
  },

  {
    "id": "HAN-NL-01",
    "note": "Chung cư The Price La Khê — dự án lớn tiện ích cao",
    "city": "hanoi", "modelType": "non_land",
    "district": "Hà Đông", "ward": "La Khê",
    "area": 103, "propertyType": "Chung cư / Căn hộ",
    "bedrooms": 3, "bathrooms": 3,
    "street": "Tố Hữu",
    "description": (
      "Căn hộ The Price, tòa S1.02, tầng 22. "
      "Diện tích 103m2, 3 phòng ngủ, 3 vệ sinh, đầy đủ nội thất. "
      "Ban công rộng view thoáng, nhiều tiện ích, gần trung tâm quận. "
      "Có thang máy, hồ bơi, gym, an ninh 24/7. "
      "Sổ hồng chính chủ, gần trường học quốc tế."
    ),
    "expected_range": (5_200_000_000, 7_400_000_000),
  },

  {
    "id": "HAN-NL-02",
    "note": "Chính chủ bán căn hộ lô góc 60.5m² 3PN - 2WC - sổ đỏ lâu dài",
    "city": "hanoi", "modelType": "non_land",
    "district": "Long Biên", "ward": "Giang Biên",
    "area": 60.0, "propertyType": "Căn hộ chung cư",
    "bedrooms": 3, "bathrooms": 2,
    "street": "Phúc Lợi",
    "description": (
      "Chính chủ bán căn hộ lô góc 60.5m² 3PN - 2WC - sổ đỏ lâu dài. "
      "Thiết kế: 3 phòng ngủ 2 vệ sinh, không gian thoáng sáng, vuông vắn. "
      "Nội thất đầy đủ: Sofa, bàn ăn, giường tủ quần áo..."
    ),
    "expected_range": (3_000_000_000, 4_400_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # HỒ CHÍ MINH — 5 cases
  # Nguồn: batdongsan.com.vn, nhatot.com tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "HCM-L-01",
    "note": "Đất mặt tiền Bình Thạnh — gần trung tâm, sổ hồng",
    "city": "hcm", "modelType": "land",
    "district": "Bình Thạnh", "ward": "Phường 26",
    "area": 80.0, "propertyType": "Đất thổ cư",
    "street": "Đinh Bộ Lĩnh",
    "description": (
      "Đất mặt tiền đường Đinh Bộ Lĩnh, Bình Thạnh. "
      "Diện tích 80m2, mặt tiền 5m, sổ hồng chính chủ. "
      "Gần cầu Sài Gòn, gần trung tâm quận 1 chỉ 3km. "
      "Kinh doanh tốt, ô tô tránh nhau, khu dân cư sầm uất."
    ),
    "expected_range": (8_000_000_000, 16_000_000_000),
  },

  {
    "id": "HCM-L-02",
    "note": "Đất hẻm xe hơi Tân Bình — khu dân cư đông đúc",
    "city": "hcm", "modelType": "land",
    "district": "Tân Bình", "ward": "Phường 5",
    "area": 46.0, "propertyType": "Đất thổ cư",
    "street": "Phạm Văn Hai",
    "description": (
      "Gần chợ Phạm Văn Hai, Bảy Hiền, thuận tiện di chuyển Tân Phú Phú Nhuận Quận 10 "
      "Hẻm ô tô vào thoải mái, khu dân cư an ninh. "
      "Mặt tiền rộng 4m."
      "Sổ hồng chính chủ, không dính quy hoạch. "
      "Khu vực hiếm nhà bán, phù hợp xây ở hoặc đầu tư giữ tài sản"
    ),
    "expected_range": (4_200_000_000, 6_200_000_000),
  },

  {
    "id": "HCM-NL-03",
    "note": "Đất Thủ Đức gần ĐHQG — tiềm năng cho thuê cao",
    "city": "hcm", "modelType": "non_land",
    "district": "Bình Thạnh", "ward": "Phường 13",
    "area": 41.0, "propertyType": "Căn hộ chung cư",
    "street": "Đặng Thùy Trâm",
    "description": (
      "Pháp lý : sổ hồng riêng."
      "Tiện ích: Giao thông thuận lợi qua các trục đường lớn: Nguyễn Văn Đậu, Phan Đăng Lưu, Nơ Trang Long, Bùi Hữu Nghĩa, chỉ 5 phút đến trung tâm Quận 1."
      "Gần chợ Bà Chiểu, Coopmart Đinh Tiên Hoàng, Đại học Hutech, Đại học Ngoại thương, Bệnh viện Gia Định."
      "Khu vực dân cư văn minh, an ninh tốt, gần chợ, trường học, gần khu trung tâm."
    ),
    "expected_range": (2_100_000_000, 3_200_000_000),
  },

  {
    "id": "HCM-NL-01",
    "note": "Bán nhà giá ngợp Ngô Tất Tố, Bình Thạnh. Nhà có sẵn HĐ thuê 18 triệu/tháng, sổ riêng",
    "city": "hcm", "modelType": "non_land",
    "district": "Bình Thạnh", "ward": "Phường 19",
    "area": 70.0, "propertyType": "Nhà phố",
    "bedrooms": 2, "bathrooms": 1,
    "street": "Ngô Tất Tố",
    "description": (
      "Vị trí trung tâm Bình Thạnh, khu dân cư sầm uất, thuận tiện di chuyển nhanh sang Quận 1, Phú Nhuận, Thủ Đức và các quận trung tâm chỉ vài phút. "
      "Nhà mới đẹp, khai thác cho thuê ổn định với dòng tiền sẵn 18 triệu/tháng, phù hợp mua ở kết hợp đầu tư giữ tài sản lâu dài."
      "Khu vực hiếm nhà bán giá tốt, gần nhiều tiện ích lớn như Landmark 81, Vincom, trường học, bệnh viện, quán cafe và khu ăn uống nhộn nhịp. "
      "Sổ hồng rõ ràng."
    ),
    "expected_range": (2_200_000_000, 3_200_000_000),
  },

  {
    "id": "HCM-NL-02",
    "note": "Nhà ở vòng xoay Điện Biên Phủ",
    "city": "hcm", "modelType": "non_land",
    "district": "Quận 1", "ward": "Phường Đa Kao",
    "area": 55, "propertyType": "Nhà phố",
    "bedrooms": 3, "bathrooms": 4,
    "street": "Hoàng Văn Thụ",
    "description": (
      "Do gia đình chuyển nơi ở và cần xoay việc gấp, nên chúng tôi mong muốn bán lại căn nhà trong thời gian sớm thích hợp hộ gia đình sinh sống hoặc kinh doanh cho thuê ở ngay trên đường Mai Thị Lựu Phường Đakao quận 1 (cũ) nay thuộc phường Tân Định (mới) gần vòng xoay Điện Biên Phủ."
      "Diện tích: 5,45 x 10m (vuông vức 54,5m²)."
      "Vị trí: Thông ra Điện Biên Phủ, gần Cầu Bông, chợ Bà Chiểu."
      "Nhà hẻm 5m, khu dân cư an ninh, hàng xóm thân thiện."
      "Tiện ích xung quanh bán kính 1km: Trường học, chợ, bệnh viện, dân cư sầm uất, thuận tiện ở lâu dài hoặc cho thuê, di chuyển nhanh sang trung tâm Q3, Bình Thạnh, Phú Nhuận, 5phut di chuyển qua Nhà thờ Đức Bà, Phố Đi Bộ Nguyễn Huệ."
      "Sổ hồng riêng tên tôi - sang tên công chứng trong ngày."
    ),
    "expected_range": (2_700_000_000, 4_000_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # ĐÀ NẴNG — 5 cases
  # Nguồn: batdongsan.com.vn, muanhadat.vn tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "DAN-L-01",
    "note": "Đất biển Ngũ Hành Sơn — mặt tiền đường biển Trường Sa",
    "city": "danang", "modelType": "land",
    "district": "Cẩm Lệ", "ward": "Hòa An",
    "area": 94.0, "propertyType": "Đất thổ cư",
    "street": "Trường Chinh",
    "description": (
      "Hiếm có đất MT Trường Chinh, vị trí kinh doanh - 4tỷ350 gần bến xe Đà Nẵng."
      "Vị trí: Gần đầu đường trục chính kinh doanh, lưu lượng xe lớn. Giáp Thanh Khê, Liên Chiểu... Khu dân cư đông đúc. Phù hợp: Kinh doanh, xây ở, đầu tư giữ tiền lâu dài."
      "Diện tích: 94,4m² (5,84m nở hậu: 7,85m) Tài lộc. "
      "Đường: 5.5m lề 3m. "
      "Pháp lý hoàn công, không quy hoạch."
    ),
    "expected_range": (3_500_000_000, 5_200_000_000),
  },

  {
    "id": "DAN-L-02",
    "note": "Đất trung tâm Hải Châu — gần cầu Rồng, sổ đỏ",
    "city": "danang", "modelType": "land",
    "district": "Hải Châu", "ward": "Hải Châu 1",
    "area": 65.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất mặt tiền đường Trần Phú, trung tâm Hải Châu Đà Nẵng. "
      "Diện tích 65m2, sổ đỏ chính chủ, pháp lý hoàn công. "
      "Gần cầu Rồng, gần sông Hàn view sông đẹp. "
      "Ô tô vào được, kinh doanh khách sạn mini tốt."
    ),
    "expected_range": (5_000_000_000, 11_000_000_000),
  },

  {
    "id": "DAN-L-03",
    "note": "Đất kiệt Thanh Khê — dân cư ổn định, giá vừa phải",
    "city": "danang", "modelType": "land",
    "district": "Thanh Khê", "ward": "Tam Thuận",
    "area": 80.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất trong kiệt ô tô Tam Thuận, Thanh Khê. "
      "Diện tích 80m2, sổ đỏ, pháp lý rõ ràng. "
      "Kiệt ô tô vào nhà, khu dân cư ổn định. "
      "Gần chợ Tam Thuận, gần trường THCS. Nhà mới xây."
    ),
    "expected_range": (2_800_000_000, 5_500_000_000),
  },

  {
    "id": "DAN-NL-01",
    "note": "Nhà phố mặt tiền Sơn Trà — kinh doanh gần biển Mỹ Khê",
    "city": "danang", "modelType": "non_land",
    "district": "Ngũ Hành Sơn", "ward": "Hòa Quý",
    "area": 63.0, "propertyType": "Căn hộ chung cư",
    "street": "Nguyễn Phước Lan",
    "bedrooms": 2, "bathrooms": 1,
    "description": (
      "Vị trí đắc địa,gần trung tâm, phù hợp kinh doanh take a way."
      "Tiện ích đầy đủ từ hồ bơi, sân bóng, vườn trên sân thượng, khu vui chơi, phòng gym, yoga."
      "An ninh tốt, bảo vệ 24/24"
      "Phù hợp khách thích sống riêng tư, thoáng, có thêm không gian thư giãn."
    ),
    "expected_range": (9_000_000_000, 18_000_000_000),
  },

  {
    "id": "DAN-NL-02",
    "note": "Căn hộ Monarchy sông Hàn — cao cấp trung tâm",
    "city": "danang", "modelType": "non_land",
    "district": "Hải Châu", "ward": "Bình Hiên",
    "area": 75.0, "propertyType": "Chung cư / Căn hộ",
    "bedrooms": 2, "bathrooms": 2,
    "description": (
      "Căn hộ Monarchy Đà Nẵng, tầng 18. "
      "Diện tích 75m2, 2 phòng ngủ 2 vệ sinh. "
      "View sông Hàn đẹp, full nội thất cao cấp. "
      "Có thang máy, hồ bơi, gym. "
      "Sổ đỏ, pháp lý đầy đủ, gần chợ Cồn, gần trung tâm."
    ),
    "expected_range": (3_500_000_000, 6_500_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # HẢI PHÒNG — 5 cases
  # Nguồn: batdongsan.com.vn, nhadat24h.net tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "HPG-L-01",
    "note": "Đất mặt đường Lê Chân — trung tâm Hải Phòng, kinh doanh",
    "city": "haiphong", "modelType": "land",
    "district": "Lê Chân", "ward": "Dư Hàng",
    "area": 60.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất mặt đường Lê Duẩn, quận Lê Chân, Hải Phòng. "
      "Diện tích 60m2, mặt tiền 4m, sổ hồng chính chủ. "
      "Đường rộng ô tô tránh nhau, kinh doanh sầm uất. "
      "Gần trung tâm thương mại Vincom Imperia, không quy hoạch."
    ),
    "expected_range": (3_500_000_000, 8_000_000_000),
  },

  {
    "id": "HPG-L-02",
    "note": "Bán đất tại phường Anh Dũng, quận Dương Kinh, Hải Phòng, giá siêu hời",
    "city": "haiphong", "modelType": "land",
    "district": "Dương Kinh", "ward": "Anh Dũng",
    "area": 50.0, "propertyType": "Đất thổ cư",
    "description": (
      "Siêu phẩm ngõ 3m gần chợ Phấn Dũng - Anh Dũng - Hàng Hiếm. "
      "Diện tích 50.4m² - mặt tiền ngang 4m, hẻm ô tô vào 7m, hướng Nam mát mẻ. "
      "Xung quanh tiện ích đầy đủ dân cư đông đúc, gần chợ, trường học các cấp. Chỉ vài phút là đến Trung Tâm Thành Phố. "
      "Sổ hồng chính chủ, không quy hoạch, không lỗi phong thuỷ."
    ),
    "expected_range": (1_120_000_000, 1_680_000_000),
  },

  {
    "id": "HPG-L-03",
    "note": "Đất Hải An gần khu công nghiệp Đình Vũ",
    "city": "haiphong", "modelType": "land",
    "district": "Hải An", "ward": "Đằng Hải",
    "area": 120.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư Đằng Hải, Hải An, Hải Phòng. "
      "Diện tích 120m2, đường 7m ô tô tránh nhau. "
      "Sổ hồng chính chủ, gần KCN Đình Vũ, cảng Hải Phòng. "
      "Khu công nhân thuê đông, tiềm năng kinh doanh nhà trọ."
    ),
    "expected_range": (1_800_000_000, 4_000_000_000),
  },

  {
    "id": "HPG-NL-01",
    "note": "Nhà 4 tầng Hồng Bàng — trung tâm, mặt phố kinh doanh",
    "city": "haiphong", "modelType": "non_land",
    "district": "Hồng Bàng", "ward": "Phan Bội Châu",
    "area": 55.0, "propertyType": "Nhà phố",
    "bedrooms": 4, "bathrooms": 3,
    "description": (
      "Nhà phố 4 tầng mặt phố Điện Biên Phủ, Hồng Bàng. "
      "Diện tích 55m2, mặt tiền 4.5m. "
      "Kinh doanh café, văn phòng cho thuê dòng tiền ổn định. "
      "Nội thất đầy đủ, thang máy, sổ hồng chính chủ. "
      "Gần Tòa án, trung tâm hành chính Hải Phòng."
    ),
    "expected_range": (4_000_000_000, 8_000_000_000),
  },

  {
    "id": "HPG-NL-02",
    "note": "Chung cư Hoàng Huy Commerce Lê Chân",
    "city": "haiphong", "modelType": "non_land",
    "district": "Lê Chân", "ward": "Dư Hàng Kênh",
    "area": 65.0, "propertyType": "Chung cư / Căn hộ",
    "bedrooms": 2, "bathrooms": 2,
    "description": (
      "Căn hộ Hoàng Huy Commerce, tầng 12. "
      "Diện tích 65m2, 2 phòng ngủ 2 vệ sinh. "
      "Đầy đủ nội thất, ban công rộng view đẹp. "
      "Có thang máy, bảo vệ 24/7, sổ hồng chính chủ. "
      "Gần trường học, siêu thị, bệnh viện tiện lợi."
    ),
    "expected_range": (1_500_000_000, 3_000_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # HUẾ — 5 cases
  # Nguồn: batdongsan.com.vn, alonhadat.com.vn tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "HUE-L-01",
    "note": "Đất mặt đường An Dương Vương — TP Huế, kinh doanh",
    "city": "hue", "modelType": "land",
    "district": "Phú Xuân", "ward": "Hương An",
    "area": 100.0, "propertyType": "Đất thổ cư",
    "description": (
      "Vị trí gần chùa Thiên Mụ khu vực du lịch, nghỉ dưỡng cực đẹp. "
      "Hẻm ô tô vào tránh nhau rộng rãi, di chuyển thuận tiện "
      "Mặt tiền rộng 4m, sổ hồng chính chủ. "
      "Cạnh view sông thoáng mát quanh năm, không khí trong lành"
    ),
    "expected_range": (700_000_000, 1_000_000_000),
  },

  {
    "id": "HUE-L-02",
    "note": "Đất ven sông Hương Vỹ Dạ — view sông, ở đẹp",
    "city": "hue", "modelType": "land",
    "district": "Phú Xuân", "ward": "Vỹ Dạ",
    "area": 120.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất ven sông Hương, phường Vỹ Dạ, TP Huế. "
      "Diện tích 120m2, hướng đông nam view sông đẹp. "
      "Sổ hồng, không quy hoạch, ô tô vào thoải mái. "
      "Khu dân cư yên tĩnh, gần cầu Phú Lưu, gần trung tâm."
    ),
    "expected_range": (2_000_000_000, 4_500_000_000),
  },

  {
    "id": "HUE-L-03",
    "note": "Đất Hương Thủy gần KCN Phú Bài — công nhân đông",
    "city": "hue", "modelType": "land",
    "district": "Hương Thủy", "ward": "Thủy Phương",
    "area": 130.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư Thủy Phương, Hương Thủy, Thừa Thiên Huế. "
      "Diện tích 130m2, đường 5m ô tô vào. "
      "Sổ hồng chính chủ, gần KCN Phú Bài 2km. "
      "Tiềm năng cho thuê nhà trọ, không quy hoạch."
    ),
    "expected_range": (1_200_000_000, 2_800_000_000),
  },

  {
    "id": "HUE-NL-01",
    "note": "Nhà phố An Cựu — TP Huế, kiệt ô tô, sổ hồng",
    "city": "hue", "modelType": "non_land",
    "district": "Phú Xuân", "ward": "An Cựu",
    "area": 70.0, "propertyType": "Nhà phố",
    "bedrooms": 3, "bathrooms": 2,
    "description": (
      "Nhà phố 3 tầng, kiệt ô tô An Cựu, TP Huế. "
      "Diện tích 70m2, 3 phòng ngủ 2 vệ sinh. "
      "Nội thất đầy đủ, nhà mới xây 2022. "
      "Kiệt ô tô vào nhà, sổ hồng chính chủ. "
      "Gần siêu thị Big C Huế, bệnh viện Trung Ương Huế."
    ),
    "expected_range": (1_800_000_000, 3_800_000_000),
  },

  {
    "id": "HUE-NL-02",
    "note": "Nhà 2 tầng Hương Trà — ngoại ô Huế, giá thấp",
    "city": "hue", "modelType": "non_land",
    "district": "Hương Trà", "ward": "Hương Chữ",
    "area": 55.0, "propertyType": "Nhà phố",
    "bedrooms": 2, "bathrooms": 1,
    "description": (
      "Nhà 2 tầng Hương Chữ, Hương Trà, Thừa Thiên Huế. "
      "Diện tích 55m2, 2 phòng ngủ 1 vệ sinh. "
      "Đường nhựa 5m ô tô vào được, sổ hồng. "
      "Nhà mới xây, gần UBND Hương Trà, chợ Hương Chữ."
    ),
    "expected_range": (900_000_000, 2_000_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # ĐỒNG NAI — 5 cases
  # Nguồn: batdongsan.com.vn, muabandongnai.com tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "DNI-L-01",
    "note": "Đất mặt tiền QL1A Biên Hòa — kinh doanh logistics",
    "city": "dongnai", "modelType": "land",
    "district": "Biên Hòa", "ward": "Trảng Dài",
    "area": 95.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất mặt tiền Quốc lộ 1A, Trảng Dài, Biên Hòa. "
      "Diện tích 95m2, mặt tiền 5m, sổ hồng chính chủ. "
      "Đường rộng 20m, xe tải ô tô vào được, kinh doanh tốt. "
      "Gần KCN Biên Hòa 2, không quy hoạch."
    ),
    "expected_range": (3_500_000_000, 7_500_000_000),
  },

  {
    "id": "DNI-L-02",
    "note": "Đất khu dân cư Long Bình — Biên Hòa, đường ô tô",
    "city": "dongnai", "modelType": "land",
    "district": "Biên Hòa", "ward": "Long Bình",
    "area": 110.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư khu dân cư Long Bình, Biên Hòa. "
      "Diện tích 110m2, đường 7m ô tô tránh nhau. "
      "Sổ hồng chính chủ, không quy hoạch. "
      "Gần UBND Long Bình, trường học, chợ, siêu thị."
    ),
    "expected_range": (2_500_000_000, 5_500_000_000),
  },

  {
    "id": "DNI-L-03",
    "note": "Đất Long Thành gần sân bay Long Thành — đầu tư tiềm năng",
    "city": "dongnai", "modelType": "land",
    "district": "Long Thành", "ward": "Long An",
    "area": 200.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư Long An, Long Thành, Đồng Nai. "
      "Diện tích 200m2, đường nhựa 6m ô tô vào. "
      "Sổ hồng riêng lô, gần sân bay quốc tế Long Thành 3km. "
      "Tiềm năng tăng giá cao, không quy hoạch, khu dân cư."
    ),
    "expected_range": (2_800_000_000, 6_000_000_000),
  },

  {
    "id": "DNI-NL-01",
    "note": "Nhà phố Biên Hòa — 4 tầng kinh doanh sầm uất",
    "city": "dongnai", "modelType": "non_land",
    "district": "Biên Hòa", "ward": "Tân Phong",
    "area": 75.0, "propertyType": "Nhà phố",
    "bedrooms": 4, "bathrooms": 3,
    "description": (
      "Nhà phố 4 tầng mặt tiền đường Đồng Khởi, Tân Phong, Biên Hòa. "
      "Diện tích 75m2, mặt tiền 5m. "
      "Kinh doanh tốt, cho thuê mặt bằng 25tr/tháng. "
      "Nội thất đầy đủ, sổ hồng chính chủ, ô tô đỗ cửa."
    ),
    "expected_range": (4_500_000_000, 9_000_000_000),
  },

  {
    "id": "DNI-NL-02",
    "note": "Nhà xây mới Nhơn Trạch — gần cảng, công nhân thuê",
    "city": "dongnai", "modelType": "non_land",
    "district": "Nhơn Trạch", "ward": "Long Tân",
    "area": 60.0, "propertyType": "Nhà phố",
    "bedrooms": 3, "bathrooms": 2,
    "description": (
      "Nhà mới xây 3 tầng, Long Tân, Nhơn Trạch, Đồng Nai. "
      "Diện tích 60m2, 3 phòng ngủ 2 vệ sinh. "
      "Đường nhựa 6m ô tô vào thoải mái, sổ hồng. "
      "Gần KCN Nhơn Trạch, cảng Phước An, cho thuê công nhân tốt."
    ),
    "expected_range": (1_800_000_000, 3_800_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # CẦN THƠ — 5 cases
  # Nguồn: batdongsan.com.vn, homedy.com tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "CTO-L-01",
    "note": "Đất mặt tiền Ninh Kiều — trung tâm Cần Thơ, siêu đắt",
    "city": "cantho", "modelType": "land",
    "district": "Ninh Kiều", "ward": "Tân An",
    "area": 65.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất mặt tiền đường Trần Hưng Đạo, Tân An, Ninh Kiều. "
      "Diện tích 65m2, mặt tiền 4.5m, sổ hồng chính chủ. "
      "Đường rộng ô tô tránh nhau, kinh doanh sầm uất. "
      "Gần Vincom Cần Thơ, bến Ninh Kiều, không quy hoạch."
    ),
    "expected_range": (4_500_000_000, 10_000_000_000),
  },

  {
    "id": "CTO-L-02",
    "note": "Đất hẻm xe hơi Bình Thủy — gần sân bay Cần Thơ",
    "city": "cantho", "modelType": "land",
    "district": "Bình Thủy", "ward": "Bình Thủy",
    "area": 100.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư hẻm xe hơi, Bình Thủy, Cần Thơ. "
      "Diện tích 100m2, hẻm ô tô vào nhà. "
      "Sổ hồng chính chủ, không quy hoạch. "
      "Gần sân bay quốc tế Cần Thơ 2km, khu dân cư an ninh."
    ),
    "expected_range": (2_000_000_000, 4_500_000_000),
  },

  {
    "id": "CTO-L-03",
    "note": "Đất Cái Răng — khu chợ nổi, tiềm năng du lịch",
    "city": "cantho", "modelType": "land",
    "district": "Cái Răng", "ward": "Lê Bình",
    "area": 90.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư Lê Bình, Cái Răng, Cần Thơ. "
      "Diện tích 90m2, đường 5m ô tô vào. "
      "Sổ hồng chính chủ, gần chợ nổi Cái Răng. "
      "Tiềm năng kinh doanh du lịch, homestay, không quy hoạch."
    ),
    "expected_range": (1_800_000_000, 4_000_000_000),
  },

  {
    "id": "CTO-NL-01",
    "note": "Nhà phố mặt tiền Ninh Kiều — kinh doanh sầm uất",
    "city": "cantho", "modelType": "non_land",
    "district": "Ninh Kiều", "ward": "An Khánh",
    "area": 70.0, "propertyType": "Nhà phố",
    "bedrooms": 3, "bathrooms": 2,
    "description": (
      "Nhà phố mặt tiền Nguyễn Trãi, An Khánh, Ninh Kiều. "
      "Diện tích 70m2, 3 tầng, mặt tiền 5m. "
      "Kinh doanh café, cho thuê văn phòng dòng tiền tốt. "
      "Nội thất đầy đủ, sổ hồng chính chủ, ô tô đỗ cửa. "
      "Gần siêu thị Go! Cần Thơ, bệnh viện Đa Khoa."
    ),
    "expected_range": (3_500_000_000, 7_000_000_000),
  },

  {
    "id": "CTO-NL-02",
    "note": "Nhà Ô Môn — ngoại ô Cần Thơ, giá bình dân",
    "city": "cantho", "modelType": "non_land",
    "district": "Ô Môn", "ward": "Phước Thới",
    "area": 55.0, "propertyType": "Nhà phố",
    "bedrooms": 2, "bathrooms": 1,
    "description": (
      "Nhà cấp 4 mới xây Phước Thới, Ô Môn, Cần Thơ. "
      "Diện tích 55m2, 2 phòng ngủ 1 vệ sinh. "
      "Đường nhựa 4m ô tô vào được, sổ hồng chính chủ. "
      "Gần trường tiểu học, chợ Phước Thới, yên tĩnh."
    ),
    "expected_range": (700_000_000, 1_600_000_000),
  },

]


def _fmt_vnd(v):
    if v >= 1e9:
        s = f"{v/1e9:.1f}".rstrip("0").rstrip(".")
        return f"{s} tỷ"
    return f"{v/1e6:.0f} triệu"


def run_tests_http(base_url="http://localhost:8000"):
    passed = failed = skipped = 0
    W = 70
    print(f"\n{'═'*W}")
    print(f"  PropVision Test Suite  —  {len(TEST_CASES)} cases / 7 thành phố")
    print(f"  Server: {base_url}")
    print(f"{'═'*W}\n")

    import urllib.request
    city_stats = {}
    for tc in TEST_CASES:
        city = tc["city"]
        payload = {k: v for k, v in tc.items()
                   if k not in ("id", "note", "expected_range")}
        body = json.dumps(payload).encode()
        try:
            t0  = time.perf_counter()
            req = urllib.request.Request(
                f"{base_url}/predict", data=body,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data     = json.loads(resp.read())
                ms       = (time.perf_counter() - t0) * 1000
                mid      = data.get("price_mid", 0)
                lo, hi   = tc["expected_range"]
                ok       = lo <= mid <= hi
                fb       = " [MOCK]" if data.get("is_fallback") else ""
                tag      = "✓ PASS" if ok else "△ OOR "
                if ok: passed += 1
                else:  failed += 1
                city_stats.setdefault(city, []).append(ok)
                print(f"  {tag}  {tc['id']:<12}  "
                      f"{data.get('price_range_label','?'):>22}  "
                      f"conf={data.get('confidence_label','?'):>4}  "
                      f"{ms:>5.0f}ms{fb}")
                print(f"         {tc['note']}")
                print()
        except Exception as e:
            skipped += 1
            city_stats.setdefault(city, []).append(None)
            print(f"  ✗ SKIP  {tc['id']:<12}  {str(e)[:55]}\n")

    print(f"{'─'*W}")
    city_map = {"hanoi":"Hà Nội","hcm":"TP.HCM","danang":"Đà Nẵng",
                "haiphong":"Hải Phòng","hue":"Huế","dongnai":"Đồng Nai","cantho":"Cần Thơ"}
    print("  Kết quả theo thành phố:")
    for c, results in city_stats.items():
        ok = sum(1 for r in results if r is True)
        bar = "█" * ok + "░" * (len(results)-ok)
        print(f"    {city_map.get(c,c):<12} {bar}  {ok}/{len(results)}")

    total = passed + failed + skipped
    print(f"\n  Tổng: {passed}/{total} pass | {failed} out-of-range | {skipped} skip")
    print(f"{'═'*W}\n")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_tests_http(url)





# fptRE-backend   | 2026-05-28 10:01:07 [INFO] app.services.predictor — [Predictor] city=cantho model=non_land area=55.0m² district=Ô Môn ward=Phước Thới
# fptRE-frontend  | 2026/05/28 10:02:07 [error] 32#32: *1 upstream timed out (110: Operation timed out) while reading response header from upstream, client: 172.19.0.1, server: _, request: "POST /api/predict HTTP/1.1", upstream: "http://172.19.0.2:8000/predict", host: "localhost:3000", referrer: "http://localhost:3000/"
# fptRE-frontend  | 172.19.0.1 - - [28/May/2026:10:02:07 +0000] "POST /api/predict HTTP/1.1" 504 569 "http://localhost:3000/" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36" "-"