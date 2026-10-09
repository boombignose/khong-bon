# รูปแบบตอน

Python 3.9+ ใช้ standard library ไม่เรียก AI หรือ API โดยตรง ตัว AI เป็นคนเขียนบทและไฟล์ JSON สคริปต์ตรวจแล้วจัดชุดผลิตให้

```json
{
  "title": "แก้วโปรดที่ไม่เคยถูกล้าง",
  "character": {
    "name": "แก้วโปรด",
    "appearance": "An ivory ceramic mug with a mustard-yellow handle on camera-right, two oval eyes, expressive eyebrows and a simple mouth on its front. No arms or legs.",
    "voice": "Thai adult male voice, medium-low pitch, tired dry humor"
  },
  "setting": "A teal kitchen counter in a warm home kitchen",
  "scenes": [
    {"action": "Raises one eyebrow at camera", "camera": "Medium close-up, locked camera", "line": "เรียกผมว่าแก้วโปรด\nแต่ไม่เคยล้างผมเลย", "duration": 8},
    {"action": "Looks at the coffee stain then back to camera", "camera": "Gentle slow push-in", "line": "กาแฟหมดตั้งแต่เช้า\nคราบยังอยู่ถึงวันศุกร์", "duration": 8},
    {"action": "Pauses and holds an unimpressed expression", "camera": "Close-up, locked camera", "line": "ผมเป็นแก้วกาแฟ\nไม่ใช่โหลหมักครับ", "duration": 8}
  ]
}
```

ทุกช่องที่แสดงต้องมีข้อความ ไม่เกิน 2000 ตัวอักษร scenes ต้องมี 3 รายการ duration เป็นเลข 8 บทพูดไม่เกิน 85 ตัวอักษร แบ่งบรรทัดได้ด้วย JSON `\n` ห้ามวงเล็บปีกกาและ backslash ที่อยู่ในบทพูดจริง เพื่อไม่ให้กลายเป็นคำสั่งจัดรูปแบบ ASS

ยาว 24 วินาทีเป็นรูปแบบรุ่นแรก หากโมเดลที่เลือกไม่รองรับ 8 วินาที ให้ตัดคลิปใน editor ให้ตรงก่อนใช้ assemble ไม่เร่งหรือชะลอเสียงโดยอัตโนมัติ

ซับสร้างจากบท ไม่ใช่การถอดเสียง ตรวจเสียงจริงก่อนใช้ หากต้องปรับจังหวะรายคำหรือรายประโยค ให้แก้ SRT ใน editor การ assemble จะสร้าง ASS จาก story.json ใหม่ จึงไม่อ่านการแก้ไฟล์ SRT/ASS ใน pack
