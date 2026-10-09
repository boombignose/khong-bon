# ผลตรวจ · 2026-10-09

## ทดสอบในเครื่อง

- Python 3.9.6 บน macOS arm64
- FFmpeg full 9.0.2, libass, ฟอนต์ Noto Sans Thai ที่แนบมาพร้อม OFL
- `python3 -m unittest discover -s tests -v`: 7 tests ผ่าน รวมการประกอบวิดีโอและเสียงจริงเป็น MP4 24 วินาที
- ตรวจ malformed JSON structure, duration ผิด/boolean, จำนวนช็อตผิด, บทพูดยาวหรือมีคำสั่ง ASS, ป้องกันการทับ pack เดิม
- ตรวจ input media มีภาพ/เสียงและความยาว 8 วินาที
- integration ใช้ชื่อไฟล์ไทย ช่องว่างและ apostrophe; input hash ไม่เปลี่ยน, output เดิมไม่ถูกทับ, Skill ที่คัดลอกไป path ใหม่รัน pack ได้
- ตัวอย่าง 4 บทและ pack ผ่าน schema; ลิงก์ภายในชุดตรวจด้วย check_repo.py

## ขอบเขตหลักฐาน

เทคนิคผ่านไม่ได้หมายถึงความขำ ภาษาไทย ปากและเสียง หรือความต่อเนื่องของภาพผ่าน QC ตัวอย่าง Flow คงสถานะ NEEDS_HUMAN_REVIEW ดู [DEMO.md](DEMO.md)

CI ตั้งไว้ 6 jobs: Ubuntu/Windows/macOS × Python 3.9/3.13 โดย Ubuntu ติดตั้ง FFmpeg เพื่อทดสอบ integration; integration จะ skip เมื่อไม่มี FFmpeg/libass หากยังไม่มี run สำเร็จใน GitHub อย่านับเป็นผลผ่าน ดู badge และ Actions จาก repo จริง

ยังไม่ได้ลองติดตั้งกับ Claude Code หรือ ChatGPT/Claude เว็บแบบ end-to-end; ตรวจโครงสร้าง Skill และเส้นทางคัดลอกในเครื่องเท่านั้น
