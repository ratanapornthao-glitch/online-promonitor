"""Online Promonitor dashboard.

Reads only the files the agents wrote to data/output/, so it runs without an
API key (safe for public deployment on Streamlit Community Cloud).

Run: streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data" / "output"
METRICS = DATA / "metrics"
PLATFORMS = ["shopee", "lazada", "tiktok"]

st.set_page_config(page_title="Online Promonitor", page_icon="🔎", layout="wide")


@st.cache_data
def load(name: str) -> pd.DataFrame:
    path = METRICS / f"{name}.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


st.title("Online Promonitor")
st.caption("รู้โปรรู้เขา: ส่องโปรโมชันคู่แข่งข้าม Shopee, Lazada และ TikTok Shop เพื่อวางกลยุทธ์แคมเปญอัพเซลล์")

if not (DATA / "extracted.csv").exists():
    st.info("ยังไม่มีข้อมูล ใส่ screenshot ใน data/screenshots/<campaign>/ แล้วสั่ง Claude Code: \"รัน promonitor กับ <campaign>\"")
    st.stop()

extracted = pd.read_csv(DATA / "extracted.csv")
campaigns = sorted(extracted["campaign_name"].dropna().unique())
campaign = st.sidebar.selectbox("แคมเปญ", campaigns, index=len(campaigns) - 1)
brands = sorted(extracted["brand"].dropna().unique())
picked = st.sidebar.multiselect("แบรนด์คู่แข่ง", brands, default=brands)
camp_type = extracted.loc[extracted.campaign_name == campaign, "campaign_type"].iloc[0]
st.sidebar.markdown(f"**ประเภทแคมเปญ:** {camp_type}")
st.sidebar.markdown(f"**Screenshot ทั้งหมด:** {len(extracted)}")

c1, c2, c3 = st.columns(3)
c1.metric("Screenshot ในแคมเปญนี้", int((extracted.campaign_name == campaign).sum()))
review_path = DATA / "review_queue.csv"
c2.metric("รอคนตรวจ", len(pd.read_csv(review_path)) if review_path.exists() else 0)
run_log_path = DATA / "run_log.csv"
if run_log_path.exists():
    log = pd.read_csv(run_log_path)
    row = log[log.campaign_name == campaign]
    if len(row):
        mins = int(row.minutes_to_insight.iloc[0])
        c3.metric("Time to Insight", f"{mins} นาที", f"ทำมือ ~{int(row.manual_baseline_minutes.iloc[0]) // 60} ชม.",
                  delta_color="off")
    else:
        c3.metric("แบรนด์", len(picked))
else:
    c3.metric("แบรนด์", len(picked))

if (Path(__file__).parent / "data" / "synthetic_truth.csv").exists():
    st.warning("ข้อมูลในหน้านี้เป็นข้อมูลสังเคราะห์ (synthetic) สำหรับสาธิตระบบ แบรนด์ทั้งหมดเป็นชื่อสมมติ")

tab_brief, tab_campaign, tab_calendar, tab_channel, tab_upsell, tab_alert, tab_sim, tab_eval = st.tabs(
    ["สรุป Insight", "Campaign Pattern", "ปฏิทินโปรคู่แข่ง", "Channel Strategy", "กลไกอัพเซลล์",
     "สัญญาณเตือน", "Margin Simulator", "ความแม่นยำ Agent"])

with tab_brief:
    brief = DATA / "insights" / f"{campaign}.md"
    if brief.exists():
        st.markdown(brief.read_text(encoding="utf-8"))
    else:
        st.info("ยังไม่มี insight ของแคมเปญนี้ สั่ง analyst agent ใน Claude Code เพื่อสร้าง")

with tab_campaign:
    st.subheader("Campaign Uplift ตามประเภทแคมเปญ (pp เทียบวันปกติ)")
    by_type = load("uplift_by_type")
    if by_type.empty:
        st.info("ต้องมีข้อมูลวันปกติ (normal) ของ SKU เดียวกันก่อน จึงจะคำนวณได้")
    else:
        by_type = by_type[by_type.brand.isin(picked)].set_index("brand")
        st.bar_chart(by_type)
        st.dataframe(by_type, use_container_width=True)
    breadth = load("promo_breadth")
    if not breadth.empty:
        st.subheader("Promo Breadth: % ของรายการที่ร่วมโปร")
        b = breadth[(breadth.campaign_name == campaign) & breadth.brand.isin(picked)]
        st.bar_chart(b.set_index("brand")["promo_breadth_pct"])

with tab_calendar:
    st.subheader("Competitor Promo Calendar: ส่วนลดเฉลี่ยของแต่ละแคมเปญ (%)")
    cal = load("promo_calendar")
    if cal.empty:
        st.info("ยังไม่มีข้อมูลปฏิทิน รัน python src/analyze.py")
    else:
        cal = cal[cal.brand.isin(picked)]
        plat = st.radio("แพลตฟอร์ม", ["ทั้งหมด"] + PLATFORMS, horizontal=True, key="cal_platform")
        if plat != "ทั้งหมด":
            cal = cal[cal.platform == plat]
        cal = cal.assign(campaign=cal.start_date + " · " + cal.campaign_name)
        heat = cal.pivot_table(index="brand", columns="campaign", values="avg_discount_pct", aggfunc="mean")
        st.dataframe(heat.style.background_gradient(cmap="Reds", axis=None).format("{:.1f}"),
                     use_container_width=True)
        st.caption("แถว = คู่แข่ง, คอลัมน์ = แคมเปญเรียงตามวันที่ ใช้ดูจังหวะว่าใครอัดโปรหนักช่วงไหน")
        st.subheader("รายละเอียดต่อแคมเปญ")
        st.dataframe(cal.drop(columns="campaign"), use_container_width=True, hide_index=True)
    freq = load("promo_frequency")
    if not freq.empty:
        st.subheader("Promo Frequency: จำนวนแคมเปญที่เข้าร่วมต่อเดือน")
        f = freq[freq.brand.isin(picked)]
        st.dataframe(f.pivot_table(index=["brand", "platform"], columns="month",
                                   values="campaigns_joined", fill_value=0),
                     use_container_width=True)

with tab_channel:
    st.subheader("ส่วนลดเฉลี่ย: แบรนด์ × แพลตฟอร์ม")
    depth = load("channel_depth")
    if not depth.empty:
        d = depth[(depth.campaign_type == camp_type) & depth.brand.isin(picked)]
        heat = d.pivot(index="brand", columns="platform", values="avg_discount_pct").reindex(columns=PLATFORMS)
        st.dataframe(heat.style.background_gradient(cmap="Blues", axis=None).format("{:.1f}%"),
                     use_container_width=True)
    share = load("best_channel_share")
    if not share.empty:
        st.subheader("Best Channel Share: แพลตฟอร์มที่ถูกที่สุด (% ของ SKU)")
        s = share[(share.campaign_name == campaign) & share.brand.isin(picked)]
        st.dataframe(s.pivot(index="brand", columns="platform", values="best_channel_share_pct")
                      .reindex(columns=PLATFORMS).fillna(0), use_container_width=True)

with tab_upsell:
    mix = load("upsell_mix")
    if not mix.empty:
        st.subheader("Upsell Mechanic Mix")
        m = mix[(mix.campaign_type == camp_type) & mix.brand.isin(picked)]
        pivot = m.pivot_table(index=["brand", "platform"], columns="upsell_mechanic",
                              values="share_pct", fill_value=0)
        pivot.index = [f"{b} · {p}" for b, p in pivot.index]  # bar_chart needs a flat index
        st.bar_chart(pivot)
    thr = load("upsell_threshold")
    if not thr.empty:
        st.subheader("เกณฑ์ขั้นต่ำของโปรอัพเซลล์")
        st.dataframe(thr[(thr.campaign_type == camp_type) & thr.brand.isin(picked)],
                     use_container_width=True, hide_index=True)

with tab_alert:
    fake = load("fake_discount")
    st.subheader("ราคาเต็มถูกปรับขึ้นก่อนลด (อาจเป็น fake discount)")
    f = fake[(fake.campaign_name == campaign) & fake.brand.isin(picked)] if not fake.empty else fake
    if f.empty:
        st.success("ไม่พบในแคมเปญนี้")
    else:
        st.dataframe(f, use_container_width=True, hide_index=True)
    if review_path.exists():
        st.subheader("รายการที่ Agent ไม่มั่นใจ (รอคนตรวจ)")
        st.dataframe(pd.read_csv(review_path), use_container_width=True, hide_index=True)

with tab_sim:
    st.subheader("Price Match Margin Simulator")
    st.caption("กรอกตัวเลขของแบรนด์เราเอง (GP คู่แข่งไม่เปิดเผย ใช้เฉพาะของเรา) ค่าเริ่มต้นเป็นตัวอย่าง ไม่ใช่อัตราจริงของแพลตฟอร์ม")
    a, b = st.columns(2)
    list_price = a.number_input("ราคาเต็มของเรา (บาท)", min_value=1.0, value=590.0, step=10.0)
    cost = a.number_input("ต้นทุนสินค้าต่อชิ้น (บาท)", min_value=0.0, value=180.0, step=10.0)
    discount = b.slider("ส่วนลดที่จะให้ (%)", 0, 80, 30)
    st.markdown("**GP / ค่าธรรมเนียมรวมของแต่ละแพลตฟอร์ม (%)**")
    g = st.columns(3)
    gp = {p: g[i].number_input(p, min_value=0.0, max_value=60.0, value=[10.0, 10.0, 8.0][i],
                               step=0.5, key=f"gp_{p}") for i, p in enumerate(PLATFORMS)}
    price = list_price * (1 - discount / 100)
    sim = pd.DataFrame({
        "platform": PLATFORMS,
        "ราคาขาย": [price] * 3,
        "ค่า GP": [price * gp[p] / 100 for p in PLATFORMS],
    })
    sim["กำไรต่อชิ้น"] = sim["ราคาขาย"] - sim["ค่า GP"] - cost
    sim["margin_%"] = sim["กำไรต่อชิ้น"] / sim["ราคาขาย"] * 100
    st.dataframe(sim.set_index("platform").style.format("{:,.1f}"), use_container_width=True)
    best = sim.loc[sim["กำไรต่อชิ้น"].idxmax(), "platform"]
    st.info(f"ถ้าลด {discount}% เท่ากันทุกแพลตฟอร์ม {best} เหลือกำไรต่อชิ้นมากที่สุด")
    if (sim["กำไรต่อชิ้น"] < 0).any():
        st.error("ระดับส่วนลดนี้ขาดทุนในบางแพลตฟอร์ม")

with tab_eval:
    st.subheader("ความแม่นยำของ Agent เทียบ ground truth")
    ev = load("evaluation")
    if ev.empty:
        st.info("รัน python src/evaluate.py เพื่อสร้างผลประเมิน")
    else:
        acc = ev[ev.unit == "%"] if "unit" in ev else ev
        st.dataframe(acc, use_container_width=True, hide_index=True)
        if "unit" in ev:
            t = ev[ev.unit == "min"].set_index("field")["value"]
            if len(t) == 2:
                a, m = st.columns(2)
                a.metric("Agent (นาที/ภาพ)", f"{t.iloc[0]:.2f}")
                m.metric("ทำมือ (นาที/ภาพ)", f"{t.iloc[1]:.2f}")
