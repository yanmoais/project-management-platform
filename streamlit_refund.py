import streamlit as st

# ===== 规则配置区域 =====

PROHIBITED_STATES = {
    "SC": [
        "California", "Connecticut", "Idaho", "Louisiana", "Michigan",
        "Montana", "Nevada", "New Jersey", "New York"
    ],
    "货币一": [
        "Arizona", "Arkansas", "Iowa", "Louisiana", "Maryland", "Michigan",
        "Montana", "Nevada", "South Carolina", "Tennessee", "Vermont", "Washington"
    ],
    "货币三": [
        "Delaware", "Louisiana", "Maryland", "Montana", "Tennessee", "Indiana",
        "Maine", "Texas", "Arizona", "Arkansas", "Iowa", "South Carolina",
        "Vermont", "Connecticut", "Virginia", "Utah", "South Dakota", "Michigan"
    ]
}

RISK_KEYWORDS = [
    "gambling", "fraud", "unauthorized", "chargeback",
    "dispute", "stolen", "illegal", "scam"
]

MIN_REFUND_AMOUNT = 200
MAX_REFUND_AMOUNT = 5000

# 美国全部州和地区
ALL_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
    # 地区
    "District of Columbia", "Puerto Rico", "Guam",
    "U.S. Virgin Islands", "American Samoa", "Northern Mariana Islands"
]

# ===== 核心判断逻辑 =====

def evaluate_refund(product, state, amount, claim_text):
    reasons = []

    # 第一步：判断是否为禁止州
    prohibited_list = PROHIBITED_STATES.get(product, [])
    if state not in prohibited_list:
        return "🟢 不需要退款处理", "green", [
            f"✅ 用户所在州（{state}）不属于 {product} 的禁止运营州",
            "📌 不进入退款流程"
        ]

    reasons.append(f"⚠️ 用户所在州（{state}）属于 {product} 的禁止运营州")

    # 第二步：判断充值金额
    if amount < MIN_REFUND_AMOUNT:
        reasons.append(f"✅ 充值金额（${amount:.2f}）未达到退款阈值（${MIN_REFUND_AMOUNT}）")
        return "🟢 不触发退款条件", "green", reasons

    if amount >= MAX_REFUND_AMOUNT:
        reasons.append(f"⚠️ 充值金额（${amount:.2f}）超过 ${MAX_REFUND_AMOUNT}，需人工介入")
        return "🟡 业务确认处理", "orange", reasons

    reasons.append(f"⚠️ 充值金额（${amount:.2f}）在退款判断区间内（${MIN_REFUND_AMOUNT} - ${MAX_REFUND_AMOUNT}）")

    # 第三步：判断关键词
    claim_lower = claim_text.lower()
    found_keywords = [kw for kw in RISK_KEYWORDS if kw in claim_lower]

    if not found_keywords:
        reasons.append("✅ 退款申请中未发现风险关键词")
        return "🟢 不触发退款条件", "green", reasons

    reasons.append(f"⚠️ 发现风险关键词：{', '.join(found_keywords)}")
    return "🔴 建议退款", "red", reasons


# ===== 页面界面 =====

st.title("退款决策辅助工具")
st.markdown("---")
st.markdown("#### 请填写以下信息")

product = st.selectbox("产品类别", options=list(PROHIBITED_STATES.keys()))

state = st.selectbox(
    "用户所在州",
    options=ALL_STATES,
    index=None,
    placeholder="输入或选择州名..."
)

amount = st.number_input(
    "充值金额（美元）",
    min_value=0.0,
    step=1.0,
    format="%.2f"
)

claim_text = st.text_area(
    "退款申请内容（直接粘贴原文）",
    height=150
)

st.markdown("---")

if st.button("开始判断", type="primary"):
    if not state:
        st.warning("⚠️ 请选择用户所在州")
    elif not claim_text:
        st.warning("⚠️ 请输入退款申请内容")
    else:
        decision, color, reasons = evaluate_refund(product, state, amount, claim_text)

        if color == "red":
            st.error(f"### 判断结果：{decision}")
        elif color == "orange":
            st.warning(f"### 判断结果：{decision}")
        else:
            st.success(f"### 判断结果：{decision}")

        st.markdown("#### 判断依据：")
        for r in reasons:
            st.markdown(f"- {r}")

        st.markdown("---")
        st.caption("⚠️ 本工具结果仅供参考，最终决定请结合具体情况由人工确认")
