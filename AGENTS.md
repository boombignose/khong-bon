# ของบ่น

ชุดแจกภาษาไทยสำหรับสร้างคลิปสิ่งของพูดได้: Skill + ตัวอย่าง story.json + Prompt + ภาพตั้งต้น + ตัวประกอบคลิปในเครื่อง

- Python 3.9+ standard library; FFmpeg/ffprobe + libass ใช้เฉพาะ assemble
- รักษาบทไทยเดิมและภาพที่อนุมัติเมื่อแก้เฉพาะจุด
- `check` และ `pack` ไม่เรียก API หรือใช้เครดิต; ไม่มีการโพสต์อัตโนมัติ
- ไม่ทับโฟลเดอร์ pack/คลิป output เดิม และไม่แก้คลิป input
- ทดสอบ logic ผ่าน CLI/module surface; integration ประกอบคลิปจริงเมื่อมี FFmpeg
- รัน `python3 -m unittest discover -s tests -v` และ `python3 scripts/check_repo.py` ก่อนส่ง
- ระบุสถานะ media จากหลักฐานจริง แยก storyboard, AI render และผล QC อย่าอ้างว่าดู/ฟังแล้วจาก metadata
