# ของบ่น · ขอบเขตรุ่นแรก

ผู้ใช้ต้องการ public giveaway repo ที่เอาไปทำของตัวเองได้จริง: คลิปของใช้พูดได้ภาษาไทยด้วย ChatGPT / Claude และ Google Flow พร้อม Skill, ภาพตั้งต้น, ตัวอย่างบท/Prompt และตัวประกอบคลิป

ข้อมูลตอนอยู่ใน story.json จุดเดียว มีตัวละคร/ฉากร่วมกับ 3 ช็อต ช็อตละ 8 วินาที Python stdlib ตรวจข้อมูลก่อนเขียน pack และเรียก FFmpeg เฉพาะ assemble ใช้ module เดียวที่มี CLI check/pack/assemble ให้ใช้ได้ทั้งจาก repo และเมื่อคัดลอก Skill ไปติดตั้ง

สิ่งที่ต้องถึง: CLI, schema, Skill instructions, chat prompt, 4 examples, character images, font and license, README/Workflow, CI/tests, download ZIP และการตรวจ media จริง ต้องไม่ทับไฟล์เดิมหรือแก้ input clips

เลือกวิธีนี้เพราะสร้างชุดผลิตซ้ำได้โดยไม่ต้องให้ AI เขียนสคริปต์ใหม่ ไม่ทำแพลตฟอร์มหรือระบบควบคุม Flow บัญชี/ค่าเครดิต และการเผยแพร่ใช้ขอบเขตที่ผู้ใช้อนุญาต

เกณฑ์ส่ง: 4 ตัวอย่างผ่าน schema; pack ทุกตัวได้ไฟล์ครบและเปิด storyboard ได้; Skill ย้ายไปโฟลเดอร์อื่นแล้วยังรันได้; ประกอบคลิปพร้อม audio/Thai subtitles จริง; malformed input และไฟล์เดิมไม่เสีย; ลิงก์ในชุดครบ; ระบุสถานะ QC ตามหลักฐาน
