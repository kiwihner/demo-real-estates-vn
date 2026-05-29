/**
 * locationData.js
 * ────────────────
 * Danh sách 7 thành phố, quận/huyện, phường/xã
 * Dùng cho dropdown menu trong ValuationForm
 */

export const LOCATION_DATA = {
  hanoi: {
    label: "Tp. Hà Nội",
    hasStreet: true,
    districts: {

      // ───────────────── QUẬN ─────────────────

      "Ba Đình": [
        "Cống Vị","Điện Biên","Đội Cấn","Giảng Võ","Kim Mã",
        "Liễu Giai","Ngọc Hà","Ngọc Khánh","Nguyễn Trung Trực",
        "Phúc Xá","Quán Thánh","Thành Công","Trúc Bạch","Vĩnh Phúc"
      ],

      "Hoàn Kiếm": [
        "Chương Dương","Cửa Đông","Cửa Nam","Đồng Xuân",
        "Hàng Bạc","Hàng Bài","Hàng Bồ","Hàng Buồm","Hàng Đào",
        "Hàng Gai","Hàng Mã","Hàng Trống","Lý Thái Tổ",
        "Phan Chu Trinh","Phúc Tân","Trần Hưng Đạo","Tràng Tiền"
      ],

      "Tây Hồ": [
        "Bưởi","Nhật Tân","Phú Thượng","Quảng An",
        "Thụy Khuê","Tứ Liên","Xuân La","Yên Phụ"
      ],

      "Long Biên": [
        "Bồ Đề","Cự Khối","Đức Giang","Gia Thụy","Giang Biên",
        "Long Biên","Ngọc Lâm","Ngọc Thụy","Phúc Đồng",
        "Phúc Lợi","Sài Đồng","Thạch Bàn","Thượng Thanh","Việt Hưng"
      ],

      "Cầu Giấy": [
        "Dịch Vọng","Dịch Vọng Hậu","Mai Dịch",
        "Nghĩa Đô","Nghĩa Tân","Quan Hoa",
        "Trung Hòa","Yên Hòa"
      ],

      "Đống Đa": [
        "Cát Linh","Hàng Bột","Khâm Thiên","Khương Thượng",
        "Kim Liên","Láng Hạ","Láng Thượng","Nam Đồng",
        "Ngã Tư Sở","Ô Chợ Dừa","Phương Liên",
        "Phương Mai","Quang Trung","Quốc Tử Giám",
        "Thịnh Quang","Trung Liệt","Trung Phụng",
        "Trung Tự","Văn Chương","Văn Miếu"
      ],

      "Hai Bà Trưng": [
        "Bách Khoa","Bạch Đằng","Bạch Mai","Bùi Thị Xuân",
        "Cầu Dền","Đồng Nhân","Đồng Tâm","Lê Đại Hành",
        "Minh Khai","Ngô Thì Nhậm","Nguyễn Du",
        "Phạm Đình Hổ","Phố Huế","Quỳnh Lôi","Quỳnh Mai",
        "Thanh Lương","Thanh Nhàn","Trương Định","Vĩnh Tuy"
      ],

      "Hoàng Mai": [
        "Đại Kim","Định Công","Giáp Bát","Hoàng Liệt",
        "Hoàng Văn Thụ","Lĩnh Nam","Mai Động","Tân Mai",
        "Thanh Trì","Thịnh Liệt","Trần Phú","Tương Mai",
        "Vĩnh Hưng","Yên Sở"
      ],

      "Thanh Xuân": [
        "Hạ Đình","Khương Đình","Khương Mai","Khương Trung",
        "Kim Giang","Nhân Chính","Phương Liệt",
        "Thanh Xuân Bắc","Thanh Xuân Nam",
        "Thanh Xuân Trung","Thượng Đình"
      ],

      "Nam Từ Liêm": [
        "Cầu Diễn","Đại Mỗ","Mễ Trì","Mỹ Đình 1",
        "Mỹ Đình 2","Phú Đô","Phương Canh",
        "Tây Mỗ","Trung Văn","Xuân Phương"
      ],

      "Bắc Từ Liêm": [
        "Cổ Nhuế 1","Cổ Nhuế 2","Đức Thắng","Đông Ngạc",
        "Liên Mạc","Minh Khai","Phú Diễn","Phúc Diễn",
        "Tây Tựu","Thượng Cát","Thụy Phương",
        "Xuân Đỉnh","Xuân Tảo"
      ],

      "Hà Đông": [
        "Biên Giang","Đồng Mai","Dương Nội","Hà Cầu",
        "Kiến Hưng","La Khê","Mộ Lao","Nguyễn Trãi",
        "Phú La","Phú Lãm","Phú Lương","Phúc La",
        "Quang Trung","Vạn Phúc","Văn Quán",
        "Yên Nghĩa","Yết Kiêu"
      ],

      // ───────────────── THỊ XÃ ─────────────────

      "Sơn Tây": [
        "Lê Lợi","Ngô Quyền","Phú Thịnh","Quang Trung",
        "Sơn Lộc","Trung Hưng","Trung Sơn Trầm","Viên Sơn",
        "Xuân Khanh","Cổ Đông","Đường Lâm","Kim Sơn",
        "Sơn Đông","Thanh Mỹ","Xuân Sơn"
      ],

      // ───────────────── HUYỆN ─────────────────

      "Ba Vì": [
        "Tây Đằng","Ba Trại","Ba Vì","Cam Thượng","Cẩm Lĩnh",
        "Chu Minh","Cổ Đô","Đông Quang","Đồng Thái","Khánh Thượng",
        "Minh Châu","Minh Quang","Phong Vân","Phú Châu","Phú Cường",
        "Phú Đông","Phú Phương","Phú Sơn","Sơn Đà","Tản Hồng",
        "Tản Lĩnh","Thái Hòa","Thuần Mỹ","Thụy An","Tiên Phong",
        "Tòng Bạt","Vạn Thắng","Vân Hòa","Vật Lại","Yên Bài"
      ],

      "Chương Mỹ": [
        "Chúc Sơn","Xuân Mai","Đại Yên","Đông Phương Yên",
        "Đông Sơn","Đồng Lạc","Hoàng Diệu","Hoàng Văn Thụ",
        "Hòa Chính","Hợp Đồng","Hữu Văn","Lam Điền",
        "Mỹ Lương","Nam Phương Tiến","Ngọc Hòa","Phú Nam An",
        "Phú Nghĩa","Phụng Châu","Quảng Bị","Tân Tiến",
        "Thủy Xuân Tiên","Thượng Vực","Tiên Phương",
        "Tốt Động","Thanh Bình","Trần Phú","Trung Hòa",
        "Trường Yên","Văn Võ"
      ],

      "Đan Phượng": [
        "Phùng","Đan Phượng","Đồng Tháp","Hạ Mỗ","Hồng Hà",
        "Liên Hà","Liên Hồng","Liên Trung","Song Phượng",
        "Tân Hội","Tân Lập","Thọ An","Thọ Xuân","Thượng Mỗ",
        "Trung Châu"
      ],

      "Đông Anh": [
        "Đông Anh","Bắc Hồng","Cổ Loa","Dục Tú","Đại Mạch",
        "Hải Bối","Kim Chung","Kim Nỗ","Liên Hà","Mai Lâm",
        "Nam Hồng","Nguyên Khê","Tàm Xá","Thụy Lâm","Tiên Dương",
        "Uy Nỗ","Vân Hà","Vân Nội","Việt Hùng","Vĩnh Ngọc",
        "Võng La","Xuân Canh","Xuân Nộn"
      ],

      "Gia Lâm": [
        "Trâu Quỳ","Yên Viên","Bát Tràng","Cổ Bi","Dương Hà",
        "Dương Quang","Đa Tốn","Đặng Xá","Đình Xuyên","Đông Dư",
        "Kim Lan","Kiêu Kỵ","Lệ Chi","Ninh Hiệp","Phù Đổng",
        "Phú Thị","Trung Mầu","Văn Đức","Yên Thường","Yên Viên"
      ],

      "Hoài Đức": [
        "Trạm Trôi","An Khánh","An Thượng","Cát Quế","Đắc Sở",
        "Di Trạch","Đông La","Đức Giang","Đức Thượng","Dương Liễu",
        "Kim Chung","La Phù","Lại Yên","Minh Khai","Sơn Đồng",
        "Song Phương","Tiền Yên","Vân Canh","Vân Côn","Yên Sở"
      ],

      "Mê Linh": [
        "Chi Đông","Quang Minh","Chu Phan","Đại Thịnh","Hoàng Kim",
        "Kim Hoa","Liên Mạc","Mê Linh","Tam Đồng","Thạch Đà",
        "Thanh Lâm","Tiền Phong","Tiến Thắng","Tiến Thịnh",
        "Tráng Việt","Tự Lập","Văn Khê","Vạn Yên"
      ],

      "Mỹ Đức": [
        "Đại Nghĩa","An Mỹ","An Phú","Bột Xuyên","Đốc Tín",
        "Đồng Tâm","Hồng Sơn","Hợp Thanh","Hợp Tiến","Hùng Tiến",
        "Lê Thanh","Mỹ Thành","Phù Lưu Tế","Phúc Lâm","Phùng Xá",
        "Tuy Lai","Thượng Lâm","Vạn Kim","Xuy Xá"
      ],

      "Phú Xuyên": [
        "Phú Xuyên","Phú Minh","Bạch Hạ","Châu Can","Chuyên Mỹ",
        "Đại Thắng","Đại Xuyên","Hoàng Long","Hồng Minh","Khai Thái",
        "Minh Tân","Nam Phong","Nam Tiến","Nam Triều","Phú Túc",
        "Phúc Tiến","Phượng Dực","Quang Hà","Quang Lãng","Tân Dân",
        "Tri Thủy","Tri Trung","Văn Hoàng","Vân Từ"
      ],

      "Phúc Thọ": [
        "Phúc Thọ","Cẩm Đình","Hát Môn","Hiệp Thuận","Liên Hiệp",
        "Long Xuyên","Ngọc Tảo","Phúc Hòa","Phụng Thượng",
        "Sen Phương","Tam Hiệp","Tam Thuấn","Thanh Đa",
        "Thọ Lộc","Tích Giang","Trạch Mỹ Lộc","Vân Hà",
        "Vân Nam","Võng Xuyên","Xuân Đình"
      ],

      "Quốc Oai": [
        "Quốc Oai","Cấn Hữu","Cộng Hòa","Đại Thành","Đồng Quang",
        "Đông Xuân","Đông Yên","Hòa Thạch","Liệp Tuyết",
        "Ngọc Liệp","Ngọc Mỹ","Phú Cát","Phú Mãn","Phượng Cách",
        "Sài Sơn","Tân Hòa","Tân Phú","Thạch Thán","Tuyết Nghĩa",
        "Yên Sơn"
      ],

      "Sóc Sơn": [
        "Sóc Sơn","Bắc Phú","Bắc Sơn","Đức Hòa","Đông Xuân",
        "Hiền Ninh","Hồng Kỳ","Kim Lũ","Mai Đình","Minh Phú",
        "Minh Trí","Nam Sơn","Phú Cường","Phù Linh","Phù Lỗ",
        "Phú Minh","Quang Tiến","Tân Dân","Tân Hưng",
        "Tiên Dược","Trung Giã","Việt Long","Xuân Giang","Xuân Thu"
      ],

      "Thạch Thất": [
        "Liên Quan","Bình Phú","Bình Yên","Cần Kiệm","Canh Nậu",
        "Chàng Sơn","Đại Đồng","Dị Nậu","Đồng Trúc","Hạ Bằng",
        "Hương Ngải","Hữu Bằng","Kim Quan","Lại Thượng",
        "Phú Kim","Phùng Xá","Tân Xã","Thạch Hòa",
        "Thạch Xá","Tiến Xuân","Yên Bình","Yên Trung"
      ],

      "Thanh Oai": [
        "Kim Bài","Bích Hòa","Bình Minh","Cao Dương","Cao Viên",
        "Cự Khê","Dân Hòa","Đỗ Động","Hồng Dương","Kim An",
        "Kim Thư","Liên Châu","Mỹ Hưng","Phương Trung",
        "Tam Hưng","Tân Ước","Thanh Cao","Thanh Mai",
        "Thanh Thùy","Thanh Văn","Xuân Dương"
      ],

      "Thanh Trì": [
        "Văn Điển","Đại Áng","Đông Mỹ","Duyên Hà","Hữu Hòa",
        "Liên Ninh","Ngọc Hồi","Ngũ Hiệp","Tả Thanh Oai",
        "Tam Hiệp","Tân Triều","Thanh Liệt","Tứ Hiệp",
        "Vạn Phúc","Vĩnh Quỳnh","Yên Mỹ"
      ],

      "Thường Tín": [
        "Thường Tín","Chương Dương","Dũng Tiến","Duyên Thái",
        "Hà Hồi","Hiền Giang","Hòa Bình","Khánh Hà","Hồng Vân",
        "Lê Lợi","Liên Phương","Minh Cường","Nghiêm Xuyên",
        "Nguyễn Trãi","Nhị Khê","Ninh Sở","Quất Động",
        "Tân Minh","Thắng Lợi","Thống Nhất","Thư Phú",
        "Tiền Phong","Tô Hiệu","Tự Nhiên","Văn Bình",
        "Văn Phú","Vạn Điểm","Vân Tảo"
      ],

      "Ứng Hòa": [
        "Vân Đình","Cao Sơn Tiến","Đại Cường","Đại Hùng",
        "Đội Bình","Đông Lỗ","Hòa Lâm","Hòa Nam","Hòa Phú",
        "Hoa Sơn","Hồng Quang","Kim Đường","Liên Bạt",
        "Lưu Hoàng","Minh Đức","Phù Lưu","Phương Tú",
        "Quảng Phú Cầu","Sơn Công","Tảo Dương Văn",
        "Trầm Lộng","Trung Tú","Trường Thịnh","Vạn Thái",
        "Viên An","Viên Nội"
      ]
    },
  },

  hcm: {
    label: "Tp. Hồ Chí Minh",
    hasStreet: true,
    districts: {

      // ───────────────── THÀNH PHỐ THỦ ĐỨC ─────────────────

      "Thủ Đức": [
        "An Khánh","An Lợi Đông","An Phú","Bình Chiểu","Bình Thọ",
        "Cát Lái","Hiệp Bình Chánh","Hiệp Bình Phước","Hiệp Phú",
        "Linh Chiểu","Linh Đông","Linh Tây","Linh Trung","Linh Xuân",
        "Long Bình","Long Phước","Long Thạnh Mỹ","Long Trường",
        "Phú Hữu","Phước Bình","Phước Long A","Phước Long B",
        "Tam Bình","Tam Phú","Tăng Nhơn Phú A","Tăng Nhơn Phú B",
        "Tân Phú","Thạnh Mỹ Lợi","Thảo Điền","Thủ Thiêm",
        "Trường Thạnh","Trường Thọ"
      ],

      // ───────────────── QUẬN ─────────────────

      "Quận 1": [
        "Bến Nghé","Bến Thành","Cầu Kho","Cầu Ông Lãnh",
        "Cô Giang","Đa Kao","Nguyễn Cư Trinh","Nguyễn Thái Bình",
        "Phạm Ngũ Lão","Tân Định"
      ],

      "Quận 3": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 9","Phường 10","Phường 11",
        "Phường 12","Phường 13","Phường 14","Võ Thị Sáu"
      ],

      "Quận 4": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 6","Phường 8","Phường 9","Phường 10",
        "Phường 13","Phường 14","Phường 15","Phường 16","Phường 18"
      ],

      "Quận 5": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 6","Phường 7","Phường 8",
        "Phường 9","Phường 10","Phường 11","Phường 12",
        "Phường 13","Phường 14"
      ],

      "Quận 6": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 6","Phường 7","Phường 8",
        "Phường 9","Phường 10","Phường 11","Phường 12",
        "Phường 13","Phường 14"
      ],

      "Quận 7": [
        "Bình Thuận","Phú Mỹ","Phú Thuận","Tân Hưng",
        "Tân Kiểng","Tân Phong","Tân Phú","Tân Quy",
        "Tân Thuận Đông","Tân Thuận Tây"
      ],

      "Quận 8": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 6","Phường 7","Phường 8",
        "Phường 9","Phường 10","Phường 11","Phường 12",
        "Phường 13","Phường 14","Phường 15","Phường 16"
      ],

      "Quận 10": [
        "Phường 1","Phường 2","Phường 4","Phường 5",
        "Phường 6","Phường 8","Phường 9","Phường 10",
        "Phường 11","Phường 12","Phường 13","Phường 14","Phường 15"
      ],

      "Quận 11": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 6","Phường 7","Phường 8",
        "Phường 9","Phường 10","Phường 11","Phường 12",
        "Phường 13","Phường 14","Phường 15","Phường 16"
      ],

      "Quận 12": [
        "An Phú Đông","Đông Hưng Thuận","Hiệp Thành",
        "Tân Chánh Hiệp","Tân Hưng Thuận","Tân Thới Hiệp",
        "Tân Thới Nhất","Thạnh Lộc","Thạnh Xuân",
        "Thới An","Trung Mỹ Tây"
      ],

      "Bình Tân": [
        "An Lạc","An Lạc A","Bình Hưng Hòa","Bình Hưng Hòa A",
        "Bình Hưng Hòa B","Bình Trị Đông","Bình Trị Đông A",
        "Bình Trị Đông B","Tân Tạo","Tân Tạo A"
      ],

      "Bình Thạnh": [
        "Phường 1","Phường 2","Phường 3","Phường 5",
        "Phường 6","Phường 7","Phường 11","Phường 12",
        "Phường 13","Phường 14","Phường 15","Phường 17",
        "Phường 19","Phường 21","Phường 22","Phường 24",
        "Phường 25","Phường 26","Phường 27","Phường 28"
      ],

      "Gò Vấp": [
        "Phường 1","Phường 3","Phường 4","Phường 5",
        "Phường 6","Phường 7","Phường 8","Phường 9",
        "Phường 10","Phường 11","Phường 12","Phường 13",
        "Phường 14","Phường 15","Phường 16","Phường 17"
      ],

      "Phú Nhuận": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 7","Phường 8","Phường 9",
        "Phường 10","Phường 11","Phường 13","Phường 14",
        "Phường 15","Phường 17"
      ],

      "Tân Bình": [
        "Phường 1","Phường 2","Phường 3","Phường 4",
        "Phường 5","Phường 6","Phường 7","Phường 8",
        "Phường 9","Phường 10","Phường 11","Phường 12",
        "Phường 13","Phường 14","Phường 15"
      ],

      "Tân Phú": [
        "Hiệp Tân","Hòa Thạnh","Phú Thạnh","Phú Thọ Hòa",
        "Phú Trung","Sơn Kỳ","Tân Quý","Tân Sơn Nhì",
        "Tân Thành","Tân Thới Hòa","Tây Thạnh"
      ],

      // ───────────────── HUYỆN ─────────────────

      "Bình Chánh": [
        "Tân Túc","An Phú Tây","Bình Chánh","Bình Hưng",
        "Bình Lợi","Đa Phước","Hưng Long","Lê Minh Xuân",
        "Phong Phú","Phạm Văn Hai","Quy Đức","Tân Kiên",
        "Tân Nhựt","Tân Quý Tây","Vĩnh Lộc A","Vĩnh Lộc B"
      ],

      "Cần Giờ": [
        "Cần Thạnh","An Thới Đông","Bình Khánh",
        "Long Hòa","Lý Nhơn","Tam Thôn Hiệp","Thạnh An"
      ],

      "Củ Chi": [
        "Củ Chi","An Nhơn Tây","An Phú","Bình Mỹ","Hòa Phú",
        "Nhuận Đức","Phạm Văn Cội","Phú Hòa Đông","Phú Mỹ Hưng",
        "Phước Hiệp","Phước Thạnh","Phước Vĩnh An","Tân An Hội",
        "Tân Phú Trung","Tân Thạnh Đông","Tân Thạnh Tây",
        "Tân Thông Hội","Thái Mỹ","Trung An","Trung Lập Hạ",
        "Trung Lập Thượng"
      ],

      "Hóc Môn": [
        "Hóc Môn","Bà Điểm","Đông Thạnh","Nhị Bình",
        "Tân Hiệp","Tân Thới Nhì","Tân Xuân","Thới Tam Thôn",
        "Trung Chánh","Xuân Thới Đông","Xuân Thới Sơn","Xuân Thới Thượng"
      ],

      "Nhà Bè": [
        "Nhà Bè","Hiệp Phước","Long Thới",
        "Nhơn Đức","Phú Xuân","Phước Kiển","Phước Lộc"
      ]
    },
  },

  danang: {
    label: "Tp. Đà Nẵng",
    hasStreet: false,
    districts: {
      "Hải Châu":      ["Bình Hiên","Bình Thuận","Hải Châu 1","Hải Châu 2","Hòa Cường Bắc","Hòa Cường Nam","Hòa Thuận Đông","Hòa Thuận Tây","Nam Dương","Phước Ninh","Thạch Thang","Thanh Bình","Thuận Phước"],
      "Thanh Khê":     ["An Khê","Chính Gián","Hòa Khê","Tam Thuận","Tân Chính","Thanh Khê Đông","Thanh Khê Tây","Thạc Gián","Vĩnh Trung","Xuân Hà"],
      "Sơn Trà":       ["An Hải Bắc","An Hải Đông","An Hải Tây","Mân Thái","Nại Hiên Đông","Phước Mỹ","Thọ Quang"],
      "Ngũ Hành Sơn":  ["Hòa Hải","Hòa Quý","Khuê Mỹ","Mỹ An"],
      "Liên Chiểu":    ["Hòa Hiệp Bắc","Hòa Hiệp Nam","Hòa Khánh Bắc","Hòa Khánh Nam","Hòa Minh"],
      "Cẩm Lệ":        ["Hòa An","Hòa Phát","Hòa Thọ Đông","Hòa Thọ Tây","Hòa Xuân","Khuê Trung"],
      "Hòa Vang":      ["Hòa Bắc","Hòa Châu","Hòa Khương","Hòa Liên","Hòa Nhơn","Hòa Ninh","Hòa Phong","Hòa Phú","Hòa Sơn","Hòa Tiến","Hòa Trung"],
    },
  },

  haiphong: {
    label: "Tp. Hải Phòng",
    hasStreet: false,
    districts: {
      "Hồng Bàng":   ["Hoàng Văn Thụ","Hùng Vương","Minh Khai","Phan Bội Châu","Phạm Hồng Thái","Quán Toan","Sở Dầu","Thượng Lý","Trại Chuối"],
      "Lê Chân":     ["An Biên","An Dương","Cát Dài","Dư Hàng","Dư Hàng Kênh","Đông Hải","Hàng Kênh","Kênh Dương","Lam Sơn","Nghĩa Xá","Niệm Nghĩa","Trần Nguyên Hãn","Vĩnh Niệm"],
      "Ngô Quyền":   ["Cầu Đất","Cầu Tre","Đằng Giang","Đằng Lâm","Đổng Quốc Bình","Gia Viên","Lạc Viên","Lê Lợi","Máy Chai","Máy Tơ","Vạn Mỹ"],
      "Hải An":      ["Đằng Hải","Đằng Lâm","Đông Hải 1","Đông Hải 2","Nam Hải","Tràng Cát"],
      "Kiến An":     ["Bắc Sơn","Đồng Hòa","Nam Sơn","Phù Liễu","Quán Trữ","Tràng Minh","Trần Thành Ngọ","Văn Đẩu"],
      "Dương Kinh":  ["Anh Dũng","Đa Phúc","Hải Thành","Hòa Nghĩa","Tân Thành"],
      "Đồ Sơn":      ["Bàng La","Hòa Đồng","Minh Đức","Ngọc Hải","Vạn Hương","Vạn Sơn"],
      "An Dương":    ["An Đồng","An Hòa","Đặng Cương","Đồng Thái","Hồng Phong","Lê Lợi","Nam Sơn","Quốc Tuấn"],
    },
  },

  hue: {
    label: "Tp. Huế",
    hasStreet: false,
    districts: {
      "Phú Xuân":     ["An Cựu","An Đông","An Hòa","An Tây","Đông Ba","Gia Hội","Hương Long","Hương Sơ","Kim Long","Phú Bình","Phú Cát","Phú Hiệp","Phú Hòa","Phú Hội","Phú Nhuận","Phú Thuận","Tây Lộc","Thuận Hòa","Thuận Lộc","Thuận Thành","Trường An","Vĩnh Ninh","Vỹ Dạ","Xuân Phú"],
      "Hương Thủy":   ["Dương Hòa","Phú Bài","Thủy Bằng","Thủy Châu","Thủy Dương","Thủy Lương","Thủy Phù","Thủy Phương","Thủy Tân","Thủy Thanh","Thủy Vân"],
      "Hương Trà":    ["Bình Điền","Bình Thành","Hải Dương","Hương An","Hương Chữ","Hương Hồ","Hương Phong","Hương Thọ","Hương Toàn","Hương Văn","Hương Vinh","Tứ Hạ"],
      "Phú Vang":     ["Phú An","Phú Dương","Phú Đa","Phú Hải","Phú Lương","Phú Mậu","Phú Mỹ","Phú Thanh","Phú Thượng","Phú Xuân","Thuận An","Vinh An","Vinh Hà","Vinh Phú","Vinh Thái","Vinh Thanh","Vinh Xuân"],
      "Phú Lộc":      ["Lăng Cô","Phú Lộc","Lộc An","Lộc Bình","Lộc Bổn","Lộc Điền","Lộc Hòa","Lộc Sơn","Lộc Thủy","Lộc Tiến","Lộc Trì","Vinh Giang","Vinh Hải","Vinh Hiền","Vinh Hưng","Xuân Lộc"],
    },
  },

  dongnai: {
    label: "Tp. Đồng Nai",
    hasStreet: false,
    districts: {
      "Biên Hòa":     ["An Bình","Bình Đa","Bửu Hòa","Bửu Long","Hiệp Hòa","Hóa An","Hố Nai","Long Bình","Long Bình Tân","Phước Tân","Quyết Thắng","Tân Biên","Tân Hiệp","Tân Hòa","Tân Hạnh","Tân Mai","Tân Phong","Tân Tiến","Thống Nhất","Trảng Dài","Trung Dũng"],
      "Long Khánh":   ["Bảo Quang","Bảo Vinh","Phú Bình","Suối Tre","Xuân An","Xuân Bình","Xuân Hòa","Xuân Lập","Xuân Tân","Xuân Thanh"],
      "Nhơn Trạch":   ["Đại Phước","Hiệp Phước","Long Tân","Long Thọ","Phú Đông","Phú Hội","Phú Thạnh","Phước An","Phước Khánh","Vĩnh Thanh"],
      "Trảng Bom":    ["An Viễn","Bắc Sơn","Bình Minh","Cây Gáo","Đông Hòa","Giang Điền","Hố Nai 3","Hưng Thịnh","Quảng Tiến","Sông Trầu","Tây Hòa","Thanh Bình","Trung Hòa","Trung Sơn"],
      "Long Thành":   ["An Phước","Bàu Cạn","Bình An","Bình Sơn","Cẩm Đường","Long An","Long Đức","Long Phước","Phước Bình","Phước Thái","Tam An","Tân Hiệp"],
    },
  },

  cantho: {
    label: "Tp. Cần Thơ",
    hasStreet: false,
    districts: {
      "Ninh Kiều":  ["An Bình","An Cư","An Hòa","An Khánh","An Nghiệp","An Phú","Cái Khế","Hưng Lợi","Tân An","Thới Bình","Xuân Khánh"],
      "Bình Thủy":  ["An Thới","Bình Thủy","Bùi Hữu Nghĩa","Long Hòa","Long Tuyền","Thới An Đông","Trà An","Trà Nóc"],
      "Cái Răng":   ["Ba Láng","Hưng Phú","Hưng Thạnh","Lê Bình","Phú Thứ","Tân Phú","Thường Thạnh"],
      "Ô Môn":      ["Long Hưng","Phước Thới","Thới An","Thới Long","Trường Lạc"],
      "Thốt Nốt":   ["Thốt Nốt","Thuận An","Tân Lộc","Trung Kiên","Trung Nhứt"],
      "Phong Điền": ["Giai Xuân","Mỹ Khánh","Nhơn Ái","Nhơn Nghĩa","Tân Thới","Trường Long"],
      "Cờ Đỏ":      ["Cờ Đỏ","Đông Hiệp","Đông Thắng","Thạnh Phú","Thới Đông","Thới Hưng","Thới Xuân","Trung An","Trung Hưng"],
    },
  },
};

// Helper: lấy danh sách thành phố cho dropdown
export const CITY_OPTIONS = Object.entries(LOCATION_DATA).map(([id, data]) => ({
  id,
  label: data.label,
  hasStreet: data.hasStreet,
}));

// Helper: lấy danh sách quận/huyện theo city
export function getDistricts(cityId) {
  return Object.keys(LOCATION_DATA[cityId]?.districts || {});
}

// Helper: lấy danh sách phường/xã theo city + district
export function getWards(cityId, district) {
  return LOCATION_DATA[cityId]?.districts?.[district] || [];
}
