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
    "note": "Đất ngõ ô tô Cầu Giấy — khu vực đại học, dân trí cao",
    "city": "hanoi", "modelType": "land",
    "district": "Cầu Giấy", "ward": "Dịch Vọng Hậu",
    "area": 55.0, "propertyType": "Đất thổ cư",
    "street": "Nguyễn Khang",
    "description": (
      "Đất thổ cư phường Dịch Vọng Hậu, ngõ ô tô vào nhà. "
      "Diện tích 55m2, vuông vắn, sổ hồng chính chủ. "
      "Gần Keangnam, ĐHQG Hà Nội, siêu thị Big C. "
      "Không quy hoạch, đường trước nhà 4m, khu dân cư văn minh."
    ),
    "expected_range": (5_500_000_000, 9_500_000_000),
  },

  {
    "id": "HAN-L-03",
    "note": "Đất phân lô Hà Đông — khu đô thị mới phát triển",
    "city": "hanoi", "modelType": "land",
    "district": "Hà Đông", "ward": "Phú Lương",
    "area": 75.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất phân lô khu đô thị Phú Lương, Hà Đông. "
      "Diện tích 75m2, lô đẹp vuông vắn, mặt tiền 5m. "
      "Đường trước nhà 7m, ô tô tránh nhau. "
      "Sổ hồng từng lô, không quy hoạch, gần Aeon Mall Hà Đông."
    ),
    "expected_range": (3_000_000_000, 5_500_000_000),
  },

  {
    "id": "HAN-NL-01",
    "note": "Chung cư Vinhomes Smart City Tây Mỗ — dự án lớn tiện ích cao",
    "city": "hanoi", "modelType": "non_land",
    "district": "Nam Từ Liêm", "ward": "Tây Mỗ",
    "area": 68.0, "propertyType": "Chung cư / Căn hộ",
    "bedrooms": 2, "bathrooms": 2,
    "street": "Đại Lộ Thăng Long",
    "description": (
      "Căn hộ Vinhomes Smart City, tòa S1.02, tầng 15. "
      "Diện tích 68m2, 2 phòng ngủ 2 vệ sinh. "
      "Full nội thất cao cấp, ban công rộng view thoáng. "
      "Có thang máy, hồ bơi, gym, an ninh 24/7. "
      "Sổ hồng chính chủ, gần trường học quốc tế."
    ),
    "expected_range": (3_200_000_000, 5_500_000_000),
  },

  {
    "id": "HAN-NL-02",
    "note": "Nhà phố Thanh Xuân — 4 tầng kinh doanh, ngõ ô tô",
    "city": "hanoi", "modelType": "non_land",
    "district": "Thanh Xuân", "ward": "Nhân Chính",
    "area": 38.0, "propertyType": "Nhà phố",
    "bedrooms": 4, "bathrooms": 3,
    "street": "Lê Văn Lương",
    "description": (
      "Nhà phố 4 tầng Nhân Chính, Thanh Xuân. "
      "Diện tích 38m2 x 4 tầng, mặt tiền 4m. "
      "Ngõ ô tô vào thoải mái, kinh doanh cho thuê tốt. "
      "Nội thất đầy đủ, thang máy, sổ hồng chính chủ. "
      "Gần Royal City, Times City, dòng tiền ổn định."
    ),
    "expected_range": (5_500_000_000, 9_000_000_000),
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
    "note": "Đất hẻm xe hơi Gò Vấp — khu dân cư đông đúc",
    "city": "hcm", "modelType": "land",
    "district": "Gò Vấp", "ward": "Phường 12",
    "area": 90.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư hẻm xe hơi Gò Vấp, diện tích 90m2. "
      "Hẻm ô tô vào thoải mái, khu dân cư an ninh. "
      "Sổ hồng chính chủ, không dính quy hoạch. "
      "Gần chợ Gò Vấp, bệnh viện, trường học đầy đủ."
    ),
    "expected_range": (5_000_000_000, 9_000_000_000),
  },

  {
    "id": "HCM-L-03",
    "note": "Đất Thủ Đức gần ĐHQG — tiềm năng cho thuê cao",
    "city": "hcm", "modelType": "land",
    "district": "Thủ Đức", "ward": "Linh Trung",
    "area": 100.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư Linh Trung Thủ Đức, gần ĐHQG TP.HCM. "
      "Diện tích 100m2, hẻm xe hơi vào nhà. "
      "Khu dân cư văn minh, sổ hồng chính chủ. "
      "Tiềm năng kinh doanh cho thuê sinh viên cao, gần siêu thị, chợ."
    ),
    "expected_range": (4_000_000_000, 8_000_000_000),
  },

  {
    "id": "HCM-NL-01",
    "note": "Căn hộ Masteri An Phú Quận 2 — chung cư cao cấp ven sông",
    "city": "hcm", "modelType": "non_land",
    "district": "Thủ Đức", "ward": "An Phú",
    "area": 70.0, "propertyType": "Chung cư / Căn hộ",
    "bedrooms": 2, "bathrooms": 2,
    "street": "Xa Lộ Hà Nội",
    "description": (
      "Căn hộ Masteri An Phú, tầng 20, 70m2. "
      "2 phòng ngủ 2 vệ sinh, full nội thất cao cấp. "
      "View sông Sài Gòn đẹp, căn góc 2 mặt thoáng. "
      "Chung cư cao cấp, có thang máy, hồ bơi, gym. "
      "Sổ hồng, gần Vincom Thảo Điền, gần trung tâm Q1."
    ),
    "expected_range": (4_500_000_000, 8_000_000_000),
  },

  {
    "id": "HCM-NL-02",
    "note": "Nhà phố Tân Bình — kinh doanh mặt tiền sầm uất",
    "city": "hcm", "modelType": "non_land",
    "district": "Tân Bình", "ward": "Phường 2",
    "area": 50.0, "propertyType": "Nhà phố",
    "bedrooms": 3, "bathrooms": 2,
    "street": "Hoàng Văn Thụ",
    "description": (
      "Nhà phố mặt tiền Hoàng Văn Thụ, Tân Bình. "
      "Diện tích 50m2, 3 tầng, mặt tiền 4m. "
      "Kinh doanh cafe, văn phòng cho thuê dòng tiền tốt. "
      "Gần sân bay Tân Sơn Nhất, khu dân cư sầm uất. "
      "Nội thất đầy đủ, sổ hồng chính chủ, ô tô đỗ cửa."
    ),
    "expected_range": (7_000_000_000, 14_000_000_000),
  },

  # ══════════════════════════════════════════════════════════════════
  # ĐÀ NẴNG — 5 cases
  # Nguồn: batdongsan.com.vn, muanhadat.vn tháng 3-4/2024
  # ══════════════════════════════════════════════════════════════════

  {
    "id": "DAN-L-01",
    "note": "Đất biển Ngũ Hành Sơn — mặt tiền đường biển Trường Sa",
    "city": "danang", "modelType": "land",
    "district": "Ngũ Hành Sơn", "ward": "Mỹ An",
    "area": 105.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất mặt tiền đường Trường Sa, Mỹ An, Ngũ Hành Sơn. "
      "Diện tích 105m2, mặt tiền 7m, sổ đỏ chính chủ. "
      "View biển Mỹ Khê tuyệt đẹp, cách biển 80m đi bộ ra biển. "
      "Kinh doanh homestay resort tốt, ô tô vào thoải mái. "
      "Pháp lý hoàn công, không quy hoạch."
    ),
    "expected_range": (8_000_000_000, 18_000_000_000),
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
    "district": "Sơn Trà", "ward": "An Hải Bắc",
    "area": 90.0, "propertyType": "Nhà phố",
    "bedrooms": 4, "bathrooms": 3,
    "description": (
      "Nhà phố mặt tiền đường Võ Nguyên Giáp, Sơn Trà Đà Nẵng. "
      "Diện tích 90m2, 5 tầng, mặt tiền 5m. "
      "Gần biển Mỹ Khê 100m, view biển đẹp. "
      "Kinh doanh khách sạn mini, đang cho thuê 40tr/tháng. "
      "Sổ đỏ, pháp lý hoàn công, ô tô vào thoải mái."
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
    "note": "Đất ngõ ô tô Ngô Quyền — khu dân cư đông, giá hợp lý",
    "city": "haiphong", "modelType": "land",
    "district": "Ngô Quyền", "ward": "Máy Chai",
    "area": 72.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất thổ cư ngõ ô tô vào, Máy Chai, Ngô Quyền. "
      "Diện tích 72m2, vuông vắn, sổ hồng chính chủ. "
      "Ngõ thông thoáng ô tô vào thoải mái, khu dân cư văn minh. "
      "Gần chợ Máy Chai, bệnh viện Việt Tiệp, trường học."
    ),
    "expected_range": (2_200_000_000, 4_500_000_000),
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
    "district": "Phú Xuân", "ward": "An Cựu",
    "area": 85.0, "propertyType": "Đất thổ cư",
    "description": (
      "Đất mặt đường An Dương Vương, An Cựu, TP Huế. "
      "Diện tích 85m2, mặt tiền 5m, sổ hồng chính chủ. "
      "Đường rộng ô tô tránh nhau, kinh doanh tốt. "
      "Gần trung tâm Huế, không quy hoạch, pháp lý rõ ràng."
    ),
    "expected_range": (2_500_000_000, 5_500_000_000),
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