# PRD: AI MCQ Exam Platform

Oct 17, 2026 · @NTKien

## 1. Tổng quan

Nền tảng web giúp giảng viên sinh ngân hàng câu hỏi trắc nghiệm bằng AI, dựng đề nhiều mã đề, in thi trên giấy và chấm tự động từ ảnh phiếu trả lời. Tài liệu này là PRD (mục 1–10); cách build cùng Claude Code nằm ở tài liệu Playbook riêng. Giao diện và nội dung câu hỏi dùng tiếng Anh; tài liệu này viết bằng tiếng Việt.

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
| D10 | Mã SV là số. Nếu mã của trường có chữ cái, cần đổi cách mã hóa (xem mục 10) | Lưới ô tô ký tự chữ làm phiếu rất dài |
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

| Lớp | Lựa chọn | Ghi chú |
| --- | --- | --- |
| API | Python 3.12, FastAPI, Pydantic v2 | OpenAPI tự sinh |
| ORM, migration | SQLAlchemy 2.0, Alembic |  |
| CSDL | PostgreSQL 16 | Chạy bằng Docker Compose |
| Hàng đợi | Redis + RQ | Chấm ảnh dùng CPU nặng nên cần worker theo tiến trình |
| Frontend | React, Vite, TypeScript, TanStack Query, Tailwind | Client API sinh từ OpenAPI |
| Xác thực | JWT trong cookie httpOnly, băm mật khẩu argon2 | Thay bằng SSO ở giai đoạn sau |
| Xử lý ảnh, OMR | OpenCV (aruco, QR), NumPy, Pillow |  |
| Sinh phiếu PDF | ReportLab | Layout engine dùng chung với bộ đọc |
| Word, Excel | python-docx, openpyxl |  |
| Trích văn bản tài liệu | pypdf hoặc pdfplumber, python-docx, python-pptx |  |
| So khớp câu trùng | rapidfuzz | Nâng cấp embedding sau |
| Kiểm thử | pytest, Playwright (e2e) |  |
| Chất lượng mã | ruff, mypy, eslint, pre-commit |  |

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
- Đề thi và tài liệu giảng dạy là dữ liệu nhạy cảm: khi deploy thật cần quyết định có gửi ra provider bên ngoài hay dùng mô hình chạy nội bộ (mục 10).

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
| Đọc ô tô sai khi ảnh chụp kém (bóng, mờ, nhăn, nghiêng) | Cao | Làm *spike* OMR sớm (Playbook, bước S1) trên ảnh tổng hợp và ảnh thật; ngưỡng hai tầng để gắn cờ ca mờ; hướng dẫn chụp trong ứng dụng; kiểm tra chất lượng ảnh trước khi nhận |
| Camera trực tiếp không chạy trên điện thoại do thiếu HTTPS khi dev | Trung bình | Dùng chứng chỉ HTTPS cục bộ hoặc đường hầm; có nút gọi camera hệ thống làm dự phòng |
| AI sinh câu sai đáp án hoặc bịa nội dung | Cao | Không có chế độ tự duyệt; dẫn nguồn khi dùng tài liệu; validate schema; HoD duyệt trước khi vào thư viện chung |
| Câu trùng làm đề lặp nội dung | Trung bình | Kiểm tra trùng ở mọi cửa vào; ngưỡng cấu hình được |
| Lộ đề thi hoặc tài liệu qua provider AI bên ngoài | Cao | Provider chọn bằng cấu hình; cho phép mô hình chạy nội bộ; chốt chính sách trước khi deploy |
| Sai đáp án sau khi đã chấm hàng trăm bài | Trung bình | Luồng đính chính và chấm lại có audit, không cần scan lại |
| Mã SV của trường có chữ cái | Trung bình | Chốt định dạng mã SV sớm (mục 10); nếu cần, đổi sang lưới chữ hoặc mã vạch in sẵn |
| Phạm vi lớn, dễ trượt tiến độ | Trung bình | Chia mốc nhỏ có tiêu chí hoàn thành; chốt PRD là nguồn sự thật; ghi mọi thay đổi vào mục 10 |
| Dung lượng ảnh lớn | Thấp | Mã hóa lại JPEG, dọn tự động sau 4 tháng |

## 10. Điểm còn mở cần bạn xác nhận

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
