import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Villa Payment Dashboard", layout="wide", page_icon="🏠")

st.markdown("""
<style>
    .main { background-color: #1a1a2e; }
    .kpi-card {
        background: linear-gradient(135deg, #16213e, #0f3460);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #e94560;
        margin: 5px;
    }
    .kpi-value { font-size: 28px; font-weight: bold; color: #e94560; }
    .kpi-label { font-size: 14px; color: #a8a8b3; margin-top: 5px; }
    .section-title {
        font-size: 18px; font-weight: bold; color: white;
        background: #0f3460; padding: 10px 15px;
        border-radius: 8px; margin: 15px 0 10px 0;
        border-left: 4px solid #e94560;
    }
</style>
""", unsafe_allow_html=True)

# ====== Constants ======
DEDUCTION = 2000
CURRENT_MONTH = datetime.today().month

MONTH_ORDER = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']

SHAREHOLDERS = {
    "V1": {"1000": 0.24, "2000": 0.14, "3000": 0.20, "4000": 0.18, "5000": 0.24},
    "V2": {"1000": 0.24, "2000": 0.14, "3000": 0.20, "4000": 0.18, "5000": 0.24},
    "V3": {"1000": 0.25, "2000": 0.00, "3000": 0.20, "4000": 0.00, "5000": 0.25, "6000": 0.30},
    "V4": {"1000": 0.25, "2000": 0.00, "3000": 0.20, "4000": 0.25, "5000": 0.05, "6000": 0.25},
    "V5": {"1000": 0.10, "2000": 0.10, "3000": 0.15, "4000": 0.20, "5000": 0.13, "6000": 0.15, "7000": 0.13, "8000": 0.05},
    "V6": {"1000": 0.25, "2000": 0.10, "3000": 0.10, "4000": 0.20, "5000": 0.10, "6000": 0.10, "7000": 0.10, "8000": 0.05},
    "V7": {"1000": 0.35, "2000": 0.10, "3000": 0.10, "4000": 0.20, "5000": 0.10, "6000": 0.10, "7000": 0.05},
}

# كل الـ shareholder codes الموجودة
ALL_SH_CODES = sorted(set(code for v in SHAREHOLDERS.values() for code in v.keys()), key=lambda x: int(x))

def sort_month_cols(cols, fixed, ending):
    month_cols = [c for c in cols if c not in fixed + ending]
    return sorted(
        month_cols,
        key=lambda x: MONTH_ORDER.index(
            next((m for m in MONTH_ORDER if m[:3] == x.split('-')[0]), None) or 'ZZZ'
        ) if '-' in x else 99
    )

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df['PAYMENT DETAILS '] = pd.to_datetime(df['PAYMENT DETAILS '])
    df['Year']        = df['PAYMENT DETAILS '].dt.year
    df['Month Num']   = df['PAYMENT DETAILS '].dt.month
    df['Month Name']  = df['PAYMENT DETAILS '].dt.strftime('%B')
    df['Period']      = df['PAYMENT DETAILS '].dt.strftime('%B %Y')
    df['Period_Sort'] = df['PAYMENT DETAILS '].dt.to_period('M')
    return df

def fmt(x):
    if isinstance(x, (int, float)):
        if x == int(x):
            return f"{int(x):,}"
        return f"{x:,.2f}"
    return x

st.markdown("# 🏠 Villa Payment Dashboard")
st.markdown("---")

uploaded_file = st.file_uploader("📂 ارفع ملف Excel", type=["xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)

    tab1, tab2 = st.tabs(["📋 الجدول التفصيلي", "👥 Monthly Collections"])

    # ==========================================
    # TAB 1
    # ==========================================
    with tab1:
        st.markdown('<div class="section-title">🔍 الفلاتر</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            years = sorted(df['Year'].unique())
            selected_years = st.multiselect("📅 السنة", options=years, default=years, key="tab1_years")
            if not selected_years:
                selected_years = years

        with col2:
            villas = sorted(df['villa No.'].unique())
            selected_villas = st.multiselect("🏠 الفيلا", options=villas, default=villas, key="tab1_villas")
            if not selected_villas:
                selected_villas = villas

        with col3:
            months = df[df['Year'].isin(selected_years)]['Month Name'].unique()
            months_sorted = sorted(months, key=lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99)
            selected_months = st.multiselect("🗓️ الشهر", options=months_sorted, default=list(months_sorted), key="tab1_months")
            if not selected_months:
                selected_months = list(months_sorted)

        filtered = df[
            df['Year'].isin(selected_years) &
            df['villa No.'].isin(selected_villas) &
            df['Month Name'].isin(selected_months)
        ]

        st.markdown("---")
        st.markdown('<div class="section-title">💰 ملخص</div>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)

        total_amount   = filtered['AMOUNT'].sum()
        num_villas     = filtered['villa No.'].nunique()
        num_months_kpi = filtered['Period'].nunique()
        avg_per_villa  = total_amount / num_villas if num_villas > 0 else 0

        with k1:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-value">{total_amount:,}</div>
                <div class="kpi-label">💰 إجمالي المدفوعات</div>
            </div>""", unsafe_allow_html=True)
        with k2:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-value">{num_villas}</div>
                <div class="kpi-label">🏠 عدد الفيلات</div>
            </div>""", unsafe_allow_html=True)
        with k3:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-value">{num_months_kpi}</div>
                <div class="kpi-label">🗓️ عدد الأشهر</div>
            </div>""", unsafe_allow_html=True)
        with k4:
            st.markdown(f"""<div class="kpi-card">
                <div class="kpi-value">{avg_per_villa:,.0f}</div>
                <div class="kpi-label">📊 متوسط لكل فيلا</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-title">📋 الجدول التفصيلي</div>', unsafe_allow_html=True)

        for villa in sorted(filtered['villa No.'].unique()):
            villa_df = filtered[filtered['villa No.'] == villa]
            st.markdown(f"#### 🏠 Villa {villa}")

            for year in sorted(villa_df['Year'].unique()):
                year_df = villa_df[villa_df['Year'] == year]
                result = (
                    year_df.groupby(['Period_Sort', 'Period'])['AMOUNT']
                    .sum().reset_index().sort_values('Period_Sort')
                )[['Period', 'AMOUNT']].rename(columns={'Period': 'الشهر', 'AMOUNT': 'SUM Amount'})
                total_row = pd.DataFrame(
                    [['إجمالي ' + str(year), result['SUM Amount'].sum()]],
                    columns=['الشهر', 'SUM Amount']
                )
                result = pd.concat([result, total_row], ignore_index=True)
                with st.expander(f"📅 سنة {year} — إجمالي: {year_df['AMOUNT'].sum():,}"):
                    st.dataframe(result, use_container_width=True, hide_index=True)

            st.markdown(f"**💰 إجمالي Villa {villa} الكلي: {villa_df['AMOUNT'].sum():,}**")
            st.markdown("---")

        def generate_excel(df_filtered):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for villa in sorted(df_filtered['villa No.'].unique()):
                    villa_df = df_filtered[df_filtered['villa No.'] == villa]
                    all_data = []
                    for year in sorted(villa_df['Year'].unique()):
                        year_df = villa_df[villa_df['Year'] == year]
                        result = (
                            year_df.groupby(['Period_Sort', 'Period'])['AMOUNT']
                            .sum().reset_index().sort_values('Period_Sort')
                        )[['Period', 'AMOUNT']].rename(columns={'Period': 'الشهر', 'AMOUNT': 'SUM Amount'})
                        result.insert(0, 'السنة', '')
                        result.at[result.index[0], 'السنة'] = str(year)
                        total_row = pd.DataFrame(
                            [['', 'إجمالي ' + str(year), result['SUM Amount'].sum()]],
                            columns=['السنة', 'الشهر', 'SUM Amount']
                        )
                        result = pd.concat([result, total_row], ignore_index=True)
                        separator = pd.DataFrame([['', '', '']], columns=['السنة', 'الشهر', 'SUM Amount'])
                        all_data.extend([result, separator])
                    grand = pd.DataFrame(
                        [['', 'الإجمالي الكلي', villa_df['AMOUNT'].sum()]],
                        columns=['السنة', 'الشهر', 'SUM Amount']
                    )
                    all_data.append(grand)
                    pd.concat(all_data, ignore_index=True).to_excel(
                        writer, sheet_name=f"Villa {villa}", index=False
                    )
            return output.getvalue()

        st.markdown('<div class="section-title">⬇️ تحميل النتائج</div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️ تحميل Excel",
            data=generate_excel(filtered),
            file_name="villa_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ==========================================
    # TAB 2 - Monthly Collections
    # ==========================================
    with tab2:
        st.markdown('<div class="section-title">🔍 فلتر السنة</div>', unsafe_allow_html=True)

        all_years = sorted(df['Year'].unique())
        selected_year_sh = st.selectbox("📅 اختر السنة", options=all_years,
                                         index=len(all_years)-1, key="tab2_year")

        df_year = df[df['Year'] == selected_year_sh]

        available_months = sorted(
            df_year['Month Name'].unique(),
            key=lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99
        )

        st.markdown(f"ℹ️ الشهر الحالي: **{MONTH_ORDER[CURRENT_MONTH-1]}** — خصم ثابت لكل شهر: **{DEDUCTION:,}**")
        st.markdown("---")

        villa_map = {i+1: f"V{i+1}" for i in range(7)}

        # ====== حساب بيانات كل فيلا ======
        # sh_monthly_data[sh_code][month_label] = مجموع نصيب الشخص من كل الفيلات
        sh_monthly_data = {code: {} for code in ALL_SH_CODES}

        st.markdown('<div class="section-title">👥 Monthly Collections - per Villa</div>', unsafe_allow_html=True)

        for villa_num in sorted(df_year['villa No.'].unique()):
            villa_key = villa_map.get(villa_num)
            if not villa_key or villa_key not in SHAREHOLDERS:
                continue

            villa_df     = df_year[df_year['villa No.'] == villa_num]
            shareholders = SHAREHOLDERS[villa_key]

            monthly_totals = (
                villa_df.groupby(['Month Num', 'Month Name'])['AMOUNT']
                .sum().reset_index()
            )
            monthly_totals['Month Order'] = monthly_totals['Month Name'].apply(
                lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99
            )
            monthly_totals = monthly_totals.sort_values('Month Order')
            monthly_totals = monthly_totals[monthly_totals['Month Name'].isin(available_months)]

            months_cols  = monthly_totals['Month Name'].tolist()
            months_nums  = monthly_totals['Month Num'].tolist()
            months_label = [f"{m[:3]}-{str(selected_year_sh)[2:]}" for m in months_cols]

            def get_net(month_name, mt=monthly_totals):
                row = mt[mt['Month Name'] == month_name]['AMOUNT'].values
                raw = int(row[0]) if len(row) > 0 else 0
                return max(raw - DEDUCTION, 0)

            rows = []

            # صف Checks Collectives
            cc_row = {"Month": "Checks Collectives", "ShareHolders": "", "%": ""}
            total_sum = current_sum = current_plus1_sum = 0

            for i, m in enumerate(months_cols):
                raw_val = int(monthly_totals[monthly_totals['Month Name'] == m]['AMOUNT'].values[0])
                net_val = max(raw_val - DEDUCTION, 0)
                cc_row[months_label[i]] = net_val
                total_sum += net_val
                m_num = months_nums[i]
                if m_num >= CURRENT_MONTH: current_sum += net_val
                if m_num >  CURRENT_MONTH: current_plus1_sum += net_val

            cc_row["الإجمالي"]  = total_sum
            cc_row["Current"]   = current_sum
            cc_row["Current+1"] = current_plus1_sum
            rows.append(cc_row)

            # صفوف الـ Shareholders
            for sh_code, sh_pct in shareholders.items():
                sh_row = {
                    "Month": villa_key,
                    "ShareHolders": sh_code,
                    "%": f"{int(sh_pct*100)}%"
                }
                sh_total = sh_current = sh_current_plus1 = 0

                for i, m in enumerate(months_cols):
                    net_val = get_net(m)
                    if sh_pct > 0:
                        sh_val = round(net_val * sh_pct, 2)
                        sh_row[months_label[i]] = sh_val
                        sh_total += sh_val
                        m_num = months_nums[i]
                        if m_num >= CURRENT_MONTH: sh_current += sh_val
                        if m_num >  CURRENT_MONTH: sh_current_plus1 += sh_val
                        # تجميع للـ Monthly Collections الكلي
                        sh_monthly_data[sh_code][months_label[i]] = \
                            sh_monthly_data[sh_code].get(months_label[i], 0) + sh_val
                    else:
                        sh_row[months_label[i]] = "-"

                sh_row["الإجمالي"]  = round(sh_total, 2)         if sh_pct > 0 else "-"
                sh_row["Current"]   = round(sh_current, 2)       if sh_pct > 0 else "-"
                sh_row["Current+1"] = round(sh_current_plus1, 2) if sh_pct > 0 else "-"
                rows.append(sh_row)

            result_df = pd.DataFrame(rows)
            fixed_cols  = ["Month", "ShareHolders", "%"]
            ending_cols = ["الإجمالي", "Current", "Current+1"]
            month_cols_sorted = sort_month_cols(result_df.columns.tolist(), fixed_cols, ending_cols)
            result_df = result_df[fixed_cols + month_cols_sorted + ending_cols]

            for col in month_cols_sorted + ending_cols:
                if col in result_df.columns:
                    result_df[col] = result_df[col].apply(fmt)

            def style_rows(row):
                if row["Month"] == "Checks Collectives":
                    return ['background-color: #f4a261; color: black; font-weight: bold'] * len(row)
                return ['background-color: #1e3a5f; color: white'] * len(row)

            styled = result_df.style.apply(style_rows, axis=1)

            with st.expander(f"🏠 {villa_key} — إجمالي {selected_year_sh}: {villa_df['AMOUNT'].sum():,}", expanded=True):
                st.dataframe(styled, use_container_width=True, hide_index=True)

        # ====== جدول Monthly Collections الكلي ======
        st.markdown("---")
        st.markdown('<div class="section-title">📊 Monthly Collections - All Villas Combined</div>', unsafe_allow_html=True)

        all_month_labels = sorted(
            set(lbl for data in sh_monthly_data.values() for lbl in data.keys()),
            key=lambda x: MONTH_ORDER.index(
                next((m for m in MONTH_ORDER if m[:3] == x.split('-')[0]), None) or 'ZZZ'
            ) if '-' in x else 99
        )

        # إعادة حساب month_nums للـ current
        def label_to_month_num(lbl):
            for i, m in enumerate(MONTH_ORDER):
                if m[:3] == lbl.split('-')[0]:
                    return i + 1
            return 99

        combined_rows = []
        grand_total_row = {"ShareHolders": "الإجمالي الكلي", "%": ""}
        grand_totals = {lbl: 0 for lbl in all_month_labels}
        grand_total_sum = grand_current = grand_current_plus1 = 0

        for sh_code in ALL_SH_CODES:
            data = sh_monthly_data[sh_code]
            if not any(v > 0 for v in data.values()):
                continue

            row = {"ShareHolders": sh_code, "%": ""}
            row_total = row_current = row_current_plus1 = 0

            for lbl in all_month_labels:
                val = round(data.get(lbl, 0), 2)
                row[lbl] = val
                row_total += val
                m_num = label_to_month_num(lbl)
                if m_num >= CURRENT_MONTH: row_current += val
                if m_num >  CURRENT_MONTH: row_current_plus1 += val
                grand_totals[lbl] = grand_totals.get(lbl, 0) + val

            row["الإجمالي"]  = round(row_total, 2)
            row["Current"]   = round(row_current, 2)
            row["Current+1"] = round(row_current_plus1, 2)
            grand_total_sum      += row_total
            grand_current        += row_current
            grand_current_plus1  += row_current_plus1
            combined_rows.append(row)

        # صف الإجمالي الكلي
        for lbl in all_month_labels:
            grand_total_row[lbl] = round(grand_totals[lbl], 2)
        grand_total_row["الإجمالي"]  = round(grand_total_sum, 2)
        grand_total_row["Current"]   = round(grand_current, 2)
        grand_total_row["Current+1"] = round(grand_current_plus1, 2)
        combined_rows.append(grand_total_row)

        combined_df = pd.DataFrame(combined_rows)
        fixed_cols  = ["ShareHolders", "%"]
        ending_cols = ["الإجمالي", "Current", "Current+1"]
        month_cols_sorted_c = sort_month_cols(combined_df.columns.tolist(), fixed_cols, ending_cols)
        combined_df = combined_df[fixed_cols + month_cols_sorted_c + ending_cols]

        for col in month_cols_sorted_c + ending_cols:
            if col in combined_df.columns:
                combined_df[col] = combined_df[col].apply(fmt)

        def style_combined(row):
            if row["ShareHolders"] == "الإجمالي الكلي":
                return ['background-color: #f4a261; color: black; font-weight: bold'] * len(row)
            return ['background-color: #1e3a5f; color: white'] * len(row)

        styled_combined = combined_df.style.apply(style_combined, axis=1)
        st.dataframe(styled_combined, use_container_width=True, hide_index=True)

        # ====== Download ======
        st.markdown("---")
        st.markdown('<div class="section-title">⬇️ تحميل Monthly Collections</div>', unsafe_allow_html=True)

        def generate_collections_excel(df_data, year):
            output = BytesIO()
            villa_map_local = {i+1: f"V{i+1}" for i in range(7)}
            df_yr  = df_data[df_data['Year'] == year]
            avail  = sorted(df_yr['Month Name'].unique(),
                            key=lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99)

            sh_monthly_xl = {code: {} for code in ALL_SH_CODES}

            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                all_rows = []
                for villa_num in sorted(df_yr['villa No.'].unique()):
                    villa_key = villa_map_local.get(villa_num)
                    if not villa_key or villa_key not in SHAREHOLDERS:
                        continue
                    villa_df     = df_yr[df_yr['villa No.'] == villa_num]
                    shareholders = SHAREHOLDERS[villa_key]

                    monthly_totals = (
                        villa_df.groupby(['Month Num', 'Month Name'])['AMOUNT']
                        .sum().reset_index()
                    )
                    monthly_totals['Month Order'] = monthly_totals['Month Name'].apply(
                        lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99
                    )
                    monthly_totals = monthly_totals.sort_values('Month Order')
                    monthly_totals = monthly_totals[monthly_totals['Month Name'].isin(avail)]

                    months_cols  = monthly_totals['Month Name'].tolist()
                    months_nums  = monthly_totals['Month Num'].tolist()
                    months_label = [f"{m[:3]}-{str(year)[2:]}" for m in months_cols]

                    def get_net_xl(month_name, mt=monthly_totals):
                        row = mt[mt['Month Name'] == month_name]['AMOUNT'].values
                        return max(int(row[0]) - DEDUCTION, 0) if len(row) > 0 else 0

                    cc_row = {"Month": "Checks Collectives", "ShareHolders": "", "%": ""}
                    t, c, c1 = 0, 0, 0
                    for i, m in enumerate(months_cols):
                        net = get_net_xl(m)
                        cc_row[months_label[i]] = net
                        t += net
                        if months_nums[i] >= CURRENT_MONTH: c  += net
                        if months_nums[i] >  CURRENT_MONTH: c1 += net
                    cc_row["الإجمالي"] = t
                    cc_row["Current"]  = c
                    cc_row["Current+1"]= c1
                    all_rows.append(cc_row)

                    for sh_code, sh_pct in shareholders.items():
                        sh_row = {"Month": villa_key, "ShareHolders": sh_code, "%": f"{int(sh_pct*100)}%"}
                        t2, c2, c12 = 0, 0, 0
                        for i, m in enumerate(months_cols):
                            net = get_net_xl(m)
                            if sh_pct > 0:
                                val = round(net * sh_pct, 2)
                                sh_row[months_label[i]] = val
                                t2  += val
                                if months_nums[i] >= CURRENT_MONTH: c2  += val
                                if months_nums[i] >  CURRENT_MONTH: c12 += val
                                sh_monthly_xl[sh_code][months_label[i]] = \
                                    sh_monthly_xl[sh_code].get(months_label[i], 0) + val
                            else:
                                sh_row[months_label[i]] = "-"
                        sh_row["الإجمالي"]  = round(t2,  2) if sh_pct > 0 else "-"
                        sh_row["Current"]   = round(c2,  2) if sh_pct > 0 else "-"
                        sh_row["Current+1"] = round(c12, 2) if sh_pct > 0 else "-"
                        all_rows.append(sh_row)

                    all_rows.append({})

                # ترتيب شيت الفيلات
                final_df    = pd.DataFrame(all_rows)
                fixed_cols  = ["Month", "ShareHolders", "%"]
                ending_cols = ["الإجمالي", "Current", "Current+1"]
                month_cols_sorted = sort_month_cols(final_df.columns.tolist(), fixed_cols, ending_cols)
                ordered_cols = (
                    [c for c in fixed_cols  if c in final_df.columns] +
                    month_cols_sorted +
                    [c for c in ending_cols if c in final_df.columns]
                )
                final_df[ordered_cols].to_excel(writer, sheet_name=f"Collections {year}", index=False)

                # ====== شيت Monthly Collections الكلي ======
                all_lbl = sorted(
                    set(lbl for data in sh_monthly_xl.values() for lbl in data.keys()),
                    key=lambda x: MONTH_ORDER.index(
                        next((m for m in MONTH_ORDER if m[:3] == x.split('-')[0]), None) or 'ZZZ'
                    ) if '-' in x else 99
                )

                combined_xl = []
                gt_row = {"ShareHolders": "الإجمالي الكلي", "%": ""}
                gt_totals = {lbl: 0 for lbl in all_lbl}
                gt_sum = gt_c = gt_c1 = 0

                for sh_code in ALL_SH_CODES:
                    data = sh_monthly_xl[sh_code]
                    if not any(v > 0 for v in data.values()):
                        continue
                    row = {"ShareHolders": sh_code, "%": ""}
                    r_t = r_c = r_c1 = 0
                    for lbl in all_lbl:
                        val = round(data.get(lbl, 0), 2)
                        row[lbl] = val
                        r_t += val
                        m_num = label_to_month_num(lbl)
                        if m_num >= CURRENT_MONTH: r_c  += val
                        if m_num >  CURRENT_MONTH: r_c1 += val
                        gt_totals[lbl] += val
                    row["الإجمالي"]  = round(r_t,  2)
                    row["Current"]   = round(r_c,  2)
                    row["Current+1"] = round(r_c1, 2)
                    gt_sum += r_t; gt_c += r_c; gt_c1 += r_c1
                    combined_xl.append(row)

                for lbl in all_lbl:
                    gt_row[lbl] = round(gt_totals[lbl], 2)
                gt_row["الإجمالي"]  = round(gt_sum, 2)
                gt_row["Current"]   = round(gt_c,   2)
                gt_row["Current+1"] = round(gt_c1,  2)
                combined_xl.append(gt_row)

                comb_df = pd.DataFrame(combined_xl)
                fc  = ["ShareHolders", "%"]
                ec  = ["الإجمالي", "Current", "Current+1"]
                mcs = sort_month_cols(comb_df.columns.tolist(), fc, ec)
                comb_df = comb_df[[c for c in fc if c in comb_df.columns] + mcs +
                                   [c for c in ec if c in comb_df.columns]]
                comb_df.to_excel(writer, sheet_name="Monthly Collections", index=False)

            return output.getvalue()

        st.download_button(
            label="⬇️ تحميل Monthly Collections Excel",
            data=generate_collections_excel(df, selected_year_sh),
            file_name=f"monthly_collections_{selected_year_sh}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("👆 ارفع ملف Excel عشان تبدأ")