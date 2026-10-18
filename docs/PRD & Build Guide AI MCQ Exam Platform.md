# PRD & Build Guide: AI MCQ Exam Platform

Oct 17, 2026 · @NTKien

## 1. Tổng quan

Nền tảng web giúp giảng viên sinh ngân hàng câu hỏi trắc nghiệm bằng AI, dựng đề nhiều mã đề, in thi trên giấy và chấm tự động từ ảnh phiếu trả lời. Tài liệu này gồm PRD (mục 1–9) và hướng dẫn triển khai với Claude Code (mục 10–11). Giao diện và nội dung câu hỏi dùng tiếng Anh; tài liệu này viết bằng tiếng Việt.

**Vấn đề cần giải quyết**

- Soạn câu hỏi thủ công, tốn thời gian, ngân hàng câu hỏi nằm rải rác trong Word và Excel của từng giảng viên.
- Dựng đề, xáo trộn mã đề và làm đáp án thủ công dễ sai.
- Chấm phiếu bằng tay chậm; không có thống kê chất lượng câu hỏi sau mỗi kỳ thi.

**Mục tiêu**

1. Thư viện câu hỏi dùng chung theo môn và module, có quy trình duyệt của trưởng bộ môn.
2. AI sinh câu hỏi nháp từ module, prompt hoặc tài liệu giảng dạy; con người luôn duyệt trước khi dùng.
3. Dựng đề theo 3 cách (Excel, chọn từ ngân hàng, random theo module và độ khó), chốt đề, xuất nhiều mã đề.
4. Chấm từ ảnh phiếu chụp trong ứng dụng; mọi ca nghi ngờ đều được đánh dấu để giảng viên kiểm tra.
5. Lưu kết quả chi tiết, xuất Excel, thống kê theo câu hỏi.

**Ngoài phạm vi phiên bản đầu**

- Thi trực tuyến trên máy; câu hỏi có hình ảnh, công thức, code; câu tự luận.
- Nhận dạng chữ viết tay (OCR); đăng nhập SSO; app mobile native.
- Nhiều trường dùng chung một hệ thống (multi-tenant theo trường).
- Thương mại hóa, thanh toán, SLA vận hành.

**Chỉ số thành công (đề xuất, hiệu chỉnh sau pilot)**

| Chỉ số | Mục tiêu |
| --- | --- |
| Độ chính xác đọc từng ô tô trên ảnh đạt chuẩn | ≥ 99,5% |
| Tỷ lệ đọc sai mà không bị cảnh báo | ≤ 0,1% số phiếu |
| Tỷ lệ phiếu phải review tay (ảnh đạt chuẩn) | ≤ 10% |
| Thời gian xử lý một phiếu | ≤ 5 giây |
| Xử lý 1.000 phiếu (4 worker) | ≤ 30 phút |
| Tỷ lệ câu AI được duyệt ở batch pilot | ≥ 60% |

## 2. Phạm vi, quyết định và giả định

Phần này tách rõ cái bạn đã chốt và cái tôi tự chọn mặc định. Các mặc định (nhóm B) cần bạn rà soát trước khi build.

**A. Quyết định đã chốt trong phần hỏi đáp**

| Chủ đề | Quyết định |
| --- | --- |
| Người dùng | Một trường, nhiều bộ môn/khoa dùng chung hệ thống |
| Vai trò | Admin, Trưởng bộ môn (HoD), Giảng viên, Sinh viên (có đăng nhập) |
| Quy mô | 50 môn học, 1.000 sinh viên |
| Loại câu hỏi | Một đáp án đúng, nhiều đáp án đúng, True/False; số lựa chọn thay đổi |
| Metadata | Module, độ khó, CLO, tag, giải thích đáp án |
| Sinh bằng AI | Từ module + prompt hoặc từ tài liệu upload; kiểm soát số lượng, độ khó, ngôn ngữ |
| Duyệt câu hỏi | Draft → chờ duyệt → Approved; HoD duyệt câu hỏi và đề vào thư viện chung |
| Câu hỏi trùng | Phát hiện khi sinh, import và nhập tay |
| Import | Chỉ template Excel |
| Dựng đề | Excel (tham chiếu mã câu hỏi), chọn từ ngân hàng, random theo module và độ khó |
| Mã đề | Xáo trộn câu hỏi và đáp án thành nhiều mã đề |
| Điểm | Mỗi câu bằng nhau, quy về thang 10, không trừ điểm câu sai |
| Chốt đề | Khóa nội dung; cho phép clone; cho phép đính chính và chấm lại |
| Xuất đề | File Word, không header/footer; nhiều mã đề kèm file đáp án cho giảng viên |
| Phiếu trả lời | Hệ thống tự sinh mẫu phiếu |
| Chấm | Chụp ảnh trong ứng dụng; màn hình review bắt buộc; mã SV đối chiếu danh sách lớp, lệch thì đánh dấu cần kiểm tra |
| Lưu ảnh | Giữ ảnh scan gốc 4 tháng |
| Kỹ thuật | Web app; Python/FastAPI cho AI và xử lý ảnh; chạy localhost trước, deploy sau |
| AI provider | Trừu tượng hóa để đổi nhà cung cấp; không giới hạn ngân sách |
| Ngôn ngữ | Giao diện và nội dung: tiếng Anh |
| Mức độ | Sản phẩm nội bộ, thử nghiệm |

**B. Mặc định do BA chọn (cần bạn xác nhận)**

| # | Mặc định | Lý do |
| --- | --- | --- |
| D1 | Phiếu trả lời xuất **PDF** (đề thi và file đáp án vẫn là Word) | Word không đảm bảo tọa độ chính xác; scan cần vị trí ô tô cố định |
| D2 | Mã SV: lưới ô tô 8 chữ số (cấu hình được, tối đa 10). Mã đề: lưới 3 chữ số. QR ở đầu phiếu chứa mã đề thi và phiên bản layout. Không nhận dạng chữ viết tay | Ô tô cho độ chính xác cao hơn OCR |
| D3 | Câu nhiều đáp án chấm **tất cả hoặc không**: chọn đúng đủ bộ đáp án mới được điểm. Chấm từng phần để vào backlog | Đơn giản, minh bạch, đúng yêu cầu "không trừ điểm" |
| D4 | Tối đa 60 câu/đề và 6 lựa chọn (A–F) mỗi câu để vừa một trang A4 | Giữ layout phiếu đơn giản ở v1 |
| D5 | Câu hỏi chỉ là văn bản thuần: không hình, công thức, code | Bạn chưa nêu nhu cầu; tránh phức tạp hóa export và scan |
| D6 | Câu có đáp án "All of the above / None of the above" tự bị khóa thứ tự lựa chọn khi xáo trộn | Tránh đề sai logic sau khi xáo |
| D7 | Khi dựng đề, giảng viên dùng được câu Approved và câu do chính mình tạo (trừ câu bị Rejected). Chỉ câu Approved mới vào thư viện chung | Không chặn giảng viên chờ duyệt |
| D8 | File Excel dựng đề chỉ chứa mã câu hỏi có sẵn. Câu hỏi mới nhập bằng template import câu hỏi và luôn được lưu vào ngân hàng | Diễn giải yêu cầu "tham chiếu mã câu hỏi" và "có lưu câu hỏi import" |
| D9 | Sinh viên: xem kết quả đã được công bố, chi tiết bài làm, ảnh phiếu của mình và gửi yêu cầu phúc khảo | Cần cho việc dùng ảnh scan để đối chứng |
| D10 | Mã SV là số. Nếu mã của trường có chữ cái, cần đổi cách mã hóa (xem mục 11) | Lưới ô tô ký tự chữ làm phiếu rất dài |
| D11 | Thời hạn 4 tháng tính từ ngày tải ảnh lên; điểm và đáp án đã chấm giữ lâu dài | Chỉ ảnh bị xóa, kết quả vẫn còn |
| D12 | Frontend React + Vite + TypeScript; CSDL PostgreSQL; hàng đợi Redis + RQ | Camera, màn hình review cần tương tác phong phú |

## 3. Vai trò, phân quyền và mô hình tổ chức

Hệ thống phục vụ một trường với cấu trúc Bộ môn/Khoa → Môn học → Module. Quyền được giới hạn theo bộ môn và theo môn được gán, không chỉ theo vai trò.

1. **Department** (bộ môn/khoa) có một hoặc nhiều Trưởng bộ môn.
2. **Course** (môn học, ví dụ ISD201) thuộc một Department, có danh sách CLO và các Module có thứ tự.
3. **Module** là đơn vị chia nhỏ nội dung của môn (chương, chủ đề); mỗi câu hỏi thuộc đúng một Module.
4. **Class/Roster** là danh sách sinh viên; **Exam session** gắn một đề đã chốt với một roster và một ngày thi.

| Chức năng | Admin | Trưởng bộ môn | Giảng viên | Sinh viên |
| --- | --- | --- | --- | --- |
| Quản lý người dùng, vai trò, bộ môn | Có | — | — | — |
| Quản lý môn, module, CLO | Có | Trong bộ môn | — | — |
| Gán giảng viên vào môn | Có | Trong bộ môn | — | — |
| Cấu hình AI provider, giới hạn hệ thống | Có | — | — | — |
| Tạo, sửa câu hỏi (Draft) | — | Có | Môn được gán | — |
| Gửi duyệt câu hỏi | — | Có | Có | — |
| Duyệt, từ chối câu hỏi | — | Trong bộ môn | — | — |
| Sinh câu hỏi bằng AI, import Excel | — | Có | Môn được gán | — |
| Dựng, chốt, clone đề | — | Có | Môn được gán | — |
| Duyệt đề vào thư viện chung | — | Trong bộ môn | — | — |
| Xuất đề và phiếu trả lời | — | Có | Đề của mình | — |
| Scan, review, chấm | — | Có | Đề của mình | — |
| Đính chính đáp án, chấm lại | — | Có | Đề của mình | — |
| Công bố kết quả, xuất Excel | — | Có | Đề của mình | — |
| Xem kết quả và ảnh phiếu | Xem tất cả | Trong bộ môn | Đề của mình | Của mình, sau khi công bố |
| Gửi và xử lý phúc khảo | — | Xử lý | Xử lý | Gửi |

**Quy tắc phạm vi dữ liệu**

- Giảng viên chỉ thấy môn được gán; Trưởng bộ môn thấy toàn bộ môn của bộ môn mình; Admin thấy tất cả.
- Sinh viên chỉ thấy bài của chính mình và chỉ sau khi giảng viên công bố kết quả.
- Mọi thao tác duyệt, chốt đề, đính chính, chấm lại, đổi vai trò đều ghi audit log (ai, khi nào, trước và sau).

## 4. Yêu cầu chức năng: ngân hàng câu hỏi

Ưu tiên theo MoSCoW: M = bắt buộc cho v1, S = nên có, C = có thể làm sau.

**4.1 Đăng nhập và dữ liệu nền**

| ID | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-AUTH-1 | Đăng nhập email + mật khẩu, đổi mật khẩu; Admin đặt lại mật khẩu | M |
| FR-AUTH-2 | Phân quyền 4 vai trò, giới hạn theo bộ môn và môn được gán (mục 3) | M |
| FR-AUTH-3 | Admin/HoD quản lý bộ môn, môn học, module (có thứ tự), CLO | M |
| FR-AUTH-4 | Import danh sách sinh viên bằng Excel (student\_code, full\_name, email, class); tự tạo tài khoản, buộc đổi mật khẩu lần đầu | M |

**4.2 Ngân hàng câu hỏi**

| ID | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-QB-1 | Ba loại: *Single* (2–6 lựa chọn, đúng 1), *Multiple* (3–6 lựa chọn, đúng ≥ 1), *True/False* (2 lựa chọn cố định, đúng 1) | M |
| FR-QB-2 | Trường dữ liệu: stem, lựa chọn, đáp án đúng, giải thích, module, độ khó (Easy/Medium/Hard), CLO (0..n), tag, cờ khóa thứ tự lựa chọn | M |
| FR-QB-3 | Mã câu hỏi tự sinh, duy nhất, không đổi (ví dụ ISD201-M03-0042) | M |
| FR-QB-4 | Mỗi lần sửa tạo một revision bất biến; xem được lịch sử và so sánh | M |
| FR-QB-5 | Tìm kiếm và lọc theo môn, module, độ khó, CLO, tag, trạng thái, tác giả, nguồn (manual/AI/import), full-text | M |
| FR-QB-6 | Câu đã dùng trong đề đã chốt chỉ được archive, không xóa cứng | M |
| FR-QB-7 | Thống kê sử dụng: số đề đã dùng, tỷ lệ trả lời đúng lịch sử | S |

**4.3 Luồng duyệt**

- Trạng thái: **Draft → Pending review → Approved** hoặc **Rejected** (kèm lý do). Câu bị Rejected sửa xong gửi duyệt lại.
- Sửa câu đã Approved tạo revision mới ở trạng thái Pending. Revision Approved cũ vẫn là bản hiệu lực cho đến khi bản mới được duyệt.
- HoD có thể sửa và duyệt trong một bước; duyệt hàng loạt theo batch AI hoặc batch import.
- Đề (đã chốt) có thể được gửi để HoD duyệt vào thư viện đề dùng chung của môn.

*Tiêu chí nghiệm thu*

- Khi giảng viên gửi 10 câu Draft, HoD của bộ môn thấy đúng 10 câu trong hàng chờ; HoD bộ môn khác không thấy.
- Khi HoD từ chối một câu mà không nhập lý do, hệ thống không cho lưu.
- Khi sửa một câu Approved đang nằm trong đề đã chốt, đề đã chốt không thay đổi nội dung.

**4.4 Sinh câu hỏi bằng AI**

| ID | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-AI-1 | Chọn môn và một hoặc nhiều module; nguồn là prompt tự do, tài liệu upload (PDF, DOCX, PPTX, TXT; ≤ 20 MB/file, ≤ 5 file/lần) hoặc cả hai | M |
| FR-AI-2 | Tham số kiểm soát: số câu (1–50/lần), tỷ lệ loại câu, số lựa chọn, phân bố độ khó, CLO mục tiêu, ngôn ngữ (mặc định English), hướng dẫn thêm | M |
| FR-AI-3 | Chạy bất đồng bộ, hiện tiến độ, hủy được, có thể rời trang và quay lại | M |
| FR-AI-4 | Kết quả là JSON có schema, được validate (đúng số đáp án đúng theo loại, không lựa chọn trùng, đủ trường); sai schema thì tự thử lại tối đa 2 lần | M |
| FR-AI-5 | Khi dùng tài liệu: mỗi câu kèm tham chiếu nguồn (tên file, trang hoặc đoạn); AI chỉ được dựa vào nội dung tài liệu | M |
| FR-AI-6 | Câu sinh ra vào một *generation batch* trạng thái Draft; màn hình review cho sửa nhanh, bỏ, sinh lại từng câu, gửi duyệt hàng loạt. Không có chế độ tự duyệt | M |
| FR-AI-7 | Lưu provenance: provider, model, phiên bản prompt, tham số, token dùng, người chạy | M |
| FR-AI-8 | Lớp trừu tượng `LLMProvider` (Anthropic mặc định; thêm OpenAI/khác bằng cấu hình), có provider giả (fake) cho test | M |
| FR-AI-9 | Tự gợi ý CLO và tag cho từng câu, người dùng sửa được | S |

**4.5 Import Excel và phát hiện câu trùng**

- Một template Excel duy nhất cho câu hỏi. Cột: `course_code`, `module`, `type` (single/multiple/true\_false), `difficulty`, `stem`, `option_a` … `option_f`, `correct` (ví dụ `B` hoặc `A,C` hoặc `TRUE`), `explanation`, `clo` (ngăn cách bằng `;`), `tags` (ngăn cách bằng `;`), `lock_option_order` (Y/N), `external_id` (tùy chọn).
- Quy trình: tải lên → kiểm tra thử (dry-run) → báo lỗi theo từng dòng, tải được file lỗi → xác nhận → tạo câu hỏi ở trạng thái Draft (có tùy chọn gửi duyệt ngay).
- Phát hiện trùng chạy ở ba chỗ: sau khi AI sinh, trong lúc import và khi lưu câu nhập tay. Phạm vi so sánh là toàn bộ câu của cùng môn.
- Cách làm v1: chuẩn hóa văn bản (chữ thường, bỏ dấu câu và khoảng trắng thừa) rồi so khớp chính xác; thêm so khớp mờ (fuzzy). Ngưỡng mặc định 0,85 cho stem và 0,85 cho bộ lựa chọn, cấu hình được. Có giao diện embedding để nâng cấp sau.
- Khi nghi trùng, hiện câu đã có kèm độ giống; người dùng chọn: bỏ qua câu mới, vẫn thêm, hoặc thay bằng revision mới.

*Tiêu chí nghiệm thu*

- File import có 100 dòng, 3 dòng lỗi: hệ thống báo đúng 3 dòng và lý do, không tạo câu nào cho tới khi người dùng xác nhận.
- Câu mới giống câu cũ chỉ khác dấu câu hoặc viết hoa bị đánh dấu trùng.

## 5. Yêu cầu chức năng: đề thi

Một đề thi là danh sách câu hỏi cố định cộng cấu hình in và chấm. Sau khi chốt, nội dung không đổi được; mọi thay đổi đi qua clone hoặc đính chính có ghi vết.

**5.1 Ba cách dựng đề**

| Cách | Cách hoạt động | Quy tắc |
| --- | --- | --- |
| Import Excel | Template một cột `question_code` (thứ tự dòng là thứ tự câu) | Mã không tồn tại hoặc không thuộc môn: báo lỗi theo dòng, không tạo đề. Câu hỏi mới nhập qua template import câu hỏi (mục 4.5) |
| Chọn từ ngân hàng | Lọc theo module, độ khó, CLO, tag; thêm, xóa, sắp xếp lại | Chỉ câu Approved hoặc câu do chính người dựng đề tạo (trừ Rejected) |
| Random theo cấu hình | Bảng quy tắc: module × độ khó × số câu (ví dụ M1: 2 Easy + 3 Hard) | Bấm *Generate* để bốc ngẫu nhiên; thiếu câu trong kho thì báo rõ module và độ khó thiếu; xem trước, đổi riêng từng câu hoặc bốc lại toàn bộ |

Sau khi bốc, đề luôn là danh sách câu cụ thể (lưu seed để tái lập). Có thể kết hợp: bốc ngẫu nhiên rồi chỉnh tay.

**5.2 Cấu hình đề**

- Thông tin: tiêu đề, môn, mã đề thi, thời lượng (chỉ để in), hướng dẫn làm bài (văn bản ngắn).
- Số mã đề (mặc định 4, mã 101–104, tối đa 10); bật hoặc tắt xáo thứ tự câu và xáo thứ tự lựa chọn.
- Điểm mỗi câu = 10 ÷ số câu, làm tròn 2 chữ số khi hiển thị; không trừ điểm câu sai; điểm đạt mặc định 5,0 và cấu hình được.
- Đề tối đa 60 câu (mục 2, D4).

**5.3 Chốt đề, mã đề, clone**

1. Khi bấm *Finalize*, hệ thống chụp bản sao nội dung từng câu (theo revision), sinh các mã đề bằng seed và lưu thứ tự câu và thứ tự lựa chọn của từng mã. Từ đó nội dung bất biến.
2. Đề đã chốt có thể *Clone* thành đề Draft mới để chỉnh sửa; đề gốc giữ nguyên.
3. Khi xáo, câu có cờ khóa thứ tự lựa chọn giữ nguyên vị trí các lựa chọn.
4. Câu *Multiple* được in kèm dòng "Select all that apply".

**5.4 Đính chính và chấm lại**

- Sau khi chốt, giảng viên có thể đính chính một câu bằng một trong ba cách: đổi đáp án đúng, chấp nhận thêm đáp án, hủy câu (mọi sinh viên được điểm câu đó).
- Đính chính bắt buộc ghi lý do, ghi audit log và áp dụng cho mọi mã đề.
- Hệ thống chấm lại toàn bộ bài đã chấm từ dữ liệu đáp án đã lưu, không cần scan lại; giữ lịch sử các lần chấm và so sánh điểm trước và sau.
- Đề đã đính chính đánh dấu rõ trong báo cáo; câu hỏi gốc trong ngân hàng tự được gắn cờ cần xem lại.

**5.5 Xuất đề**

Mỗi lần xuất tạo một gói ZIP:

| File | Định dạng | Nội dung |
| --- | --- | --- |
| Đề thi, mỗi mã đề một file | Word (.docx) | Mã đề nổi bật đầu trang 1, tiêu đề, thời lượng, hướng dẫn, các câu theo thứ tự của mã đề. Không header/footer |
| Đáp án cho giảng viên | Word (.docx) | Bảng đáp án của từng mã đề, kèm bảng đối chiếu số câu gốc và số câu trong từng mã |
| Phiếu trả lời | PDF | Một mẫu dùng chung cho mọi mã đề của đề thi (mục 6) |

*Tiêu chí nghiệm thu*

- Random 3 module × 2 độ khó theo đúng số câu cấu hình cho ra đúng số câu từng nhóm; thiếu kho thì báo lỗi, không cho chốt.
- Hai mã đề của cùng một đề có cùng tập câu hỏi nhưng khác thứ tự; bảng đáp án từng mã khớp với nội dung file đề.
- Sau khi chốt, sửa câu gốc trong ngân hàng không làm đổi file Word xuất lại.

## 6. Phiếu trả lời, scan và chấm bài

Đây là phần rủi ro kỹ thuật cao nhất. Nguyên tắc xuyên suốt: **không bao giờ đọc sai mà không báo**. Ca nào máy không chắc chắn đều vào hàng review cho giảng viên.

**6.1 Phiếu trả lời do hệ thống sinh**

- A4 dọc, một trang, PDF vector sinh từ một *layout engine*. Layout engine xuất đồng thời PDF và một file layout JSON (tọa độ mm của mọi ô tô, marker, QR). Bộ đọc scan dùng chính file JSON này, nên bản in và bộ đọc không thể lệch nhau.
- Bốn marker ArUco ở bốn góc để nắn phối cảnh; một mã QR chứa mã đề thi, phiên bản layout và checksum.
- Lưới mã sinh viên (8 cột × chữ số 0–9, cấu hình được) và lưới mã đề (3 cột × chữ số 0–9). Sinh viên tô theo mã in trên đề của mình.
- Vùng đáp án: mỗi câu một hàng, tối đa 6 ô (A–F). Câu có ít lựa chọn hơn số ô tối đa thì các ô thừa được in mờ. Câu True/False dùng A = True, B = False.
- Có ô họ tên và chữ ký viết tay để giảng viên đối chiếu; máy không đọc các ô này.
- Layout JSON được lưu cùng đề và bất biến sau khi chốt.

**6.2 Đầu vào ảnh**

- Trang Scan chụp ngay trong ứng dụng: camera trực tiếp với khung hướng dẫn căn phiếu, chụp liên tiếp nhiều phiếu, mỗi ảnh được gửi lên và xếp hàng xử lý.
- Ngoài ra tải lên ảnh (JPG, PNG) hoặc PDF nhiều trang từ máy scan.
- Camera trực tiếp của trình duyệt chỉ chạy trên HTTPS hoặc localhost. Khi dùng điện thoại truy cập máy chủ trong mạng LAN cần chứng chỉ HTTPS cục bộ; nút "Take photo" gọi camera hệ thống là phương án dự phòng.
- Chuẩn ảnh đề nghị: thấy đủ cả 4 marker, cạnh dài ≥ 1.600 px, phiếu phẳng và không bị bóng che lên vùng ô tô.

**6.3 Quy trình xử lý một phiếu**

Mỗi ảnh là một job nền; kết quả hiện lên màn hình ngay khi job xong.

&#91;embedded content: quy trình chấm một phiếu · 5 bước, 1 điểm rẽ\]

Phiếu không có cờ được tự chấm ngay; phiếu có cờ chờ giảng viên sửa và xác nhận.

**6.4 Khi nào đánh dấu "cần kiểm tra"**

| Tình huống | Cách xử lý |
| --- | --- |
| Không đủ 4 marker hoặc không đọc được QR | Đánh dấu lỗi ảnh, yêu cầu chụp lại |
| QR thuộc đề thi khác với đề đang chấm | Chặn và báo sai đề |
| Cột mã SV trống hoặc có từ 2 ô tô | Cần kiểm tra, gợi ý sinh viên gần giống trong roster |
| Mã SV không có trong danh sách lớp | Cần kiểm tra |
| Mã SV trùng với phiếu khác trong cùng kỳ thi | Cần kiểm tra cả hai phiếu |
| Mã đề không thuộc đề thi | Cần kiểm tra |
| Câu Single hoặc True/False có từ 2 ô tô | Cần kiểm tra câu đó |
| Ô tô mờ, nằm giữa ngưỡng chắc chắn tô và chắc chắn trống | Cần kiểm tra câu đó |
| Ô tô ở lựa chọn không tồn tại của câu | Cần kiểm tra câu đó |
| Từ 30% số câu trở lên bỏ trống (ngưỡng cấu hình được) | Cần kiểm tra, vì có thể là lỗi đọc |

Câu bỏ trống đơn lẻ là hợp lệ: ghi nhận "blank", tính 0 điểm, không gắn cờ.

**6.5 Màn hình review**

- Hàng chờ các phiếu cần kiểm tra, lọc theo lý do, chuyển phiếu bằng phím tắt.
- Ảnh đã nắn thẳng kèm lớp phủ: ô máy đọc là đã tô, ô nghi ngờ, ô lỗi (khác màu); chọn câu để phóng to.
- Sửa tại chỗ: bấm ô để đổi đáp án; tìm sinh viên trong roster để sửa mã SV; đổi mã đề; đánh dấu phiếu không hợp lệ.
- Bấm Confirm thì phiếu thành *Confirmed*, điểm tính lại ngay; mọi chỉnh sửa lưu audit (ai sửa gì).
- Phiếu tự chấm vẫn mở xem được ảnh để lấy mẫu kiểm tra và mở lại sửa được.

**6.6 Kết quả, báo cáo Excel, cổng sinh viên**

Dữ liệu lưu cho mỗi phiếu: sinh viên, mã đề, trạng thái, ảnh gốc, đáp án chọn của từng câu, đúng hay sai, điểm, lần chấm và lịch sử sửa tay.

| Sheet Excel | Cột chính |
| --- | --- |
| Results | student\_code, full\_name, class, version, correct, total, score (thang 10), pass/fail, status (auto/confirmed), scanned\_at |
| Answers | Mỗi câu một cột theo thứ tự câu gốc: đáp án sinh viên chọn (chữ cái gốc, ví dụ A hoặc AC), cột đúng/sai kèm theo |
| Question stats | Mã câu, module, độ khó, số người trả lời, số người đúng, tỷ lệ đúng, phân bố lựa chọn A–F, cờ "quá khó/quá dễ" (tỷ lệ đúng dưới 20% hoặc trên 95%, cấu hình được) |
| Exam summary | Điểm trung bình, trung vị, độ lệch chuẩn, phổ điểm, tỷ lệ đạt |

- Giảng viên chủ động *Publish results*; trước đó sinh viên không thấy gì.
- Cổng sinh viên: danh sách kỳ thi đã công bố; điểm; chi tiết từng câu (đáp án của mình, và đáp án đúng nếu giảng viên bật tùy chọn); ảnh phiếu của mình khi còn thời hạn lưu; gửi yêu cầu phúc khảo kèm ghi chú.
- Phúc khảo có trạng thái Open → In review → Resolved (kèm ghi chú). Nếu phải sửa điểm thì thực hiện qua màn hình review hoặc đính chính.
- Ảnh scan xóa tự động sau 4 tháng kể từ ngày tải lên; bản ghi kết quả giữ nguyên, ảnh hiển thị "đã hết hạn lưu".

*Tiêu chí nghiệm thu*

- Phiếu sinh ra, được vẽ lại thành ảnh tổng hợp có nhiễu nhẹ, được đọc đúng 100% các ô.
- Trên bộ ảnh điện thoại thật ở điều kiện chụp bình thường, đạt các chỉ số ở mục 1.
- Mọi phiếu có ô mờ hoặc hai ô tô trong câu một đáp án đều nằm trong hàng review, không có phiếu nào được chấm lặng lẽ.
- Sửa tay một câu trong màn hình review làm điểm cập nhật đúng trong Excel xuất ra.

## 7. Mô hình dữ liệu

Thiết kế xoay quanh ba điều bất biến: câu hỏi có revision, đề đã chốt chứa bản chụp nội dung, và điểm luôn tính lại được từ đáp án đã lưu. Khóa chính dùng UUID; mọi bảng có `created_at`, `updated_at`.

**7.1 Thực thể chính**

| Nhóm | Thực thể | Trường và quan hệ chính |
| --- | --- | --- |
| Tổ chức | Department, Course, Module, CLO | Course thuộc Department; Module và CLO thuộc Course; Module có `position` |
| Người dùng | User, CourseAssignment | User có `role` (admin, hod, lecturer, student) và `department_id`; CourseAssignment nối giảng viên với môn |
| Câu hỏi | Question, QuestionRevision, QuestionOption | Question giữ `code`, `module_id`, `status`, `current_revision_id`. Revision giữ stem, loại, độ khó, giải thích, `lock_option_order`, nguồn (manual, ai, import). Option thuộc revision: nội dung, `is_correct`, `position` |
| Phân loại | Tag, QuestionTag, QuestionCLO | Nhiều-nhiều với Question |
| Duyệt | ReviewAction | Question hoặc Exam, người duyệt, kết quả, lý do |
| AI | GenerationBatch, SourceDocument | Batch giữ tham số, provider, model, phiên bản prompt, token, trạng thái job; SourceDocument giữ file đã upload và văn bản trích xuất |
| Import | ImportJob, ImportRowResult | Loại (câu hỏi, roster, đề), trạng thái dry-run hoặc đã áp dụng, lỗi từng dòng |
| Đề thi | Exam, ExamItem, BlueprintRule | Exam giữ môn, cấu hình, `status` (draft, locked), `library_status` (private, pending, shared), seed, layout JSON. ExamItem là câu được chọn (tham chiếu revision). BlueprintRule là dòng cấu hình random: module, độ khó, số câu |
| Mã đề | ExamVersion, ExamVersionItem | Version có `code` (101…) và seed. VersionItem có vị trí, `revision_id`, thứ tự lựa chọn đã xáo. Hai bảng bất biến sau khi chốt |
| Kỳ thi | ExamSession, Enrollment | Session nối Exam với roster và ngày thi; Enrollment nối sinh viên với session |
| Chấm bài | ScanImage, Submission, SubmissionAnswer, GradingRun | ScanImage giữ đường dẫn file, `uploaded_at`, `expires_at`, kết quả đọc thô (tỷ lệ tô từng ô). Submission giữ sinh viên, mã đề, trạng thái (auto, needs\_review, confirmed, invalid), điểm. SubmissionAnswer giữ các lựa chọn đã chọn và đúng/sai |
| Đính chính | ExamCorrection | Câu bị đính chính, loại (đổi đáp án, thêm đáp án, hủy câu), lý do, người làm |
| Phúc khảo | ReviewRequest | Submission, sinh viên, ghi chú, trạng thái, ghi chú xử lý |
| Hệ thống | AuditLog | Người làm, hành động, đối tượng, giá trị trước và sau |

**7.2 Vòng đời trạng thái**

| Đối tượng | Trạng thái |
| --- | --- |
| Question | draft → pending → approved hoặc rejected; rejected sửa xong về draft; approved → archived |
| Exam | draft → locked (không quay lại; muốn sửa thì clone) |
| Exam, thư viện chung | private → pending → shared |
| Submission | auto hoặc needs\_review → confirmed; hoặc invalid |
| ReviewRequest | open → in\_review → resolved |
| Job (AI, import, scan) | queued → running → done, failed hoặc cancelled |

**7.3 Quy tắc dữ liệu cần giữ**

- Revision, ExamVersionItem và layout JSON của đề đã chốt không bao giờ bị cập nhật hoặc xóa.
- Điểm của Submission luôn tính lại được từ SubmissionAnswer, thứ tự lựa chọn của mã đề và ExamCorrection. Không lưu điểm như nguồn sự thật duy nhất.
- Đáp án sinh viên lưu theo `option_id` gốc của revision, không lưu chữ cái, để việc xáo không làm sai khi chấm lại hoặc thống kê.
- Job xóa ảnh theo `expires_at` chỉ xóa file và đánh dấu bản ghi, không xóa Submission.

## 8. Kiến trúc và công nghệ

Một monolith FastAPI cộng worker nền, dùng chung mã nguồn; tách thành các module rõ ràng để sau này tách dịch vụ nếu cần.

**8.1 Kiến trúc tổng thể**

Trình duyệt (máy giảng viên, điện thoại, máy sinh viên) gọi API; tác vụ nặng như gọi AI, chấm ảnh, xuất file đi qua hàng đợi sang worker.

&#91;embedded content: kiến trúc tổng thể · 7 thành phần\]

Mọi tác vụ nặng chạy ở worker; chỉ worker gọi nhà cung cấp AI, và chỉ qua `LLMProvider`.

**8.2 Công nghệ đề xuất**

| Lớp                    | Lựa chọn                                          | Ghi chú                                               |
| ---------------------- | ------------------------------------------------- | ----------------------------------------------------- |
| API                    | Python 3.12, FastAPI, Pydantic v2                 | OpenAPI tự sinh                                       |
| ORM, migration         | SQLAlchemy 2.0, Alembic                           |                                                       |
| CSDL                   | PostgreSQL 16                                     | Chạy bằng Docker Compose                              |
| Hàng đợi               | Redis + RQ                                        | Chấm ảnh dùng CPU nặng nên cần worker theo tiến trình |
| Frontend               | React, Vite, TypeScript, TanStack Query, Tailwind | Client API sinh từ OpenAPI                            |
| Xác thực               | JWT trong cookie httpOnly, băm mật khẩu argon2    | Thay bằng SSO ở giai đoạn sau                         |
| Xử lý ảnh, OMR         | OpenCV (aruco, QR), NumPy, Pillow                 |                                                       |
| Sinh phiếu PDF         | ReportLab                                         | Layout engine dùng chung với bộ đọc                   |
| Word, Excel            | python-docx, openpyxl                             |                                                       |
| Trích văn bản tài liệu | pypdf hoặc pdfplumber, python-docx, python-pptx   |                                                       |
| So khớp câu trùng      | rapidfuzz                                         | Nâng cấp embedding sau                                |
| Kiểm thử               | pytest, Playwright (e2e)                          |                                                       |
| Chất lượng mã          | ruff, mypy, eslint, pre-commit                    |                                                       |

**8.3 Trừu tượng hóa AI provider**

Toàn bộ mã nghiệp vụ chỉ gọi giao diện bên dưới; việc chọn provider và model nằm trong cấu hình môi trường (`AI_PROVIDER`, `AI_MODEL`, khóa API riêng cho từng provider). Prompt lưu thành file có phiên bản trong repo, không nhúng cứng trong mã.

```python
class LLMProvider(Protocol):
    name: str

    def generate_structured(
        self,
        *,
        system: str,
        messages: list[Message],
        schema: type[BaseModel],
        max_retries: int = 2,
    ) -> StructuredResult:
        """Return an object validated against `schema`, plus token usage."""
```

- Triển khai ban đầu: provider Anthropic và provider `fake` (trả dữ liệu cố định để test). Thêm provider khác chỉ cần một lớp mới và một dòng đăng ký.
- Tài liệu dài được cắt thành các đoạn; mỗi đoạn sinh một phần số câu, rồi gộp và loại trùng.
- Đề thi và tài liệu giảng dạy là dữ liệu nhạy cảm: khi deploy thật cần quyết định có gửi ra provider bên ngoài hay dùng mô hình chạy nội bộ (mục 11).

**8.4 Lưu trữ file và xử lý nền**

- Lớp `StorageBackend` (bản đầu dùng thư mục cục bộ, sau chuyển S3 hoặc MinIO). Ảnh scan được mã hóa lại JPEG, cạnh dài tối đa 2.480 px, chất lượng 85 để giảm dung lượng.
- Job nền: sinh câu hỏi AI, import, chấm ảnh, xuất gói đề, dọn ảnh hết hạn (chạy mỗi đêm). Job idempotent, thử lại có giới hạn, trạng thái đọc qua API.
- Số worker chấm ảnh mặc định 4, cấu hình được.

**8.5 Môi trường**

- Giai đoạn đầu: `docker compose up` chạy cả postgres, redis, api, worker và web trên máy bạn.
- Khi deploy: reverse proxy HTTPS (bắt buộc cho camera trực tiếp), sao lưu PostgreSQL và thư mục ảnh, quản lý khóa API bằng biến môi trường hoặc secret store.

## 9. Phi chức năng, bảo mật và rủi ro

**9.1 Yêu cầu phi chức năng**

| Nhóm | Yêu cầu |
| --- | --- |
| Hiệu năng | Chấm ≤ 5 giây/phiếu; 1.000 phiếu ≤ 30 phút với 4 worker; trang danh sách câu hỏi phản hồi dưới 1 giây với 5.000 câu hỏi mỗi môn |
| Độ chính xác | Theo các chỉ số ở mục 1; mọi ca không chắc chắn phải bị gắn cờ |
| Độ tin cậy | Job nền thử lại có giới hạn; tải ảnh lên không mất khi job lỗi; chấm lại được từ dữ liệu đã lưu |
| Khả năng kiểm toán | Audit log cho duyệt, chốt, đính chính, chấm lại, sửa tay, đổi vai trò, chạy AI |
| Bảo mật | RBAC kiểm tra ở backend cho mọi endpoint; giới hạn truy cập theo bộ môn và môn; băm mật khẩu argon2; giới hạn số lần đăng nhập sai; file upload kiểm tra loại và dung lượng |
| Quyền riêng tư | Sinh viên chỉ thấy bài của mình; ảnh phiếu và điểm không công khai qua URL đoán được (dùng URL có chữ ký, hết hạn ngắn); xóa ảnh sau 4 tháng |
| Khả năng mở rộng | Lưu trữ file và AI provider qua giao diện trừu tượng; có thể thêm worker khi tải tăng |
| Khả năng kiểm thử | Nhà cung cấp AI giả và bộ ảnh phiếu tổng hợp để chạy test không cần mạng |
| Giao diện | Tiếng Anh; dùng được trên laptop và điện thoại (trang Scan và Review ưu tiên điện thoại và máy tính bảng) |
| Khả năng truy cập | Giao diện dùng được bằng bàn phím cho màn hình review |

**9.2 Rủi ro và cách giảm thiểu**

| Rủi ro | Mức | Giảm thiểu |
| --- | --- | --- |
| Đọc ô tô sai khi ảnh chụp kém (bóng, mờ, nhăn, nghiêng) | Cao | Làm *spike* OMR sớm (mục 10, bước S1) trên ảnh tổng hợp và ảnh thật; ngưỡng hai tầng để gắn cờ ca mờ; hướng dẫn chụp trong ứng dụng; kiểm tra chất lượng ảnh trước khi nhận |
| Camera trực tiếp không chạy trên điện thoại do thiếu HTTPS khi dev | Trung bình | Dùng chứng chỉ HTTPS cục bộ hoặc đường hầm; có nút gọi camera hệ thống làm dự phòng |
| AI sinh câu sai đáp án hoặc bịa nội dung | Cao | Không có chế độ tự duyệt; dẫn nguồn khi dùng tài liệu; validate schema; HoD duyệt trước khi vào thư viện chung |
| Câu trùng làm đề lặp nội dung | Trung bình | Kiểm tra trùng ở mọi cửa vào; ngưỡng cấu hình được |
| Lộ đề thi hoặc tài liệu qua provider AI bên ngoài | Cao | Provider chọn bằng cấu hình; cho phép mô hình chạy nội bộ; chốt chính sách trước khi deploy |
| Sai đáp án sau khi đã chấm hàng trăm bài | Trung bình | Luồng đính chính và chấm lại có audit, không cần scan lại |
| Mã SV của trường có chữ cái | Trung bình | Chốt định dạng mã SV sớm (mục 11); nếu cần, đổi sang lưới chữ hoặc mã vạch in sẵn |
| Phạm vi lớn, dễ trượt tiến độ | Trung bình | Chia mốc nhỏ có tiêu chí hoàn thành; chốt PRD là nguồn sự thật; ghi mọi thay đổi vào mục 11 |
| Dung lượng ảnh lớn | Thấp | Mã hóa lại JPEG, dọn tự động sau 4 tháng |

## 10. Hướng dẫn triển khai với Claude Code

Chia dự án thành 10 mốc nhỏ, mỗi mốc có prompt dán sẵn và tiêu chí hoàn thành. Phần rủi ro nhất (đọc phiếu) được làm thành một spike độc lập ngay sau mốc nền để biết sớm có khả thi không.

**10.1 Cách làm việc**

1. Tạo repo trống. Xuất tài liệu này sang Markdown và lưu thành `docs/PRD.md`; tạo `CLAUDE.md` ở thư mục gốc với nội dung ở mục 10.3.
2. Mỗi mốc: mở một phiên Claude Code mới, bật plan mode, dán prompt của mốc, đọc kế hoạch Claude đề xuất rồi mới cho chạy.
3. Commit nhỏ, thường xuyên. Chạy test và lint trước khi chuyển mốc; kiểm tra từng tiêu chí hoàn thành.
4. Nếu Claude Code phát hiện PRD mâu thuẫn hoặc thiếu, yêu cầu nó dừng và hỏi bạn; sửa PRD trước rồi mới sửa mã.
5. Giữ mỗi mốc trong khoảng một đến vài ngày làm việc. Mốc nào dài hơn thì tách tiếp.

**10.2 Cấu trúc repo**

```text
exam-platform/
├── CLAUDE.md
├── docker-compose.yml
├── .env.example
├── docs/
│   ├── PRD.md
│   └── decisions/              # ADR ngắn cho mỗi quyết định lớn
├── backend/
│   ├── pyproject.toml
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/               # config, security, deps, audit
│   │   ├── models/             # SQLAlchemy
│   │   ├── schemas/            # Pydantic
│   │   ├── api/                # routers theo domain, mỏng
│   │   ├── services/           # nghiệp vụ: questions, exams, grading
│   │   ├── ai/                 # providers/, prompts/, ingestion/
│   │   ├── omr/                # layout, sheet_pdf, reader (không phụ thuộc DB)
│   │   ├── exporters/          # docx_exam, docx_key, xlsx_results
│   │   ├── importers/          # excel_questions, excel_roster, excel_exam
│   │   ├── dedupe/
│   │   ├── storage/
│   │   └── jobs/               # tác vụ RQ
│   └── tests/
│       ├── unit/
│       ├── api/
│       └── omr/                # ảnh phiếu tổng hợp và biến thể có nhiễu
├── frontend/
│   ├── src/                    # pages, components, api, hooks, lib
│   └── e2e/
└── tools/                      # seed data, tạo phiếu thử
```

**10.3 Nội dung `CLAUDE.md`**

```markdown
# Exam Platform

AI-assisted multiple-choice exam platform: question bank, exam builder,
Word/PDF export, and scan-based grading of paper answer sheets.

Read docs/PRD.md before starting any task. It is the source of truth.
If a task conflicts with the PRD, stop and ask before changing anything.

## Stack and commands
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Redis + RQ, OpenCV.
- Frontend: React, Vite, TypeScript, TanStack Query, Tailwind.
- Start services: `docker compose up -d db redis`
- Backend: `cd backend && uv run pytest`, `uv run ruff check .`, `uv run mypy app`, `uv run alembic upgrade head`
- Frontend: `cd frontend && pnpm dev`, `pnpm test`, `pnpm lint`, `pnpm e2e`

## Non-negotiable rules
1. Locked exams, question revisions, exam version items and the sheet layout JSON are immutable.
2. A submission score is always recomputable from stored answers, version option order and corrections.
3. Student answers are stored by option_id, never by letter.
4. OMR never guesses silently. Any ambiguity sets the submission to needs_review.
5. The layout engine in app/omr is the single source of truth for both the answer sheet PDF and the reader.
6. All LLM calls go through LLMProvider. No provider SDK imports outside app/ai/providers.
7. Authorization and department scoping are enforced in backend dependencies. Every endpoint has an authz test.
8. State-changing actions listed in PRD section 3 write an AuditLog row.
9. UI strings and question content are in English.

## Conventions
- Type hints everywhere; mypy strict for app/omr and app/services.
- Routers stay thin; business logic lives in services/.
- Database changes only through Alembic migrations.
- Tests never use the network. AI is tested with the fake provider.
- Do not add a dependency without saying why.
- Small commits with clear messages. Run lint and tests before saying a task is done.

## Workflow
- Work on one milestone at a time (PRD section 10). Start with a plan listing the files you will touch.
- Definition of done: tests pass, lint is clean, the milestone acceptance criteria are verified, docs updated.
- Record notable decisions in docs/decisions/NNN-title.md.
```

**10.4 Lộ trình tổng quan**

| Mốc | Nội dung | Phụ thuộc |
| --- | --- | --- |
| M0 | Nền tảng repo, Docker Compose, khung API và web, CI | — |
| M1 | Đăng nhập, vai trò, bộ môn, môn, module, CLO, roster | M0 |
| M2 | Ngân hàng câu hỏi, revision, luồng duyệt | M1 |
| S1 | Spike OMR: layout engine, phiếu PDF, bộ đọc, bộ test ảnh | M0, làm song song với M1–M2 |
| M3 | Import Excel (câu hỏi, đề) và phát hiện câu trùng | M2 |
| M4 | Sinh câu hỏi bằng AI | M2, M3 |
| M5 | Dựng đề 3 cách, chốt, mã đề, clone | M2, M3 |
| M6 | Xuất Word, đáp án, phiếu PDF | M5, S1 |
| M7 | Scan trong ứng dụng, xử lý nền, màn hình review | M6, S1, M1 |
| M8 | Kết quả, báo cáo Excel, đính chính, chấm lại, cổng sinh viên, phúc khảo | M7 |
| M9 | Hoàn thiện: dọn ảnh, audit, hiệu năng, e2e, tài liệu | M0–M8 |

**10.5 Các mốc chi tiết**

Mỗi prompt giả định `CLAUDE.md` và `docs/PRD.md` đã có trong repo.

**M0. Nền tảng repo**

```text
Read CLAUDE.md and docs/PRD.md (sections 2, 8, 10). Set up the project skeleton for milestone M0:
- docker-compose.yml with postgres 16, redis, api, worker and web services, plus .env.example.
- backend: FastAPI app with a /health endpoint, settings via pydantic-settings, SQLAlchemy 2.0 base and Alembic configured, an RQ worker with one sample job, structured logging, pytest + ruff + mypy configured with uv.
- frontend: Vite + React + TypeScript app with routing, TanStack Query, Tailwind, and an API client generated from the backend OpenAPI schema (a script in package.json).
- CI (GitHub Actions or a Makefile) running lint and tests for backend and frontend.
- docs/decisions/001-stack.md recording the stack choices from PRD section 8.
Do not implement business features yet. Show me your plan first.
```

Hoàn thành khi: `docker compose up` chạy đủ dịch vụ; `/health` trả OK; mỗi phía có ít nhất một test chạy xanh trong CI; sinh được API client từ OpenAPI.

**M1. Đăng nhập, vai trò, dữ liệu nền**

```text
Implement milestone M1 (PRD sections 3, 4.1, 7). Read those sections first.
- Models and Alembic migrations: Department, User, Course, Module (ordered), CLO, CourseAssignment, AuditLog.
- Auth: email + password login, JWT in an httpOnly cookie, argon2 hashing, login rate limiting, change password, admin password reset, forced password change on first login.
- RBAC as FastAPI dependencies with department and course scoping exactly as the matrix in PRD section 3.
- UI for Admin and HoD: manage departments, courses, modules (drag to reorder), CLOs, assign lecturers to courses.
- Student roster import from Excel (student_code, full_name, email, class): dry-run first, per-row errors, then apply and create student accounts.
- A seed script: 2 departments, 3 courses with modules, one user per role.
- An audit helper used for role changes and assignments.
Write authz tests for every endpoint (allowed and forbidden cases per role). Plan first.
```

Hoàn thành khi: bốn vai trò đăng nhập được; HoD bộ môn A không thấy môn của bộ môn B (có test); import roster có dòng lỗi thì báo đúng dòng; đổi vai trò tạo bản ghi audit.

**M2. Ngân hàng câu hỏi và luồng duyệt**

```text
Implement milestone M2 (PRD sections 4.2, 4.3, 7). Read them first.
- Models: Question, QuestionRevision, QuestionOption, Tag, QuestionCLO. Types: single, multiple, true_false, with the validation rules from FR-QB-1 (option counts, number of correct answers, fixed True/False options).
- Generate unique question codes like ISD201-M03-0042 at creation.
- Every edit creates a new immutable revision. Status workflow draft -> pending -> approved or rejected (rejection needs a reason). Editing an approved question creates a pending revision while the approved revision stays effective.
- API and UI: question list with filters (course, module, difficulty, CLO, tag, status, author, source) and full-text search using PostgreSQL; editor with 2-6 dynamic options, correct answer selection, difficulty, CLOs, tags, explanation and lock-option-order flag; revision history view; HoD review queue with batch approve and reject; soft archive.
- Block hard delete of questions that will be used by locked exams (add a stub check to be completed in M5).
Write tests for each acceptance criterion in PRD 4.3 and a seed of 5,000 questions to measure list latency. Plan first.
```

Hoàn thành khi: các tiêu chí nghiệm thu ở mục 4.3 có test xanh; danh sách lọc trên 5.000 câu phản hồi dưới 1 giây; giao diện sửa, gửi duyệt, duyệt hoạt động trọn vòng.

**S1. Spike OMR (song song với M1–M2)**

Đây là cổng quyết định của cả dự án. Nếu spike không đạt, phải sửa thiết kế phiếu trước khi làm M6 và M7.

```text
Read CLAUDE.md and PRD sections 6 and 7.3. Build the OMR core as a standalone library in backend/app/omr with no database dependency. This is a spike: prove accuracy before any UI work.

1. layout.py: a parametric layout engine. Inputs: number of questions (<= 60), max options per question (<= 6), student code digits (default 8), version code digits (3). Output: a serializable Layout (dataclass to JSON) with mm coordinates of the 4 ArUco corner markers, the QR area, every bubble (grid id, row, col, center, radius) and per-question option counts (unused bubbles flagged).
2. sheet_pdf.py: render a Layout to an A4 PDF with ReportLab. QR encodes exam id, layout version and checksum. Include a title, fill instructions, and handwritten name and signature boxes.
3. reader.py: given an image (numpy array) and a Layout: detect the 4 ArUco markers, warp to a canonical size, decode the QR, measure the fill ratio of every bubble, classify each as filled, empty or ambiguous using two thresholds with per-sheet calibration, decode student code and version code, and return a ReadResult with raw fill ratios and flags as listed in PRD 6.4.
4. tools/make_test_sheets.py: generate synthetic filled sheets (random answers including multi-mark, faint marks and blank questions) and degrade them: rotation up to 10 degrees, perspective warp, gaussian blur, uneven lighting and shadow, noise, JPEG compression.
5. tests/omr: assert 100% accuracy on clean synthetic sheets; report accuracy and the false-confident rate (wrong but not flagged) per degradation type as a table.

Write docs/omr-notes.md with the measured results and the failure modes you found. Do not tune thresholds just to pass a test; report honestly.
```

Hoàn thành khi:

- In phiếu ra A4 đúng tỷ lệ 100% và đo thước thấy khoảng cách ô khớp layout.
- Ảnh tổng hợp sạch đọc đúng 100%.
- Tỷ lệ đọc sai mà không gắn cờ trên bộ ảnh bị làm xấu ≤ 0,1%, hoặc có tài liệu giải thích khoảng cách còn lại.
- Thử thật: in một phiếu, tô bằng bút chì, chụp 10 ảnh bằng điện thoại ở điều kiện khác nhau, chạy bộ đọc và ghi kết quả vào `docs/omr-notes.md`.

**M3. Import Excel và phát hiện câu trùng**

```text
Implement milestone M3 (PRD sections 4.5, 5.1 first row, 7). Read them first.
- importers/excel_questions.py: parse the question template (columns listed in PRD 4.5), validate every row (course and module exist, type rules, correct answer format like B or A,C or TRUE, option counts), return per-row errors. Provide a downloadable template file and a downloadable error report.
- Import flow as an ImportJob: upload -> dry-run result with errors and duplicate warnings -> user confirms -> create questions as draft (option to submit for review).
- dedupe/: normalize text (lowercase, strip punctuation and extra spaces), exact-match on normalized stem plus option set, and fuzzy match with rapidfuzz (default threshold 0.85 for stem and for option set, configurable). Compare within the same course. Expose it as a service used by manual save, import, and later AI generation. Define an EmbeddingProvider interface but do not implement it.
- UI: import wizard with error table and duplicate review (skip, keep anyway, replace with new revision); duplicate warning in the question editor on save.
- importers/excel_exam.py (parse only for now): a single question_code column; return resolved questions or per-row errors. It is wired into the exam builder in M5.
Tests: 100-row file with 3 bad rows reports exactly those 3; a question differing only by punctuation or case is flagged as duplicate. Plan first.
```

Hoàn thành khi: hai tiêu chí nghiệm thu ở mục 4.5 có test xanh; wizard import chạy trọn vòng với file mẫu.

**M4. Sinh câu hỏi bằng AI**

```text
Implement milestone M4 (PRD sections 4.4, 8.3, 7). Read them first.
- ai/providers: LLMProvider protocol (generate_structured), an Anthropic implementation, and a fake provider returning deterministic data for tests. Provider and model chosen by env vars. No provider SDK imports outside this package.
- ai/prompts: versioned prompt files (markdown) for question generation. Output must validate against a Pydantic schema: stem, type, options with is_correct, explanation, difficulty, suggested CLOs and tags, source reference. Retry up to 2 times on invalid output.
- ai/ingestion: extract text from PDF, DOCX, PPTX, TXT (limits: 20 MB per file, 5 files per request), keep page or slide references, chunk long documents; generate per chunk and merge.
- Generation as a background RQ job with progress, cancel, and a GenerationBatch record storing parameters, provider, model, prompt version, token usage, and who ran it.
- Parameters per FR-AI-2: course and modules, source (prompt, documents, or both), number of questions (1-50), type mix, options per question, difficulty distribution, target CLOs, language (default English), extra instructions.
- Auto-set lock_option_order when an option says all of the above or none of the above.
- Run dedupe from M3 on results before showing them.
- UI: generation form, progress view, batch review screen (edit inline, discard, regenerate a single question, submit selected to review). No auto-approve anywhere.
Tests use the fake provider only. Plan first.
```

Hoàn thành khi: sinh được batch 20 câu bằng provider giả trong test và bằng provider thật khi có khóa API; câu từ tài liệu có tham chiếu nguồn; đổi `AI_PROVIDER` sang provider khác không cần sửa mã nghiệp vụ; câu lỗi schema được thử lại và không làm hỏng batch.

**M5. Dựng đề, chốt, mã đề, clone**

```text
Implement milestone M5 (PRD sections 5.1-5.4, 7). Read them first.
- Models: Exam, ExamItem, BlueprintRule, ExamVersion, ExamVersionItem, ExamCorrection (table only for now).
- Three build modes: (a) Excel import by question_code using the M3 parser; (b) manual selection from the bank with filters, add, remove, reorder; (c) random generation from blueprint rules (module x difficulty x count) with a stored seed, shortage errors naming the module and difficulty, preview, reroll one question or all.
- Eligibility: approved questions plus the author's own questions that are not rejected. Max 60 questions per exam.
- Config: title, course, exam code, duration, instructions, number of versions (default 4, codes 101-104, max 10), shuffle questions and options toggles, points per question = 10 / number of questions, pass mark (default 5.0).
- Finalize: in one transaction freeze the exam, snapshot each question revision into ExamVersionItem rows, generate versions from seeds (respect lock_option_order), and store the layout JSON from app/omr for the exam. After this the exam is immutable. Exams are cloneable into a new draft.
- Complete the stub from M2: questions used by locked exams cannot be hard-deleted.
- HoD flow to approve a locked exam into the shared library (library_status).
Tests: per-group counts for random generation, same question set but different order between versions, edited source question does not change a locked exam, immutability enforced at the service layer. Plan first.
```

Hoàn thành khi: các tiêu chí nghiệm thu ở mục 5 liên quan đến dựng đề và chốt có test xanh; chốt đề lặp lại với cùng seed cho cùng kết quả; giao diện dựng đề dùng được cả ba cách.

**M6. Xuất Word, đáp án, phiếu PDF**

```text
Implement milestone M6 (PRD section 5.5 and 6.1). Read them first.
- exporters/docx_exam.py: one .docx per exam version using python-docx. Prominent version code at the top of page 1, title, duration, instructions, questions numbered in version order, options lettered A-F, a Select all that apply line for multiple-answer questions. No header or footer.
- exporters/docx_key.py: one .docx for the lecturer with an answer table per version and a mapping table from original question number to number in each version.
- Answer sheet PDF generated from the exam's stored layout JSON using app/omr/sheet_pdf.py. One sheet for all versions.
- A background job that builds a ZIP with all files and a download endpoint; UI button on locked exams.
- Tests: the answer key of each version matches the order and options in that version's docx (parse the docx back and compare); export of a locked exam is byte-stable in content after the source questions are edited.
Plan first.
```

Hoàn thành khi: mở file Word thấy đúng định dạng; bảng đáp án từng mã khớp nội dung đề; phiếu PDF in ra khớp layout đã kiểm ở S1.

**M7. Scan trong ứng dụng, xử lý nền, màn hình review**

```text
Implement milestone M7 (PRD sections 6.2-6.5, 7, 8.4). Read them first. Reuse app/omr from S1 without changing its public interface unless you explain why.
- Models: ExamSession, Enrollment, ScanImage, Submission, SubmissionAnswer, GradingRun. Create a session from a locked exam plus a roster and a date.
- Upload endpoints for images (JPG, PNG) and multi-page PDFs. Re-encode stored images to JPEG, max 2480 px long edge, quality 85; store raw read results (fill ratios per bubble) with each ScanImage and set expires_at to 4 months after upload.
- RQ job per image: read with app/omr, map answers to option_id via the exam version's option order, grade, apply every flag rule in PRD 6.4, set status auto or needs_review. Student code lookup against the session roster. Duplicate student detection within a session.
- Scan page in the web app: live camera with an alignment frame and continuous capture, plus a Take photo fallback that uses the system camera, plus drag-and-drop upload. Queue view with per-image status updating by polling.
- Review screen: queue of needs_review submissions with filters by reason and keyboard shortcuts; warped image with overlays for filled, ambiguous and error bubbles; click to change an answer; roster search to fix the student code; change version; mark invalid; Confirm. Every manual edit writes an audit row and recomputes the score.
- Local HTTPS for phone testing: document mkcert (or a tunnel) setup in docs/dev-https.md.
Tests: end-to-end test with synthetic sheets covering every flag in PRD 6.4; review edits change the score; a needs_review sheet is never counted as auto. Plan first.
```

Hoàn thành khi: chụp bằng điện thoại trong ứng dụng cho ra kết quả; mọi tình huống ở bảng 6.4 có test; không có phiếu nào ở trạng thái auto khi có ô mờ hoặc hai ô tô trong câu một đáp án.

**M8. Kết quả, báo cáo, đính chính, cổng sinh viên**

```text
Implement milestone M8 (PRD sections 5.4, 6.6, 7). Read them first.
- Result views per session: table of submissions with status filters, score distribution, mean, median, standard deviation, pass rate.
- Excel export with the four sheets in PRD 6.6 (Results, Answers, Question stats, Exam summary) using openpyxl; Answers uses original question order and original option letters.
- Corrections: ExamCorrection with the three types (change correct answer, accept additional answer, void question), mandatory reason, audit log, applied to all versions; regrade job recomputes every submission from stored answers, keeps GradingRun history and shows before and after scores. Flag the source question in the bank for review.
- Publish results action; student portal: list of published exams, score, per-question detail (correct answers only if the lecturer enabled it), own scan image while it has not expired.
- Review requests: student submits with a note; lecturer and HoD see a list, move it through open, in_review, resolved with a note.
Tests: regrade after a correction changes scores as expected and keeps history; students cannot see unpublished results or other students' data; Excel numbers match the database. Plan first.
```

Hoàn thành khi: sửa đáp án một câu rồi chấm lại đổi đúng điểm những bài bị ảnh hưởng; sinh viên đăng nhập xem được đúng bài của mình sau khi công bố; file Excel khớp dữ liệu trong hệ thống.

**M9. Hoàn thiện**

```text
Implement milestone M9 (PRD sections 8.4, 9). Read them first.
- Nightly job deleting expired scan images (file and path only, keep submissions) with a log, and UI text for expired images.
- Complete audit coverage: verify every state-changing action listed in PRD section 3 writes an AuditLog row; add an audit viewer for Admin and HoD.
- Performance: seed 1,000 synthetic sheets for one session and measure grading throughput with 4 workers; seed 5,000 questions per course and measure list latency. Fix hotspots and record numbers in docs/performance.md.
- Playwright end-to-end scenarios: lecturer builds a random exam, finalizes, exports; uploads synthetic scans; reviews flagged sheets; publishes results; student logs in and sees the score.
- Security pass: signed short-lived URLs for scan images, upload validation, rate limits, dependency audit.
- Write docs/runbook.md: setup, env vars, backup and restore, switching AI provider, deploying behind HTTPS.
Plan first.
```

Hoàn thành khi: số đo hiệu năng đạt mục 9.1; kịch bản end-to-end chạy xanh; runbook đủ để người khác dựng lại hệ thống từ đầu.

## 11. Điểm còn mở cần bạn xác nhận

Nếu bạn không trả lời, Claude Code sẽ dùng cột *Mặc định*. Câu 1 và câu 2 nên chốt trước khi làm S1 vì ảnh hưởng thiết kế phiếu.

| # | Câu hỏi | Mặc định nếu không trả lời |
| --- | --- | --- |
| 1 | Mã sinh viên của trường chỉ gồm chữ số hay có cả chữ cái (ví dụ HE170001)? | Chỉ chữ số, 8 ký tự |
| 2 | Phiếu trả lời xuất PDF (không phải Word) có chấp nhận được không? | PDF, vì cần tọa độ chính xác để scan |
| 3 | Tối đa 60 câu mỗi đề có đủ cho các kỳ thi thực tế không? | 60 câu, một trang phiếu |
| 4 | Câu nhiều đáp án chấm tất cả hoặc không có đúng ý bạn không, hay cần chấm từng phần? | Tất cả hoặc không |
| 5 | File Excel dựng đề chỉ chứa mã câu hỏi, còn câu mới nhập bằng template import câu hỏi, có đúng ý bạn không? | Đúng như mô tả ở D8 |
| 6 | Giảng viên có được dựng đề bằng câu của chính mình khi chưa được HoD duyệt không? | Được (trừ câu bị Rejected) |
| 7 | Khi chạy thật, đề thi và tài liệu giảng dạy có được gửi tới nhà cung cấp AI bên ngoài không, hay phải dùng mô hình chạy nội bộ? | Gửi được, vì đang là bản thử nghiệm |
| 8 | Tài khoản sinh viên tạo thế nào: mật khẩu khởi tạo rồi đổi lần đầu, hay cần SSO của trường? | Mật khẩu khởi tạo, bắt buộc đổi lần đầu |
| 9 | Con số 1.000 sinh viên là tổng số sinh viên trong hệ thống hay số bài mỗi đợt thi? | Số bài của một đợt thi (kịch bản nặng hơn) |
| 10 | Điểm đạt là bao nhiêu và có thay đổi theo môn không? | 5,0 cho mọi môn, cấu hình theo từng đề |
| 11 | Đính chính đáp án có cần HoD duyệt trước khi chấm lại không? | Không cần, chỉ ghi audit và báo HoD |
| 12 | Trường có muốn sinh viên thấy đáp án đúng sau khi công bố không? | Giảng viên bật hoặc tắt theo từng đề, mặc định tắt |
