# Playbook: Building the AI MCQ Exam Platform with Claude Code

Oct 17, 2026 · @NTKien

## 1. Chuẩn bị một lần

Làm xong phần này là bạn có một repo sạch, có PRD và `CLAUDE.md`, sẵn sàng bắt đầu mốc M0. Tài liệu này đi kèm PRD (tài liệu "PRD: AI MCQ Exam Platform"); các mốc và tiêu chí hoàn thành nằm ở Phụ lục C của tài liệu này.

**Bước 1.1. Cài công cụ**

| Công cụ | Dùng để | Kiểm tra |
| --- | --- | --- |
| Git | Quản lý mã nguồn, mỗi mốc một nhánh | `git --version` |
| PostgreSQL 16 | Cơ sở dữ liệu của hệ thống (giai đoạn đầu chưa dùng Docker và Redis) | `psql --version` |
| Python 3.12 và `uv` | Backend FastAPI | `uv --version` |
| Node.js LTS và `pnpm` | Frontend React | `pnpm --version` |
| Claude Code | Trợ lý viết mã trong terminal | Cài theo hướng dẫn chính thức trên docs.claude.com, rồi chạy `claude` trong thư mục repo |
| Khóa API của AI provider (Anthropic) | Chạy tính năng sinh câu hỏi ở M4 | Lưu trong file `.env`, không commit |

**Bước 1.1b. Cài PostgreSQL và tạo cơ sở dữ liệu**

Giai đoạn này chưa dùng Docker và Redis, nên PostgreSQL được cài trực tiếp trên Windows. Hàng đợi job của hệ thống cũng nằm trong PostgreSQL, nên bạn không cần cài thêm gì khác.

1. Tải trình cài đặt PostgreSQL 16 cho Windows từ trang chính thức postgresql.org (mục Download, Windows) và cài với các lựa chọn mặc định. Trình cài sẽ hỏi mật khẩu cho tài khoản `postgres`: hãy ghi lại, và giữ cổng mặc định 5432.
2. Mở "SQL Shell (psql)" trong Start Menu (hoặc thêm thư mục `bin` của PostgreSQL vào `PATH` để chạy `psql` trong cmd), đăng nhập bằng tài khoản `postgres`, rồi chạy các lệnh sau (đổi mật khẩu thành mật khẩu của riêng bạn):

```sql
CREATE USER quizai WITH PASSWORD 'doi-mat-khau-nay';
CREATE DATABASE quizai OWNER quizai;
CREATE DATABASE quizai_test OWNER quizai;
```

3. Sau M0, sao chép `.env.example` thành `.env` và điền thông tin kết nối vào đúng dòng của cơ sở dữ liệu (người dùng `quizai`, mật khẩu bạn vừa đặt, cổng 5432; cơ sở dữ liệu `quizai` cho chạy thường và `quizai_test` cho test). Không commit `.env`.

*Kiểm tra:* `psql --version` hiển thị phiên bản 16, và `psql -U quizai -d quizai -h localhost` đăng nhập được bằng mật khẩu vừa đặt.

Khi cần deploy hoặc chạy nhiều máy, Docker và Redis có thể thêm sau. Hệ thống đã thiết kế sẵn giao diện `JobQueue` để việc đổi sang Redis không phải sửa mã nghiệp vụ.

**Bước 1.2. Tạo repo**

```bash
mkdir exam-platform && cd exam-platform
git init -b main
mkdir -p docs/decisions
```

**Bước 1.3. Đưa PRD và `CLAUDE.md` vào repo**

1. Xuất tài liệu PRD sang Markdown và lưu thành `docs/PRD.md`.
2. Tạo `CLAUDE.md` ở thư mục gốc, dán nội dung ở Phụ lục A của tài liệu này, rồi lưu tài liệu này thành docs/PLAYBOOK.md.
3. Commit:

```bash
git add .
git commit -m "docs: add PRD, PLAYBOOK and CLAUDE.md"
```

**Bước 1.4. Chốt các điểm còn mở**

Câu 1 (mã sinh viên gồm chữ và số, dạng HE170001) và câu 2 (phiếu trả lời xuất PDF) ở mục 10 của PRD đã được chốt và ghi vào PRD. Nếu bạn đổi quyết định nào, hoặc muốn trả lời các câu còn lại ở mục 10, hãy sửa thẳng vào `docs/PRD.md` (mục 2, bảng B: các dòng D10 và D1 tương ứng). Claude Code đọc PRD để làm việc, nên PRD càng khớp quyết định thật càng ít phải sửa lại mã.

**Bước 1.5. Quy ước nhánh và quyền**

- Mỗi mốc một nhánh, ví dụ `git switch -c m0-foundation`. Chỉ gộp vào `main` khi đã kiểm đủ tiêu chí hoàn thành.
- Khi Claude Code xin quyền chạy lệnh, chỉ đồng ý với lệnh nằm trong repo (test, lint, migration). Từ chối lệnh xóa file ngoài repo hoặc gửi dữ liệu ra ngoài.
- Khóa API và mật khẩu chỉ nằm trong `.env`. Nhờ Claude Code kiểm tra `.gitignore` đã chặn `.env` trước commit đầu tiên của M0.

*Kiểm tra xong bước chuẩn bị:* `git log` có đúng một commit chứa `docs/PRD.md`, docs/PLAYBOOK.md và `CLAUDE.md`; mở `docs/PRD.md` đọc được đủ 10 mục.

**Bước 1.6. Kết nối repo với GitHub**

Làm bước này ngay sau commit đầu tiên ở bước 1.3, trước khi bắt đầu M0, để mã luôn có bản sao lưu và CI chạy được.

1. **Tạo repo trống trên GitHub.** Chọn *Private*. Đừng tick tạo README, `.gitignore` hay license, vì repo local đã có commit đầu và sẽ xung đột.
2. **Chọn một cách xác thực** (làm một lần trên máy):
   - *SSH (khuyên dùng):* tạo khóa, thêm khóa công khai vào GitHub (Settings, mục SSH and GPG keys), rồi kiểm tra.
   - *GitHub CLI:* chạy `gh auth login` và làm theo hướng dẫn; dùng địa chỉ HTTPS ở bước 3.

```bash
ssh-keygen -t ed25519 -C "email-cua-ban@example.com"
cat ~/.ssh/id_ed25519.pub        # sao chép nội dung này vào GitHub
ssh -T git@github.com            # phải thấy lời chào có tên tài khoản của bạn
```

3. **Thêm remote và đẩy nhánh `main`:**

```bash
git remote add origin git@github.com:<tai-khoan-hoac-to-chuc>/exam-platform.git
git branch -M main
git push -u origin main
```

Nếu dùng HTTPS thì địa chỉ là `https://github.com/<tai-khoan-hoac-to-chuc>/exam-platform.git`. Kiểm tra bằng `git remote -v` và tải lại trang repo trên GitHub, phải thấy `docs/PRD.md`, `docs/PLAYBOOK.md` và `CLAUDE.md`.

4. **Bật bảo vệ cơ bản** trong Settings của repo: bật secret scanning và push protection; với nhánh `main`, nếu bạn làm một mình thì tối thiểu yêu cầu CI xanh trước khi gộp.
5. **Quy tắc dữ liệu:** chỉ đẩy dữ liệu tổng hợp lên GitHub. Không commit đề thi thật, ảnh phiếu của sinh viên, danh sách sinh viên thật, hay khóa API. Nhờ Claude Code kiểm tra `.gitignore` đã chặn `.env`, thư mục lưu ảnh upload và dữ liệu thật; các file mẫu dùng cho test chỉ chứa dữ liệu giả.

**Làm việc theo nhánh với remote**

Từ mỗi mốc, thay bước 9 ở mục 2 bằng một trong hai cách:

- *Gộp bằng Pull Request (khuyên dùng, vì CI chạy trên GitHub và để lại lịch sử):* đẩy nhánh mốc, mở PR vào `main`, đợi CI xanh, gộp trên GitHub rồi cập nhật máy.
- *Gộp local như mục 2,* rồi đẩy `main` và tag lên GitHub.

```bash
# Cách 1: Pull Request
git push -u origin m1-auth-orgs
# mở Pull Request trên GitHub, đợi CI xanh, bấm merge, rồi:
git switch main
git pull
git tag m1-done
git push origin m1-done

# Cách 2: gộp local
git switch main
git merge --no-ff m1-auth-orgs
git tag m1-done
git push origin main --tags
```

Nếu đã cài GitHub CLI, có thể mở PR từ terminal bằng `gh pr create`. Để Claude Code soạn sẵn nội dung PR, dùng prompt sau trong phiên của mốc (hoặc phiên review):

```text
Summarize this branch for a pull request: what changed, how to test it, the definition of done checklist for milestone [M?] (docs/PLAYBOOK.md, Appendix C) with the status of each item, and anything deferred. Write it as text I can paste into the PR description. Do not push anything.
```

**Về quyền đẩy mã:** để Claude Code commit trên nhánh mốc là được. Với lệnh `git push`, bạn nên tự chạy hoặc chỉ cho phép đúng lệnh đẩy nhánh mốc, không cho đẩy `main` hay dùng `--force`.

**Nếu lỡ commit khóa API hoặc mật khẩu:** thu hồi và tạo khóa mới ngay ở nhà cung cấp (xóa khỏi lịch sử git thôi chưa đủ vì khóa đã lộ); sau đó mới dọn lịch sử.

*Kiểm tra xong bước 1.6:* trang repo trên GitHub hiển thị đủ ba file; `git status` báo nhánh `main` đã đồng bộ với `origin/main`; trong thư mục repo không có file `.env` nào xuất hiện trong `git status`.

## 2. Quy trình chuẩn cho mỗi mốc

Mười một mốc (M0 đến M9 và S1) đều đi qua cùng chín bước. Làm đúng thứ tự này sẽ giữ cho mỗi mốc nhỏ, kiểm được và quay lui được.

1. **Tạo nhánh.** `git switch -c m1-auth-orgs` (đặt tên theo mốc).
2. **Mở phiên Claude Code mới** trong thư mục repo bằng lệnh `claude`. Mỗi mốc một phiên mới, hoặc dùng `/clear` nếu phiên cũ còn, để ngữ cảnh sạch và không lẫn quyết định của mốc trước.
3. **Bật plan mode** (chuyển chế độ bằng Shift+Tab). Claude chỉ lập kế hoạch, chưa sửa file.
4. **Dán prompt kickoff của mốc** (mục 4). Prompt đã bảo Claude đọc `CLAUDE.md` và đúng các mục PRD cần thiết.
5. **Đọc kế hoạch kỹ trước khi cho chạy.** Hỏi bốn câu:
   - Có làm đúng phạm vi mốc, không kéo thêm tính năng của mốc sau?
   - Danh sách file sửa có hợp lý, có file nào lạ ngoài `backend/`, `frontend/`, `docs/`?
   - Có thêm thư viện mới không, lý do là gì?
   - Có đụng vào các quy tắc bất biến trong `CLAUDE.md` không? Chưa ổn thì trả lời thẳng trong phiên để Claude sửa kế hoạch; ổn thì chấp nhận kế hoạch.
6. **Theo dõi khi Claude làm.** Nếu thấy nó đi chệch (sửa PRD, viết tính năng ngoài mốc, bỏ qua test), ngắt và dùng prompt "kéo về đúng hướng" ở mục 3.
7. **Tự kiểm.** Chạy bộ lệnh dưới đây, rồi tự thao tác giao diện theo mục "Điều cần tự tay kiểm" của mốc, và đối chiếu từng tiêu chí hoàn thành.
8. **Review diff** bằng prompt review ở mục 3 trong một phiên mới (để Claude nhìn mã bằng mắt người ngoài), sửa các điểm đáng sửa.
9. **Tổng kết và gộp.** Dùng prompt tổng kết ở mục 3 để cập nhật tài liệu và ghi quyết định, rồi commit và gộp (đã kết nối GitHub thì xem thêm cách gộp bằng Pull Request ở bước 1.6):

```bash
git add .
git commit -m "feat(m1): auth, orgs, roster import"
git switch main
git merge --no-ff m1-auth-orgs
git tag m1-done
```

**Bộ lệnh kiểm tra dùng cho mọi mốc**

```bash
# bảo đảm PostgreSQL đang chạy (xem bước 1.1b)
cd backend && uv run pytest && uv run ruff check . && uv run mypy app
cd ../frontend && pnpm test && pnpm lint
```

Từ M7 trở đi thêm `pnpm e2e`. Đừng gộp vào `main` khi một lệnh trên còn đỏ.

**Quy tắc kích thước**

- Một mốc nên xong trong một đến vài ngày làm việc. Nếu kế hoạch Claude đưa ra quá dài (nhiều chục file, nhiều nhóm tính năng không liên quan), yêu cầu tách làm hai nhánh con rồi làm lần lượt.
- Mỗi phiên chỉ một mục tiêu. Việc phát sinh ngoài mốc ghi vào danh sách "để sau" trong `docs/decisions/`, không làm lẫn.

## 3. Bộ prompt dùng lại

Các prompt dưới đây dùng ở mọi mốc. Thay phần trong ngoặc vuông.

**3.1 Kickoff một mốc**

Prompt đầy đủ của từng mốc nằm ở mục 4. Nếu muốn viết nhanh một prompt kickoff tùy biến, dùng mẫu này:

```text
Read CLAUDE.md and docs/PRD.md sections [list]. We are working on milestone [M?]: [name].
Scope: [one or two sentences]. Out of scope: [what later milestones cover].
Before writing code, give me a plan with: files you will create or change, data model changes, the tests you will write, and any dependency you want to add with the reason.
Do not start coding until I approve the plan.
```

**3.2 Kéo Claude về đúng hướng**

```text
Stop. You are drifting from the milestone scope: [what it did].
Re-read CLAUDE.md and the PRD sections for this milestone. Revert the changes outside scope, keep a note of them in docs/decisions/later.md, then continue with the remaining in-scope tasks.
```

**3.3 Tự kiểm tiêu chí hoàn thành**

```text
Go through the definition of done of milestone [M?] (docs/PLAYBOOK.md, Appendix C) and the related acceptance criteria in docs/PRD.md, one by one.
For each criterion, tell me which test or manual check proves it, run the test, and report pass or fail with evidence. List any criterion that has no test yet and write the missing test. Do not mark anything as done without running it.
```

**3.4 Review diff trong phiên mới**

Mở phiên mới (Claude không nhớ quá trình viết mã) rồi dán:

```text
Review the changes on this branch against main (git diff main).
Check against CLAUDE.md non-negotiable rules and docs/PRD.md for this milestone. Look for: broken immutability rules, missing authorization checks or tests, scores or answers stored in a way that cannot be recomputed, silent failures where the system should flag for review, secrets in code, and tests that do not actually assert behavior.
Report findings as a list ordered by severity with file and line. Do not change any code.
```

**3.5 PRD mâu thuẫn hoặc còn thiếu**

```text
The PRD seems to [conflict with itself / not cover this case]: [describe].
Do not choose silently. Show me the options with trade-offs and your recommendation. After I decide, update docs/PRD.md first (and note the change in docs/decisions/), then continue with the code.
```

**3.6 Sửa lỗi theo kiểu có test**

```text
Bug: [what I did, what I expected, what happened, error message if any].
First write a failing test that reproduces it. Then find the root cause and fix it with the smallest change. Run the full test suite and lint. Explain the cause in two sentences. Do not refactor unrelated code.
```

**3.7 Tổng kết mốc**

```text
Milestone [M?] is done. Update the repository documentation:
- README: how to run and test what exists now.
- docs/decisions/: one short note per notable decision made in this milestone (what, why, alternatives).
- docs/PRD.md: only if behavior changed from the PRD, mark the change clearly.
Then propose a commit message and list anything deferred to later milestones.
```

## 4. Từng mốc: bước, prompt, cách kiểm

Mỗi mốc được chia thành một đến ba prompt chạy tuần tự trong cùng một phiên (mỗi prompt là một vòng plan, chạy, kiểm). Chi tiết yêu cầu nằm ở `docs/PRD.md` nên prompt ngắn gọn, chỉ trỏ đúng mục. Với mọi mốc, bắt đầu bằng bước 1 đến 4 của mục 2 và kết thúc bằng bước 7 đến 9.

**M0. Nền tảng repo** (nhánh `m0-foundation`)

Prompt 1:

```text
Read CLAUDE.md and docs/PRD.md sections 2 and 8. Milestone M0: project skeleton, no business features. Plan first.
Create: no Docker and no Redis in this phase: a README section on installing PostgreSQL locally on Windows, .env.example (database URL and other settings), a JobQueue interface with a PostgreSQL-backed implementation (a jobs table; workers claim jobs with FOR UPDATE SKIP LOCKED) and a worker entry point run by `uv run python -m app.worker`, .gitignore (must ignore .env and uploaded data), backend (FastAPI with /health, pydantic-settings, SQLAlchemy 2.0 + Alembic, a worker process with one sample job through the JobQueue, pytest + ruff + mypy via uv), frontend (Vite + React + TypeScript, routing, TanStack Query, Tailwind, API client generated from the backend OpenAPI schema), CI running lint and tests for both sides (with a PostgreSQL service for backend tests), and docs/decisions/001-stack.md.
```

Prompt 2 (sau khi prompt 1 xong):

```text
Add a README section explaining how to start everything, run tests, regenerate the API client, and enqueue the sample job. Then verify every command in it from a clean state (drop and recreate the local database first) and fix whatever fails.
```

*Điều cần tự tay kiểm:* chạy `uv run uvicorn app.main:app --reload` (API), rồi mở thêm hai cửa sổ terminal chạy worker (uv run python -m app.worker) và web (pnpm dev); mở địa chỉ `/health` của API thấy OK; mở trang web thấy trang khởi đầu; log của worker cho thấy job mẫu đã chạy; kiểm tra file `.gitignore` có chặn `.env`.

**M1. Đăng nhập, vai trò, dữ liệu nền** (nhánh `m1-auth-orgs`)

Prompt 1 (backend):

```text
Read CLAUDE.md and docs/PRD.md sections 3, 4.1 and 7. Milestone M1, backend only. Plan first.
Models and Alembic migrations: Department, User, Course, Module, CLO, CourseAssignment, AuditLog. Auth: email + password login, JWT in an httpOnly cookie, argon2, login rate limiting, change password, admin password reset, forced password change on first login. RBAC as FastAPI dependencies with department and course scoping exactly as the matrix in PRD section 3. CRUD APIs for organization data. Write an authz test for every endpoint: allowed and forbidden cases per role.
```

Prompt 2 (giao diện và roster):

```text
Milestone M1, part 2. Build the UI: login and change-password pages; Admin and HoD screens for departments, courses, modules (drag to reorder), CLOs and lecturer assignments. Then the student roster import from Excel (student_code, full_name, email, class), where student_code must match a configurable pattern (default two letters + six digits like HE170001, normalized to uppercase): downloadable template, dry-run, per-row errors, then apply and create student accounts. Add a seed script: 2 departments, 3 courses with modules, one user per role. Add tests for the import.
```

*Điều cần tự tay kiểm:* đăng nhập bằng từng tài khoản seed; đăng nhập HoD bộ môn A và thử mở môn của bộ môn B (phải bị chặn); tạo một file roster có một dòng lỗi (thiếu email) và xem hệ thống báo đúng dòng; đổi vai trò một người rồi xem bản ghi audit.

**M2. Ngân hàng câu hỏi và luồng duyệt** (nhánh `m2-question-bank`)

Prompt 1 (backend):

```text
Read CLAUDE.md and docs/PRD.md sections 4.2, 4.3 and 7. Milestone M2, backend only. Plan first.
Models: Question, QuestionRevision, QuestionOption, Tag, QuestionCLO. Types single, multiple, true_false with the validation rules in FR-QB-1. Unique question codes like ISD201-M03-0042. Every edit creates an immutable revision. Status workflow draft -> pending -> approved or rejected (rejection needs a reason); editing an approved question creates a pending revision while the approved one stays effective. APIs with filters (course, module, difficulty, CLO, tag, status, author, source) and PostgreSQL full-text search. Soft archive only. Tests for every acceptance criterion in PRD 4.3 and authz tests per endpoint.
```

Prompt 2 (giao diện):

```text
Milestone M2, UI. Question list with filters and search; editor with 2-6 dynamic options, correct answer selection, difficulty, CLOs, tags, explanation and the lock-option-order flag; revision history view; submit for review; HoD review queue with batch approve and reject (reason required). Show validation errors inline.
```

Prompt 3 (hiệu năng):

```text
Add tools/seed_questions.py that creates 5,000 questions across a few courses. Measure the question list API latency with filters and full-text search, add indexes if needed, and record the numbers in docs/decisions/. Target: under 1 second.
```

*Điều cần tự tay kiểm:* tạo một câu mỗi loại (single, multiple, true/false) và thử cố ý nhập sai (ví dụ câu single có hai đáp án đúng) để xem thông báo lỗi; gửi duyệt rồi HoD duyệt và từ chối; sửa một câu đã duyệt và thấy bản cũ vẫn là bản hiệu lực; mở lịch sử revision.

**S1. Spike OMR** (nhánh `s1-omr-spike`, làm sau M0, có thể song song M1 và M2)

Đây là cổng quyết định. Đừng làm M6 và M7 trước khi S1 đạt.

Prompt 1 (layout và phiếu PDF):

```text
Read CLAUDE.md and docs/PRD.md sections 6 and 7.3. Milestone S1, step 1. Build backend/app/omr as a library with no database dependency. Plan first.
layout.py: a parametric layout engine (questions <= 60, options <= 6, student code as a configurable pattern, default two letters + six digits like HE170001 with letter columns A-Z and digit columns 0-9, version code 3 digits) producing a serializable Layout with mm coordinates of 4 ArUco corner markers, the QR area, every bubble (grid id, row, col, center, radius) and per-question option counts (unused bubbles flagged).
sheet_pdf.py: render a Layout to an A4 PDF with ReportLab: title, fill instructions, QR (exam id, layout version, checksum), handwritten name and signature boxes. Add a CLI to generate a sample sheet with 40 questions. The 26-row letter columns make the student code grid tall: verify that the grid, the version code grid, the QR and 60 questions still fit on one A4 page. If not, say so and propose options (for example a configured list of allowed letter prefixes) before continuing.
```

*Dừng lại và kiểm bằng tay:* in file PDF mẫu ở tỷ lệ 100% (không chọn fit to page), dùng thước đo khoảng cách giữa hai ô liên tiếp và so với số liệu trong layout. Đo lệch quá 1 mm thì yêu cầu Claude sửa trước khi đi tiếp.

Prompt 2 (bộ đọc và ảnh tổng hợp):

```text
S1, step 2. Build app/omr/reader.py: detect the 4 ArUco markers, warp to a canonical size, decode the QR, measure each bubble fill ratio, classify filled / empty / ambiguous with two thresholds and per-sheet calibration, decode student code and version code, return a ReadResult with raw fill ratios and flags as in PRD 6.4.
Also tools/make_test_sheets.py: generate synthetic filled sheets (random answers incl. multi-mark, faint marks, blank questions) and degraded variants (rotation up to 10 degrees, perspective warp, blur, uneven lighting and shadow, noise, JPEG compression).
Tests in tests/omr: 100% on clean sheets; a table of accuracy and false-confident rate (wrong but not flagged) per degradation type. Do not tune thresholds only to pass: report honestly in docs/omr-notes.md.
```

Prompt 3 (ảnh thật), sau khi bạn chuẩn bị ảnh:

1. In ít nhất hai phiếu mẫu, tô bằng bút chì và bút bi với các lỗi cố ý: một câu tô hai ô, một ô tô nhạt, một câu bỏ trống, một mã sinh viên tô thiếu cột.
2. Chụp mười ảnh bằng điện thoại: ánh sáng bình thường, có bóng, nghiêng nhẹ, giấy hơi cong, ánh sáng yếu. Lưu vào `backend/tests/omr/real/` và tạo `answers.json` ghi đáp án bạn đã tô.

```text
Run the reader on every image in backend/tests/omr/real against answers.json. Report per-image accuracy, flags raised and the false-confident count in docs/omr-notes.md. For each failure, explain the cause from the image (marker not found, shadow, faint mark, etc.).
```

Nếu có ảnh đọc sai mà không gắn cờ, dùng prompt chẩn đoán:

```text
Analyze the failures in docs/omr-notes.md. For each failure class, propose a fix in the sheet design (bubble size, marker size, margins) or in the reader (thresholds, preprocessing). Implement the most impactful fix, regenerate the sheets and re-run all OMR tests. Report before and after numbers. Never trade false-confident errors for fewer review flags.
```

*Cổng quyết định:* đạt khi ảnh sạch tổng hợp 100%, tỷ lệ sai không cờ trên bộ ảnh xấu và ảnh thật đạt mục tiêu ở mục 1 của PRD. Chưa đạt thì lặp lại prompt chẩn đoán, hoặc bàn lại thiết kế phiếu với tôi.

**M3. Import Excel và phát hiện câu trùng** (nhánh `m3-import-dedupe`)

Prompt 1 (backend):

```text
Read CLAUDE.md and docs/PRD.md sections 4.5, 5.1 and 7. Milestone M3, backend. Plan first.
importers/excel_questions.py: parse and validate the question template (columns in PRD 4.5) with per-row errors; downloadable template and error report. ImportJob flow: upload -> dry-run -> confirm -> create draft questions (optional submit for review).
dedupe/: normalize text, exact match on normalized stem plus option set, fuzzy match with rapidfuzz (default 0.85, configurable), scoped to the same course; an EmbeddingProvider interface without implementation. Wire dedupe into manual save and import.
importers/excel_exam.py: parse only (single question_code column), return resolved questions or per-row errors.
Also tools/make_sample_import.py generating a 100-row sample with 3 bad rows and 5 near-duplicates of existing questions. Tests per PRD 4.5 acceptance criteria.
```

Prompt 2 (giao diện):

```text
Milestone M3, UI: import wizard (upload, error table, duplicate review with skip / keep anyway / replace by new revision, confirm) and a duplicate warning in the question editor on save.
```

*Điều cần tự tay kiểm:* chạy script tạo file mẫu, import và đối chiếu: đúng 3 dòng lỗi, đúng năm câu bị báo trùng; tự sửa một câu cũ chỉ khác dấu câu rồi lưu và xem cảnh báo trùng.

**M4. Sinh câu hỏi bằng AI** (nhánh `m4-ai-generation`)

Prompt 1 (provider và schema):

```text
Read CLAUDE.md and docs/PRD.md sections 4.4, 8.3 and 7. Milestone M4, step 1. Plan first.
ai/providers: LLMProvider protocol (generate_structured), an Anthropic implementation, and a fake provider with deterministic output for tests. Provider and model are chosen by env vars (AI_PROVIDER, AI_MODEL). No provider SDK imports outside this package. ai/prompts: a versioned prompt file for question generation and a Pydantic output schema (stem, type, options with is_correct, explanation, difficulty, suggested CLOs and tags, source reference). Validate output and retry up to 2 times. Tests use only the fake provider.
```

Prompt 2 (tài liệu và job):

```text
M4, step 2. ai/ingestion: extract text from PDF, DOCX, PPTX, TXT (20 MB per file, 5 files per request) keeping page or slide references; chunk long documents, generate per chunk and merge. Generation runs as a background job (JobQueue) with progress and cancel; a GenerationBatch stores parameters, provider, model, prompt version, token usage and the user. Parameters per FR-AI-2. Auto-set lock_option_order for all of the above / none of the above. Run dedupe on results. Add the APIs and tests with the fake provider.
```

Prompt 3 (giao diện):

```text
M4, step 3, UI: generation form, progress view, batch review screen (edit inline, discard, regenerate one question, submit selected for review). There must be no auto-approve anywhere.
```

*Điều cần tự tay kiểm (cần khóa API thật):* đặt khóa vào `.env`, chọn một chương giáo trình dạng PDF, sinh 10 câu. Tự đọc từng câu: đáp án đúng chưa, câu có bám tài liệu không, tham chiếu trang có đúng không. Rồi đổi `AI_PROVIDER` sang `fake` và xác nhận hệ thống vẫn chạy mà không sửa mã. Ghi nhận xét chất lượng vào `docs/decisions/` để chỉnh prompt sau.

**M5. Dựng đề, chốt, mã đề, clone** (nhánh `m5-exam-builder`)

Prompt 1 (mô hình và chốt đề):

```text
Read CLAUDE.md and docs/PRD.md sections 5.1-5.4 and 7. Milestone M5, step 1: data model and finalize logic only, no UI. Plan first.
Models: Exam, ExamItem, BlueprintRule, ExamVersion, ExamVersionItem, ExamCorrection (table only). Finalize in one transaction: freeze the exam, snapshot each question revision into the version items, generate versions from seeds (respect lock_option_order and the shuffle toggles), store the layout JSON from app/omr. After that the exam is immutable at the service layer. Clone into a new draft. Complete the M2 stub: block hard delete for questions used by locked exams. Tests: same question set but different order between versions, same seed gives the same result, editing a source question does not change a locked exam, writes to a locked exam are rejected.
```

Prompt 2 (ba cách dựng đề):

```text
M5, step 2: APIs and services for the three build modes: (a) Excel by question_code using the M3 parser; (b) manual selection with filters, add, remove, reorder; (c) random from blueprint rules (module x difficulty x count) with a stored seed, shortage errors naming the module and difficulty, preview, reroll one question or all. Eligibility: approved questions plus the author's own non-rejected questions. Max 60 questions. Tests per the acceptance criteria in PRD 5.
```

Prompt 3 (giao diện):

```text
M5, step 3, UI: exam list and creation wizard with the three modes, blueprint table editor, preview, exam configuration (versions, shuffle toggles, instructions, pass mark), Finalize with a confirmation that explains it cannot be undone, Clone, and the HoD action to approve a locked exam into the shared library.
```

*Điều cần tự tay kiểm:* dựng ba đề bằng ba cách; với đề random hãy cố ý yêu cầu nhiều câu hơn số câu có trong kho và xem thông báo thiếu; chốt đề, sửa một câu gốc trong ngân hàng rồi mở lại đề đã chốt (không được đổi); clone đề và sửa bản clone.

**M6. Xuất Word, đáp án, phiếu PDF** (nhánh `m6-export`)

```text
Read CLAUDE.md and docs/PRD.md sections 5.5 and 6.1. Milestone M6. Plan first.
exporters/docx_exam.py: one .docx per exam version with python-docx: prominent version code at the top of page 1, title, duration, instructions, questions in the version order, options lettered A-F, a Select all that apply line for multiple-answer questions, no header or footer. exporters/docx_key.py: one .docx for the lecturer with an answer table per version and a mapping table from original question number to number in each version. The answer sheet PDF comes from the exam's stored layout JSON via app/omr/sheet_pdf.py, one sheet for all versions. A background job builds a ZIP with everything and a download endpoint; add the button on locked exams in the UI.
Tests: parse each generated docx back and check the answer key matches the order and options of that version; exporting a locked exam after editing the source questions gives identical content.
```

*Điều cần tự tay kiểm:* tải gói ZIP, mở file Word của hai mã đề và so khớp thủ công năm câu bất kỳ với bảng đáp án; in phiếu và đặt lên cạnh phiếu mẫu S1 để chắc layout không đổi.

**M7. Scan trong ứng dụng, xử lý nền, màn hình review** (nhánh `m7-scan-review`)

Prompt 1 (backend và job):

```text
Read CLAUDE.md and docs/PRD.md sections 6.2-6.5, 7 and 8.4. Milestone M7, step 1: backend only. Reuse app/omr without changing its public interface unless you explain why. Plan first.
Models: ExamSession, Enrollment, ScanImage, Submission, SubmissionAnswer, GradingRun. Upload endpoints for images and multi-page PDFs; re-encode to JPEG (max 2480 px long edge, quality 85); store raw read results; set expires_at to 4 months after upload. One background job (JobQueue) per image: read, map answers to option_id through the version option order, grade, apply every flag rule in PRD 6.4, set status auto or needs_review; roster lookup and duplicate student detection within a session. Tests with synthetic sheets covering every flag rule; a needs_review sheet is never counted as auto.
```

Prompt 2 (trang Scan):

```text
M7, step 2: the Scan page. Live camera with an alignment frame and continuous capture, a Take photo fallback using the system camera, and drag-and-drop upload; a queue view with per-image status. Write docs/dev-https.md explaining how to test the live camera from a phone on the local network with a local HTTPS certificate (mkcert or a tunnel).
```

Prompt 3 (màn hình review):

```text
M7, step 3: the Review screen. Queue of needs_review submissions filtered by reason with keyboard shortcuts; warped image with overlays for filled, ambiguous and error bubbles; click a bubble to change the answer; roster search to fix the student code; change version; mark invalid; Confirm. Every manual edit writes an audit row and recomputes the score. Add Playwright tests covering a flagged sheet end to end.
```

*Điều cần tự tay kiểm:* tạo một đề, tạo kỳ thi với roster, in 10 phiếu và tô có chủ đích các tình huống lỗi: hai ô một câu, ô nhạt, mã sinh viên không có trong roster, mã đề không thuộc đề, hai phiếu cùng một sinh viên, một phiếu để trắng. Chụp bằng điện thoại trong ứng dụng và xác nhận mỗi tình huống đều vào hàng review với đúng lý do. Sửa tay một phiếu và xem điểm đổi.

**M8. Kết quả, báo cáo, đính chính, cổng sinh viên** (nhánh `m8-results`)

Prompt 1 (kết quả và Excel):

```text
Read CLAUDE.md and docs/PRD.md sections 5.4, 6.6 and 7. Milestone M8, step 1. Plan first.
Result views per session (status filters, score distribution, mean, median, standard deviation, pass rate) and the Excel export with four sheets (Results, Answers, Question stats, Exam summary) using openpyxl: Answers uses original question order and original option letters. Tests: the Excel numbers match the database.
```

Prompt 2 (đính chính và chấm lại):

```text
M8, step 2: corrections and regrade. ExamCorrection with three types (change correct answer, accept additional answer, void question), mandatory reason, audit log, applied to all versions. A regrade job recomputes every submission from stored answers, keeps GradingRun history and shows before and after scores; flag the source question in the bank for review. Tests: a correction changes exactly the affected scores and keeps history.
```

Prompt 3 (sinh viên):

```text
M8, step 3: Publish results action; the student portal (published exams, score, per-question detail with correct answers only if the lecturer enabled it, own scan image while not expired); review requests from students with open / in_review / resolved handling by lecturer and HoD. Tests: students cannot see unpublished results or other students' data.
```

*Điều cần tự tay kiểm:* chấm xong bộ phiếu thử, xuất Excel và dò thủ công ba sinh viên; đính chính một câu và so điểm trước sau; đăng nhập tài khoản sinh viên để xem bài của mình trước và sau khi công bố; thử mở bài của sinh viên khác bằng cách sửa địa chỉ trên trình duyệt (phải bị chặn).

**M9. Hoàn thiện** (nhánh `m9-hardening`)

```text
Read CLAUDE.md and docs/PRD.md sections 8.4 and 9. Milestone M9. Plan first.
1) A nightly job deleting expired scan images (file and path only, keep submissions) with a log, and UI text for expired images. 2) Verify that every state-changing action listed in PRD section 3 writes an AuditLog row, add missing ones, and add an audit viewer for Admin and HoD. 3) Performance: seed 1,000 synthetic sheets for one session, measure grading throughput with 4 workers, measure list latency with 5,000 questions per course, fix hotspots, record numbers in docs/performance.md. 4) Playwright scenarios: lecturer builds a random exam, finalizes, exports; uploads synthetic scans; reviews flagged sheets; publishes; student logs in and sees the score. 5) Security pass: signed short-lived URLs for scan images, upload validation, rate limits, dependency audit. 6) docs/runbook.md: setup, env vars, backup and restore, switching AI provider, deploying behind HTTPS.
```

*Điều cần tự tay kiểm:* đối chiếu số đo hiệu năng với mục 9.1 của PRD; chạy lại toàn bộ kịch bản end-to-end; nhờ một người khác làm theo `docs/runbook.md` trên máy sạch xem có dựng được hệ thống không.

## 5. Khi gặp sự cố

| Tình huống | Cách xử lý |
| --- | --- |
| Claude làm quá phạm vi mốc hoặc viết tính năng của mốc sau | Ngắt, dùng prompt 3.2 (kéo về đúng hướng). Nếu đã commit quá nhiều, `git reset` về commit sạch gần nhất rồi cho làm lại với kế hoạch hẹp hơn |
| Kế hoạch quá dài, quá nhiều file | Yêu cầu tách mốc thành hai nhánh con; làm lần lượt, mỗi nhánh có kiểm riêng |
| Claude tự ý đổi hành vi so với PRD | Dùng prompt 3.5; sửa PRD trước, mã sau. Không để mã và PRD lệch nhau, vì các phiên sau đọc PRD |
| Test đỏ và Claude cứ sửa test cho xanh | Dặn rõ: sửa mã chứ không sửa test để qua. Dùng prompt 3.6: viết test tái hiện lỗi trước, tìm nguyên nhân gốc, rồi sửa |
| Phiên làm việc dài, Claude bắt đầu quên quy tắc | Chạy tổng kết (prompt 3.7), commit, rồi mở phiên mới. Quy tắc quan trọng luôn nằm trong `CLAUDE.md` nên không mất |
| Claude thêm thư viện lạ | Hỏi lý do và phương án thay thế trong thư viện sẵn có. Chỉ chấp nhận khi lý do đủ mạnh, ghi vào `docs/decisions/` |
| Đọc ảnh OMR sai không báo cờ | Đây là lỗi nghiêm trọng nhất. Dừng việc khác, thêm ảnh lỗi vào bộ test, dùng prompt chẩn đoán của S1, không gộp nhánh khi còn ca sai không cờ |
| Camera trực tiếp không chạy trên điện thoại | Thường do thiếu HTTPS. Làm theo `docs/dev-https.md`; trong lúc đó dùng nút Take photo hoặc tải ảnh lên |
| Kết quả AI sinh kém hoặc sai | Chỉnh file prompt trong `ai/prompts/` (tăng phiên bản), thêm ví dụ câu tốt vào prompt, chạy lại; mọi câu vẫn phải qua HoD duyệt |
| Không chắc nên làm gì tiếp | Quay lại Phụ lục C (bảng phụ thuộc giữa các mốc) và tuân theo thứ tự đó |

**Ba thói quen giúp cả dự án trơn tru**

1. Commit nhỏ và thường xuyên; tag sau mỗi mốc để quay lui dễ.
2. Luôn tự tay thử trên giao diện thật, không chỉ tin test xanh.
3. Mỗi quyết định đáng nhớ ghi vào `docs/decisions/` để các phiên Claude Code sau không phải đoán.

## Phụ lục A. Nội dung CLAUDE.md

Tạo file `CLAUDE.md` ở thư mục gốc repo với nội dung dưới đây. Claude Code đọc file này đầu mỗi phiên, nên các quy tắc bất biến luôn được nhắc lại.

```markdown
# Exam Platform

AI-assisted multiple-choice exam platform: question bank, exam builder,
Word/PDF export, and scan-based grading of paper answer sheets.

Read docs/PRD.md before starting any task. It is the source of truth for product behavior.
Milestones, prompts and definitions of done are in docs/PLAYBOOK.md.
If a task conflicts with the PRD, stop and ask before changing anything.

## Stack and commands
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL (installed locally as a Windows service), a PostgreSQL-backed job queue behind a JobQueue interface, OpenCV. No Docker and no Redis for now.
- Frontend: React, Vite, TypeScript, TanStack Query, Tailwind.
- Database: local PostgreSQL service (see docs/PLAYBOOK.md step 1.1b)
- Run API: `cd backend && uv run uvicorn app.main:app --reload`; worker: `uv run python -m app.worker`; web: `cd frontend && pnpm dev`
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
- Background work goes through the JobQueue interface. Do not add Docker or Redis unless asked.
- Small commits with clear messages. Run lint and tests before saying a task is done.

## Workflow
- Work on one milestone at a time (see docs/PLAYBOOK.md). Start with a plan listing the files you will touch.
- Definition of done: tests pass, lint is clean, the milestone definition of done and the related PRD acceptance criteria are verified, docs updated.
- Record notable decisions in docs/decisions/NNN-title.md.
```

## Phụ lục B. Cấu trúc repo

```text
exam-platform/
├── CLAUDE.md
├── .env.example
├── docs/
│   ├── PRD.md
│   ├── PLAYBOOK.md
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
│   │   └── jobs/               # tác vụ nền (JobQueue, worker)
│   └── tests/
│       ├── unit/
│       ├── api/
│       └── omr/                # ảnh phiếu tổng hợp và biến thể có nhiễu
├── frontend/
│   ├── src/                    # pages, components, api, hooks, lib
│   └── e2e/
└── tools/                      # seed data, tạo phiếu thử
```

## Phụ lục C. Lộ trình, phụ thuộc và tiêu chí hoàn thành

| Mốc | Nội dung | Phụ thuộc | Hoàn thành khi |
| --- | --- | --- | --- |
| M0 | Nền tảng repo, PostgreSQL cục bộ, hàng đợi job, khung API và web, CI | — | `uv run uvicorn` (API), worker và web chạy được; `/health` trả OK; mỗi phía có ít nhất một test xanh trong CI; sinh được API client từ OpenAPI |
| M1 | Đăng nhập, vai trò, bộ môn, môn, module, CLO, roster | M0 | Bốn vai trò đăng nhập được; HoD bộ môn A không thấy môn bộ môn B (có test); import roster có dòng lỗi thì báo đúng dòng; đổi vai trò tạo bản ghi audit |
| M2 | Ngân hàng câu hỏi, revision, luồng duyệt | M1 | Tiêu chí nghiệm thu mục 4.3 của PRD có test xanh; danh sách lọc trên 5.000 câu phản hồi dưới 1 giây; sửa, gửi duyệt, duyệt chạy trọn vòng |
| S1 | Spike OMR: layout engine, phiếu PDF, bộ đọc, bộ test ảnh | M0, song song M1–M2 | In A4 đúng tỷ lệ và đo thước khớp layout; ảnh tổng hợp sạch đọc đúng 100%; tỷ lệ sai không cờ trên bộ ảnh xấu ≤ 0,1% hoặc có tài liệu giải thích khoảng cách; đã chạy 10 ảnh thật và ghi kết quả |
| M3 | Import Excel (câu hỏi, đề) và phát hiện câu trùng | M2 | Hai tiêu chí nghiệm thu mục 4.5 có test xanh; wizard import chạy trọn vòng với file mẫu |
| M4 | Sinh câu hỏi bằng AI | M2, M3 | Sinh được batch 20 câu bằng provider giả trong test và provider thật khi có khóa; câu từ tài liệu có tham chiếu nguồn; đổi `AI_PROVIDER` không cần sửa mã nghiệp vụ; câu lỗi schema được thử lại và không làm hỏng batch |
| M5 | Dựng đề 3 cách, chốt, mã đề, clone | M2, M3 | Tiêu chí nghiệm thu mục 5 về dựng đề và chốt có test xanh; chốt đề lặp lại với cùng seed cho cùng kết quả; giao diện dùng được cả ba cách |
| M6 | Xuất Word, đáp án, phiếu PDF | M5, S1 | Mở file Word thấy đúng định dạng; bảng đáp án từng mã khớp nội dung đề; phiếu PDF khớp layout đã kiểm ở S1 |
| M7 | Scan trong ứng dụng, xử lý nền, màn hình review | M6, S1, M1 | Chụp bằng điện thoại trong ứng dụng cho ra kết quả; mọi tình huống ở bảng 6.4 của PRD có test; không phiếu nào ở trạng thái auto khi có ô mờ hoặc hai ô tô trong câu một đáp án |
| M8 | Kết quả, báo cáo Excel, đính chính, chấm lại, cổng sinh viên, phúc khảo | M7 | Sửa đáp án một câu rồi chấm lại đổi đúng điểm bài bị ảnh hưởng; sinh viên xem đúng bài của mình sau khi công bố; Excel khớp dữ liệu trong hệ thống |
| M9 | Hoàn thiện: dọn ảnh, audit, hiệu năng, e2e, tài liệu | M0–M8 | Số đo hiệu năng đạt mục 9.1 của PRD; kịch bản end-to-end chạy xanh; runbook đủ để dựng lại hệ thống từ đầu |
