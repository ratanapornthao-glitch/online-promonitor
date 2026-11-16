# Literature Review: วิธีและเครื่องมือที่มีอยู่สำหรับติดตามโปรโมชันคู่แข่ง

> ค้นข้อมูลเมื่อ 16 พ.ย. 2026 ราคาและฟีเจอร์ของเครื่องมือเชิงพาณิชย์เปลี่ยนบ่อย และหลายแหล่งเป็นเนื้อหาของผู้ขายเอง (ระบุไว้ในรายการอ้างอิง) จึงใช้เพื่อเทียบแนวทาง ไม่ใช่ราคาที่ยืนยันแล้ว

## 1. เกณฑ์ที่ใช้ประเมิน (มาจาก context และข้อจำกัดของโปรเจกต์)

ผู้ใช้คือ E-commerce Manager ของแบรนด์สกินแคร์ไทยขนาดกลาง ต้องเทียบโปรคู่แข่ง 5 แบรนด์บน 3 แพลตฟอร์มก่อนทุกแคมเปญ และเป็นงานวิชาการที่มีงบจำกัด จึงตั้งเกณฑ์ 8 ข้อ:

| # | เกณฑ์ | ทำไมสำคัญ (pain point ที่เกี่ยว) |
| --- | --- | --- |
| C1 | เห็นราคา/โปรของ **คู่แข่ง** ได้ | โจทย์หลักของโปรเจกต์ (1, 2) |
| C2 | ครอบคลุม **Shopee + Lazada + TikTok Shop** ในที่เดียว | ผู้ซื้อไทยกระจายอยู่ 3 แพลตฟอร์ม (5) |
| C3 | **แยกส่วนลดแบรนด์ออกจากของแพลตฟอร์ม** (โค้ดร้าน vs voucher/coins) | ประเมินความแรงโปรผิด (6) |
| C4 | จับ **กลไกอัพเซลล์** (เซ็ต, ครบ X ลด Y, ซื้อ 2, ของแถมตามยอด) และเกณฑ์ขั้นต่ำ | ออกแบบโปรอัพเซลล์แบบเดา (4) |
| C5 | อ่าน **ภาษาไทย** และ layout หน้าสินค้าได้ | ข้อมูลทั้งหมดอยู่ในหน้าเว็บภาษาไทย |
| C6 | **ไม่ต้อง scrape อัตโนมัติ** | ความเสี่ยงด้านข้อกำหนดแพลตฟอร์ม และเป็นงานวิชาการ |
| C7 | **ต้นทุนต่ำ** สำหรับแบรนด์กลาง/ทีมนักศึกษา | ข้อจำกัดงบ |
| C8 | มี **ข้อมูลย้อนหลังของเราเอง** ตรวจสอบย้อนกลับได้ | คาดการณ์จังหวะคู่แข่งไม่ได้, fake discount (3, 8) |

## 2. แนวทางที่มีอยู่

### A. ทำมือ: เปิดร้านคู่แข่งแล้วจดลง Excel (วิธีปัจจุบัน)
- **ข้อดี:** ไม่มีค่าใช้จ่าย เห็นทุกอย่างที่ลูกค้าเห็น ไม่ผิดข้อกำหนดแพลตฟอร์ม
- **ข้อเสีย:** ใช้ 2–3 วันต่อแคมเปญ ต้องทำซ้ำทุกเดือน ผลไม่สม่ำเสมอระหว่างคน มักนับ voucher แพลตฟอร์มรวมกับส่วนลดร้าน และไม่มีใครเทียบราคาเต็มกับวันปกติทุก SKU เพื่อจับ fake discount

### B. เครื่องมือของแพลตฟอร์มเอง (Seller Center)
- **Shopee Business Insights** แสดง GMV, ออเดอร์ และตัวชี้วัดของร้าน **เราเอง** แหล่งภายนอกหลายแห่งระบุว่าไม่มีข้อมูลคู่แข่ง เช่น ราคาหรือยอดขายของร้านอื่น [1][2]
- **Lazada Business Advisor** เป็นแดชบอร์ดผลประกอบการร้านและ SKU ของผู้ขาย (conversion rate, page views) [3][4] มีรายงานว่ามีแท็บ Market ที่แสดงอันดับหมวดหมู่และคีย์เวิร์ด แต่ยืนยันจากหน้าทางการไม่ได้ [5]
- **ข้อดี:** ฟรี ข้อมูลแม่นเพราะมาจากแพลตฟอร์มโดยตรง
- **ข้อเสีย:** ข้อมูลอยู่แยกกันคนละแพลตฟอร์ม และเน้นร้านของตัวเอง **ไม่ตอบคำถาม "คู่แข่งจัดโปรอะไร"**

### C. เว็บเปรียบเทียบราคา (เช่น Priceza)
- Priceza (ก่อตั้ง 2010) เป็น shopping search engine ให้ผู้บริโภคเทียบราคา รีวิว และดีล โดยร้านค้าส่งรายการสินค้าและราคาเข้าระบบ รายได้มาจาก performance-based marketing กับร้านค้า [6][7]
- **ข้อดี:** ฟรีสำหรับผู้ใช้ เห็นราคาหลายร้านในที่เดียว
- **ข้อเสีย:** ออกแบบมาให้ **ผู้ซื้อ** ไม่ใช่ทีมวางแคมเปญ แสดงราคาแต่ไม่แยกว่าส่วนลดชั้นไหนเป็นของใคร ไม่จัดประเภทกลไกอัพเซลล์ และความครอบคลุมขึ้นกับร้านที่ส่งข้อมูลเข้าระบบ

### D. SaaS วิเคราะห์ marketplace (เน้นยอดขายและสินค้าขายดี)
- **TikTok Shop:** Kalodata และ FastMoss ให้ข้อมูลสินค้า ครีเอเตอร์ และร้านค้า รองรับประเทศไทย [8][9] ราคาที่รายงานต่างกันมากตามแพ็กเกจและช่วงเวลา (ประมาณ $17–$499 ต่อเดือน) และรีวิวระบุว่าความแม่นยำ 100% ทำได้ยากเพราะไม่ใช่ข้อมูลทางการ [10][11]
- **Shopee:** มีเครื่องมืออย่าง Shopdora หรือ Zhixia ที่ประเมินยอดขายและรายได้ของคู่แข่ง [2][12]
- **ข้ามแพลตฟอร์ม:** BA3.studio เปิดตัว AI copilot ติดตามกิจกรรมและราคาคู่แข่งบน Shopee, TikTok Shop และ Lazada (ข่าวเดือน ส.ค. 2026 ยังไม่มีรีวิวอิสระ) [13]
- **ข้อดี:** ข้อมูลปริมาณมาก มี **ประมาณการยอดขาย** ซึ่งระบบเราไม่มี
- **ข้อเสีย:** ส่วนใหญ่แยกเครื่องมือตามแพลตฟอร์ม เน้นยอดขายและเทรนด์มากกว่าโครงสร้างโปรโมชัน ไม่พบว่าแยกส่วนลดแบรนด์/แพลตฟอร์ม หรือจัดประเภทกลไกอัพเซลล์ ค่าสมาชิกรายเดือนรวมหลายเครื่องมือสูงสำหรับแบรนด์กลาง และข้อมูลมาจากการเก็บอัตโนมัติที่ผู้ใช้ตรวจสอบเองไม่ได้

### E. ระบบติดตามราคา (price monitoring) และบริการ scraping
- **Prisync** ติดตามราคาและสต็อกคู่แข่งจาก URL มีแพ็กเกจเริ่มประมาณ $99 ต่อเดือนที่ 100 สินค้า [14][15] ทางเลือกอื่นมีตั้งแต่ประมาณ $29 ต่อเดือน (Minderest) ไปจนถึงระดับองค์กรประมาณ $1,000 ต่อเดือนขึ้นไป (Competera) ตามที่ผู้ขายรายหนึ่งรวบรวมไว้ [16] Priceva มีตัวติดตามราคา Lazada [17]
- **บริการ scraping** เช่น Actowiz หรือ actor บน Apify เก็บราคา ส่วนลด และโปรจาก Shopee/Lazada ได้ปริมาณมาก [18][19]
- **ข้อดี:** อัตโนมัติ ติดตามได้บ่อย ปริมาณมาก
- **ข้อเสีย:**
  - ออกแบบสำหรับ "ราคาเดียวต่อสินค้า" แบบเว็บร้านค้าทั่วไป ไม่ได้ออกแบบมาแยกชั้นส่วนลดซ้อนแบบ marketplace ไทย
  - แพลตฟอร์มใช้มาตรการกันบอต เช่น จำกัด IP, CAPTCHA และเปลี่ยนโครงสร้างหน้าบ่อย [20] ทำให้ต้องดูแลระบบต่อเนื่อง
  - ข้อกำหนดการใช้งานเรื่องการเก็บข้อมูลอัตโนมัติยังตีความต่างกันในแหล่งที่พบ (ส่วนใหญ่เป็นผู้ขายบริการ scraping เอง) [20][21] ต้องให้ฝ่ายกฎหมายประเมินก่อนใช้เชิงพาณิชย์ จึงไม่เหมาะกับงานวิชาการนี้

### F. OCR และ Document AI ทั่วไป
- **Tesseract** (โอเพนซอร์ส) รองรับภาษาไทยแต่มีข้อจำกัด: ภาษาไทยไม่เว้นวรรคระหว่างคำ มีสระและวรรณยุกต์ซ้อน มีตัวอักษรหน้าคล้ายกัน (ด/ต, บ/ป) และบรรทัดที่มีไทยปนอังกฤษอ่านได้ไม่ดี ความแม่นยำขึ้นกับคุณภาพภาพมาก [22][23]
- **Azure Document Intelligence (Read)** รองรับข้อความไทยแบบพิมพ์ [24] **Google Document AI** OCR รองรับมากกว่า 200 ภาษา (ขึ้นกับ processor ที่เลือก) [25]
- **ข้อดี:** อ่านภาพเป็นข้อความได้ บริการคลาวด์รองรับภาษาไทย ราคาต่อหน้าต่ำ
- **ข้อเสีย:** ได้ "ข้อความ" ไม่ได้ "ความหมาย" ยังต้องเขียนกฎเองว่าตัวเลขไหนคือราคาเต็ม ราคาขาย หรือโค้ดร้าน และโปรไหนเป็นของแพลตฟอร์ม ซึ่งแต่ละแพลตฟอร์มมี layout ต่างกันและเปลี่ยนบ่อย กฎจึงเปราะ

### G. งานวิจัย: เข้าใจเอกสารจากภาพโดยตรง (OCR-free / Vision-Language Model)
- **Donut** (OCR-free Document Understanding Transformer) อ่านเอกสารจากภาพโดยไม่ต้องใช้ OCR ภายนอก และทำผลได้ดีเทียบกับ LayoutLM/LayoutLMv2 ในงานดึงข้อมูลจากเอกสาร [26]
- Heyne et al. (2026) เทียบ LayoutLMv3, Donut และ Qwen3-VL บน RVL-CDIP พบว่าสำหรับเอกสาร layout ซับซ้อน **ข้อมูลจากภาพมีส่วนสำคัญที่สุด** ส่วนข้อความจาก OCR เป็นตัวช่วยรอง และโมเดล multimodal เฉพาะทางยังทำได้ดีกว่าแนวทางที่ใช้ LLM ในงานจัดประเภทเอกสาร [27]
- Shen et al. (2026) "OCR or Not?" ทดสอบกับชุดข้อมูลจริงขนาดใหญ่ พบว่า **multimodal LLM ที่อ่านภาพเอกสารโดยตรงทำได้ใกล้เคียงกับ pipeline แบบ OCR แล้วค่อยส่งให้โมเดล** จึงอาจไม่จำเป็นต้องมีขั้น OCR แยก [29]
- งาน benchmark ใบแจ้งหนี้ปี 2025 พบว่าแนวทางที่ดีที่สุดยังขึ้นกับลักษณะเอกสาร [28]
- มี **ThaiOCRBench** สำหรับวัด vision-language model บนงานภาษาไทยโดยเฉพาะ [23] แสดงว่าภาษาไทยยังเป็นโจทย์เฉพาะที่ต้องทดสอบ
- **นัยต่อโปรเจกต์:** หน้าสินค้า marketplace เป็นเอกสารที่ layout ซับซ้อน (ราคา, ป้าย, chip โปรหลายชั้น) จึงเหมาะกับแนวทางอ่านจากภาพโดยตรง แต่ผลขึ้นกับลักษณะเอกสาร ต้อง **วัดความแม่นยำกับข้อมูลของเราเอง** และมีกลไกตรวจทาน

## 3. ตารางเปรียบเทียบ

✅ ตอบโจทย์ · 🟡 บางส่วน · ❌ ไม่ตอบโจทย์

| แนวทาง | C1 คู่แข่ง | C2 3 แพลตฟอร์ม | C3 แยกชั้นส่วนลด | C4 อัพเซลล์ | C5 ภาษาไทย | C6 ไม่ scrape | C7 ต้นทุนต่ำ | C8 ข้อมูลย้อนหลังของเรา |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. ทำมือ + Excel | ✅ | ✅ | 🟡 ขึ้นกับคน | 🟡 ขึ้นกับคน | ✅ | ✅ | 🟡 ฟรีแต่เสียเวลาคน 2–3 วัน | 🟡 ไม่เป็นระบบ |
| B. Seller Center | ❌ | ❌ แยกกัน | ❌ | ❌ | ✅ | ✅ | ✅ | 🟡 เฉพาะร้านเรา |
| C. เว็บเทียบราคา | 🟡 | 🟡 | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| D. SaaS marketplace | ✅ | 🟡 ส่วนใหญ่แยกเครื่องมือ | ❌ ไม่พบ | 🟡 | 🟡 | ❌ | 🟡/❌ | 🟡 ข้อมูลของผู้ขาย |
| E. Price monitoring / scraping | ✅ | 🟡 | ❌ | ❌ | 🟡 | ❌ | ❌ | ✅ |
| F. OCR / Document AI | 🟡 ต้องมีภาพ | ✅ | ❌ ต้องเขียนกฎเอง | ❌ | 🟡 | ✅ | ✅ | ✅ |
| **H. Online Promonitor** (Vision LLM agent + validation + คนตรวจ) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ แคปด้วยมือ | ✅ | ✅ |

## 4. สรุป: ทำไมเลือกแนวทางนี้

1. **ช่องว่างที่ยังไม่มีใครเติม:** ไม่พบเครื่องมือที่ทำครบ 3 อย่างพร้อมกัน คือ (a) เห็นโปรคู่แข่งบนทั้ง 3 แพลตฟอร์ม (b) แยกส่วนลดของแบรนด์ออกจากของแพลตฟอร์ม (c) จัดประเภทกลไกอัพเซลล์พร้อมยอดขั้นต่ำ ซึ่งเป็นข้อมูลที่ทีมต้องใช้วางแคมเปญอัพเซลล์โดยตรง
2. **เหมาะกับข้อจำกัด:** การแคปหน้าจอด้วยมือในปริมาณน้อย (20–60 ภาพต่อแคมเปญ) เลี่ยงความเสี่ยงเรื่อง scraping ไม่ต้องดูแลระบบกันบอต และต้นทุนต่ำ
3. **เทคนิคมีหลักฐานรองรับ:** งานวิจัยชี้ว่าข้อมูลจากภาพสำคัญที่สุดสำหรับเอกสาร layout ซับซ้อน และ multimodal LLM อ่านภาพโดยตรงได้ใกล้เคียง pipeline ที่มี OCR [26][27][29] แต่ผลยังขึ้นกับชนิดเอกสาร [28] โปรเจกต์จึงใส่ **Validation (Pydantic) + Human Review + การวัดผลเทียบ ground truth** ไว้ใน flow ไม่เชื่อ LLM อย่างเดียว
4. **สิ่งที่ยอมแลก:** ยังต้องใช้คนแคปหน้าจอ ไม่มีประมาณการยอดขายแบบ SaaS กลุ่ม D และความแม่นยำบนหน้าจริงต้องวัดเพิ่ม (ดู `docs/real_data_pilot.md`)

## 5. ข้อมูลประกอบ Rationale (ขนาดตลาด)

- e-commerce บนแพลตฟอร์มในอาเซียนปี 2025 มีมูลค่า **US$157.6 พันล้าน** โต **22.8%** และ Shopee, Lazada, TikTok Shop รวมกันครองตลาดประมาณ **98.8%** [30]
- **ไทยโตเร็วที่สุดในภูมิภาค +51.8%** ต่อปี [30] มูลค่าตลาดไทยปี 2025 ประมาณ **US$35.5 พันล้าน** Shopee ยังครองมากกว่า 50% ในไทย TikTok Shop กำลังไล่ทัน ส่วน Lazada ปรับไปเน้นแบรนด์และสินค้าพรีเมียม [32]

### ส่วนแบ่งตลาดเฉพาะประเทศไทย (ส่วนแบ่ง GMV ของ 3 แพลตฟอร์มรวมกัน)

ข้อมูลจาก Cube (ชุดข้อมูล Tradewinds ประมาณ GMV สินค้าที่จับต้องได้บน 3 แพลตฟอร์ม เผยแพร่ 13 ต.ค. 2026) [33]

| ช่วงเวลา | Shopee | TikTok Shop | Lazada |
| --- | --- | --- | --- |
| Q1 2025 | 50% | 35% | 15% |
| Q2 2025 | 56% | 30% | 14% |
| Q3 2025 | 54% | 36% | 10% |
| Q4 2025 | 49% | 43% | 8% |
| Q1 2026 | 48% | 45% | 8% |
| **Q2 2026** | **45%** | **48%** | **7%** |

- ทั้งปี 2025 Shopee ครองประมาณ **52%** มูลค่ารวม 3 แพลตฟอร์มปี 2025 = US$30.7 พันล้าน (+21%) [33]
- **Q2 2026 เป็นไตรมาสแรกที่ TikTok Shop แซง Shopee ในไทย** (US$5.3 พันล้าน vs US$4.9 พันล้าน) แต่ Shopee ยังมีจำนวนออเดอร์มากกว่า และครึ่งปีแรก 2026 ทั้งคู่เสมอกันที่ 46% [33]
- ตัวเลขมูลค่ารวมของ Momentum Works (US$35.5 พันล้าน) กับ Cube (US$30.7 พันล้าน) ต่างกัน เพราะนับขอบเขตต่างกัน (Cube นับเฉพาะสินค้าที่จับต้องได้บน 3 แพลตฟอร์ม) ทั้งสองเป็น **ค่าประมาณของบริษัทวิจัย** ไม่ใช่ตัวเลขที่แพลตฟอร์มเปิดเผยเอง

**ตัวเลขที่ไม่ควรใช้เป็นส่วนแบ่งตลาด**
- "Shopee 50% / TikTok Shop 32% / Lazada 18% (ปี 2025)" ถูกอ้างต่อกันในบทความหลายแห่ง แต่ไม่ระบุว่าวัดอะไร (GMV, ออเดอร์ หรือผู้ใช้) [34]
- "Shopee 89% / TikTok Shop 71% / Lazada 66%" เป็น **สัดส่วนผู้ตอบแบบสำรวจที่ใช้แต่ละแพลตฟอร์ม** (ตอบได้หลายข้อ รวมเกิน 100%) ไม่ใช่ส่วนแบ่งยอดขาย [35]

**นัยต่อโปรเจกต์**
- ต้องติดตาม **ทั้ง 3 แพลตฟอร์ม** จึงจะครอบคลุมเกือบทั้งตลาด และตลาดที่โตเร็วทำให้การแข่งขันด้านโปรโมชันรุนแรงขึ้น
- **TikTok Shop ส่วนแบ่งเปลี่ยนเร็วมาก** (30% → 48% ใน 5 ไตรมาส) การดูแค่ Shopee แบบเดิมจะพลาดสนามที่คู่แข่งกำลังย้ายงบโปรไป ตรงกับเรื่อง Hadaso ที่ลดแรงสุดบน TikTok ในข้อมูลสาธิต
- **Lazada ส่วนแบ่งลดลง แต่เน้นแบรนด์ (LazMall)** ยังสำคัญสำหรับแบรนด์สกินแคร์ที่ขายผ่านร้าน official

## รายการอ้างอิง

ประเภทแหล่ง: **[P]** แหล่งปฐมภูมิ/ทางการ · **[R]** งานวิจัย · **[S]** สื่อ/บทความอิสระ · **[V]** เนื้อหาของผู้ขายหรือ affiliate (ใช้ด้วยความระวัง)

1. [V] Easy Data, "Beyond Shopee Business Insights" — https://dev.to/easydata/beyond-shopee-business-insights-how-external-data-gives-you-an-edge-2j2n
2. [V] Shopdora, "The Shopee Analytics Tool That Finally Shows What Your Competitors Are Doing" — https://blog.shopdora.com/en/page/the-shopee-analytics-tool-that-finally-shows-what-your-competitors-are-doing
3. [P] Lazada Seller Community (PH), Business Advisor data — https://community.lazada.com.ph/post/does-the-display-data-and-visitor-data-in-the-business-advisor-not-include-the-data-in-seller-picks-and-paid-promotion-3ea
4. [S] Philstar, "Online sellers can make data-driven decisions easier — Lazada's metrics" (2024) — https://philstar.com/business-life/2024/08/07/2375622/online-sellers-can-make-data-driven-decisions-easier-lazadas-metrics
5. [S] JeopardyLabs, Lazada training quiz (ยืนยันจากหน้าทางการไม่ได้) — https://jeopardylabs.com/play/week-1-topics-laz-cebu
6. [P] Priceza Group, About — https://www.pricezagroup.com/en/about
7. [S] Wikipedia, Priceza — https://www.wikipedia.org/wiki/Priceza
8. [P] Kalodata Knowledge Base (ประเทศที่รองรับ) — https://www.kalodata.com/knowledge.html
9. [S] Capterra, FastMoss — https://www.capterra.com.sg/software/1091830/FastMoss
10. [V] Hubfluence, "Kalodata vs FastMoss" (ต.ค. 2026) — https://www.hubfluence.io/blog/kalodata-vs-fastmoss
11. [V] Tabcut, "Kalodata vs FastMoss" — https://www.tabcut.com/blog/post/kalodata-vs-fastmoss-which-tiktok-shop-analytics-tool-is-better
12. [V] Shopdora, "What is Zhixia?" — https://blog.shopdora.com/en/page/what-is-zhixia-complete-guide-to-shopee-analytics-tool
13. [S] AIToolly, BA3.studio launches AI copilot (ส.ค. 2026) — https://aitoolly.com/en/ai-news/article/2026-08-22-ba3studio-launches-ai-copilot-to-help-southeast-asian-brands-track-competitors-across-shopee-tiktok
14. [P] Prisync, Compare plans — https://prisync.com/compare-plans
15. [S] Toolradar, Prisync pricing — https://toolradar.com/tools/prisync/pricing
16. [V] Priceva, "Top 10 Prisync Alternatives in 2026" — https://priceva.com/blog/prisync-alternatives
17. [V] Priceva, Lazada Price Tracker — https://priceva.com/lazada-price-tracker
18. [V] Actowiz Solutions, Shopee vs Lazada marketplace data — https://www.actowizsolutions.com/shopee-vs-lazada-marketplace-data.php
19. [V] Apify, Shopee Scraper actor — https://apify.com/bnzz/shopee-scraper.md
20. [V] Pixelscan, "Shopee scraping guide" (มาตรการกันบอต) — https://pixelscan.net/blog/shopee-scraping-guide/
21. [V] Scrapeless, "Is scraping Shopee legal" — https://browserless.scrapeless.com/en/blog/is-scraping-shopee-legal
22. [S] Tesseract OCR mailing list, "Experiment with Thai language" — https://groups.google.com/g/tesseract-ocr/c/R4V3Sw2UFrk/m/V0xFC81nBAAJ
23. [R] ThaiOCRBench: A Task-Diverse Benchmark for Vision-Language Understanding in Thai (บทสรุป) — https://www.themoonlight.io/review/thaiocrbench-a-task-diverse-benchmark-for-vision-language-understanding-in-thai
24. [P] Microsoft Learn, Azure AI Vision language support — https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/language-support
25. [S] Stack Overflow, "Does Google Document AI support Thai language" — https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/72386879/does-google-document-ai-support-thai-language
26. [R] Kim et al., "OCR-free Document Understanding Transformer" (Donut) — https://arxiv.org/pdf/2111.15664
27. [R] Heyne et al., "Multimodal Approaches for Visually-Rich Document Type Classification: A Comparative Analysis" (2026), arXiv:2606.02162 — https://arxiv.org/abs/2606.02162
28. [R] "Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Strategies for Invoice Processing" (2025), arXiv:2509.04469 — https://arxiv.org/html/2509.04469v1
29. [R] Shen et al., "OCR or Not? Rethinking Document Information Extraction in the MLLMs Era with Real-World Large-Scale Datasets" (2026), arXiv:2603.02789 — https://arxiv.org/abs/2603.02789
30. [P] Momentum Works, "Southeast Asia's platform ecommerce reaches US$157.6B in 2025" (14 เม.ย. 2026) — https://thelowdown.momentum.asia/new-report-southeast-asias-platform-ecommerce-reaches-us157-6b-in-2025-with-top-platforms-expanding-share-to-98-8/
31. [S] MarketingOops (อ้างรายงาน Momentum Works) — https://www.marketingoops.com/?p=373302
32. [S] Bangkok Post, "Thailand driving e-commerce growth" อ้างรายงาน Momentum Works "Ecommerce in Southeast Asia 2026" (เผยแพร่ซ้ำโดย AEC VCCI, 20 เม.ย. 2026) — https://www.bangkokpost.com/business/general/3239004/thailand-driving-ecommerce-growth · https://en.aecvcci.vn/tin-tuc-n15259/thailand-driving-e-commerce-growth.htm
33. [P] Cube Asia, "E-commerce in Thailand: Market Data, Platform Breakdown, and What Brands Need to Know in 2026" (Tradewinds H1 2026, 13 ต.ค. 2026) — https://cube.asia/ecommerce-in-thailand/
34. [S] AnyMind Group, "[2026 Local Data] Comparing Thailand's Top 3 E-commerce Platforms" (1 ก.ค. 2026) — https://note.com/anymindgroup/n/n75cc4480a32e?hl=en
35. [S] Brand Inside, ผลสำรวจ Milieu Insight: TikTok Shop นิยมอันดับ 2 รองจาก Shopee — https://brandinside.asia/milieu-insight-poll-tiktok-shop-no-2-in-thailand/
