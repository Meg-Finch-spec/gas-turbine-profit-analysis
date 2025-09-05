import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# 设置页面配置
st.set_page_config(
    page_title="燃气轮机投资经济技术分析计算软件",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 页面标题
st.title("燃气轮机投资经济技术分析计算软件")

# 金额单位转换字典
unit_conversion = {
    "人民币元": 1,
    "万元": 10000,
    "百万元": 1000000,
    "美元": 1,
    "万美元": 10000,
    "百万美元": 1000000
}

# 热耗率单位转换字典
heat_rate_conversion = {
    "btu/kwh": 1.05506,  # 1 btu = 1.05506 kj
    "kcal/kwh": 4.1868,  # 1 kcal = 4.1868 kj
    "kj/kwh": 1
}

# 功率单位转换字典
power_conversion = {
    "kW": 1,
    "MW": 1000
}

# 货币类型
currency_types = ["人民币", "美元"]

# 初始化会话状态
if "maintenance_items" not in st.session_state:
    st.session_state.maintenance_items = ["常规保养", "零部件更换"]
    st.session_state.maintenance_costs = [1000.0, 2000.0]
    st.session_state.maintenance_currency_units = ["人民币元"] * 2
if "delete_flags" not in st.session_state:
    st.session_state.delete_flags = [False] * len(st.session_state.maintenance_items)
if "add_new_item_flag" not in st.session_state:
    st.session_state.add_new_item_flag = False

# 定义回调函数 - 添加新项目
def add_new_maintenance_item():
    if st.session_state.add_new_item_flag:
        st.session_state.maintenance_items.append("新项目")
        st.session_state.maintenance_costs.append(0.0)
        st.session_state.maintenance_currency_units.append("人民币元")
        st.session_state.delete_flags.append(False)
        # 重置添加标志以避免重复添加
        st.session_state.add_new_item_flag = False

# 定义回调函数 - 删除项目
def delete_maintenance_item(index):
    if st.session_state[f"delete_flag_{index}"]:
        # 延迟删除以避免界面更新问题
        st.session_state[f"delete_queued_{index}"] = True
        # 触发界面更新
        st.session_state["ui_update_trigger"] = not st.session_state.get("ui_update_trigger", False)

# 确保有ui_update_trigger状态
if "ui_update_trigger" not in st.session_state:
    st.session_state["ui_update_trigger"] = False

# 处理删除队列中的项目
for i in range(len(st.session_state.maintenance_items) + 1):  # +1是为了处理可能的新增项目
    if f"delete_queued_{i}" in st.session_state and st.session_state[f"delete_queued_{i}"]:
        if i < len(st.session_state.maintenance_items):
            st.session_state.maintenance_items.pop(i)
            st.session_state.maintenance_costs.pop(i)
            st.session_state.maintenance_currency_units.pop(i)
            # 调整剩余的删除队列标志
            for j in range(i, len(st.session_state.maintenance_items) + 1):
                if f"delete_queued_{j+1}" in st.session_state:
                    st.session_state[f"delete_queued_{j}"] = st.session_state[f"delete_queued_{j+1}"]
                    del st.session_state[f"delete_queued_{j+1}"]
        # 重置当前删除标志
        del st.session_state[f"delete_queued_{i}"]
        # 调整delete_flags列表长度
        st.session_state.delete_flags = [False] * len(st.session_state.maintenance_items)
        # 跳出循环以避免索引问题
        break

# 在侧边栏创建输入表单
with st.sidebar.form("input_form"):
    st.header("输入参数")
    
    # 1. 金额单位统一选项（用于最终结果显示）
    result_display_unit = st.selectbox(
        "结果显示单位",
        list(unit_conversion.keys())
    )
    
    # 解析结果显示单位中的货币类型
    result_currency = "人民币" if "人民币" in result_display_unit else "美元"
    
    # 2. 燃机发电形式
    power_type = st.selectbox(
        "燃机发电形式",
        ["发电厂", "电源车", "压缩机", "其他"]
    )
    
    # 3. 单台机组核心机价格
    with st.expander("单台机组核心机价格"):
        unit_price_currency_unit = st.selectbox(
            "货币单位",
            list(unit_conversion.keys())
        )
        single_unit_price = st.number_input(
            f"单台机组核心机价格 ({unit_price_currency_unit})",
            min_value=0.0,
            format="%.2f"
        )
    
    # 4. 需要的机组数量
    unit_count = st.number_input(
        "需要的机组数量（台）",
        min_value=1,
        step=1,
        value=1
    )
    
    # 5. 单台机组工况功率
    with st.expander("单台机组工况功率"):
        工况 = st.text_input("工况描述", "基本负荷")
        power_value = st.number_input(
            "功率值",
            min_value=0.0,
            format="%.2f"
        )
        power_unit = st.selectbox(
            "功率单位",
            list(power_conversion.keys())
        )
    
    # 6. 燃气轮机热耗率
    with st.expander("燃气轮机热耗率"):
        heat_rate_value = st.number_input(
            "热耗率值",
            min_value=0.0,
            format="%.2f"
        )
        heat_rate_unit = st.selectbox(
            "热耗率单位",
            list(heat_rate_conversion.keys())
        )
    
    # 7. 燃料体积低位热值
    fuel_lower_heating_value = st.number_input(
        "燃料体积低位热值 (KJ/Nm³)",
        min_value=0.0,
        format="%.2f"
    )
    
    # 8. 天然气价格
    with st.expander("天然气价格"):
        gas_price_currency_unit = st.selectbox(
            "货币单位",
            list(unit_conversion.keys())
        )
        natural_gas_price = st.number_input(
            f"天然气价格 ({gas_price_currency_unit}/Nm³)",
            min_value=0.0,
            format="%.6f"
        )
    
    # 9. 电价
    with st.expander("电价"):
        elec_price_currency_unit = st.selectbox(
            "货币单位",
            list(unit_conversion.keys())
        )
        electricity_price = st.number_input(
            f"电价 ({elec_price_currency_unit}/kwh)",
            min_value=0.0,
            format="%.6f"
        )
    
    # 10. 是否联合循环或其他
    is_combined_cycle = st.checkbox("是否联合循环")
    
    if is_combined_cycle:
        st.warning("联合循环功能将在后续总投资和运维成本，盈利中加入相应项目")
        
    # 11. 工人费用
    with st.expander("工人费用"):
        st.subheader("请输入各工种的年薪和人数")
        
        # 工人费用货币选择
        worker_currency_unit = st.selectbox(
            "工人费用货币单位",
            list(unit_conversion.keys()),
            index=0 if "人民币" in result_display_unit else 3
        )
        
        # 创建工人费用数据结构
        worker_types = [
            "仪器仪表工程师", "电气工程师", "燃气轮机操作员",
            "机械工程师", "电厂运营助理", "安全工程师"
        ]
        
        worker_data = {}
        for worker in worker_types:
            col1, col2 = st.columns(2)
            with col1:
                annual_salary = st.number_input(
                    f"{worker}年薪 ({worker_currency_unit})",
                    min_value=0.0,
                    format="%.2f",
                    key=f"{worker}_salary"
                )
            with col2:
                count = st.number_input(
                    f"{worker}人数",
                    min_value=0,
                    step=1,
                    key=f"{worker}_count"
                )
            worker_data[worker] = {"年薪": annual_salary, "人数": count, 
                                 "货币单位": worker_currency_unit}
    
    # 12. 设备维护费用
    with st.expander("设备维护费用"):
        st.subheader("设备维护费用项目")
        
        # 确保delete_flags长度与项目数量一致
        if len(st.session_state.delete_flags) != len(st.session_state.maintenance_items):
            st.session_state.delete_flags = [False] * len(st.session_state.maintenance_items)
        
        # 显示现有维护项目
        for i in range(len(st.session_state.maintenance_items)):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.session_state.maintenance_items[i] = st.text_input(
                    "项目名称",
                    st.session_state.maintenance_items[i],
                    key=f"maintenance_name_{i}"
                )
            with col2:
                st.session_state.maintenance_costs[i] = st.number_input(
                    "费用",
                    min_value=0.0,
                    format="%.2f",
                    value=st.session_state.maintenance_costs[i],
                    key=f"maintenance_cost_{i}"
                )
            with col3:
                if i >= len(st.session_state.maintenance_currency_units):
                    st.session_state.maintenance_currency_units.append("人民币元")
                st.session_state.maintenance_currency_units[i] = st.selectbox(
                    "货币单位",
                    list(unit_conversion.keys()),
                    index=list(unit_conversion.keys()).index(st.session_state.maintenance_currency_units[i])
                    if i < len(st.session_state.maintenance_currency_units) else 0,
                    key=f"maintenance_unit_{i}"
                )
            with col4:
                if len(st.session_state.maintenance_items) > 1:
                    # 使用回调函数实现实时删除
                    if st.checkbox(
                        "删除", 
                        key=f"delete_flag_{i}",
                        on_change=delete_maintenance_item, 
                        args=(i,)
                    ):
                        pass
        
        # 添加新项目（使用回调函数实现实时添加）
        st.checkbox(
            "添加新维护项目", 
            key="add_new_item_flag",
            on_change=add_new_maintenance_item
        )
    
    # 13. 单次大修费用
    with st.expander("单次大修费用"):
        overhaul_currency_unit = st.selectbox(
            "货币单位",
            list(unit_conversion.keys())
        )
        overhaul_cost = st.number_input(
            f"单次大修费用 ({overhaul_currency_unit})",
            min_value=0.0,
            format="%.2f"
        )
    
    # 14. 大修周期
    overhaul_period = st.number_input(
        "大修周期 (h)",
        min_value=1.0,
        format="%.2f"
    )
    
    # 15. A/B检修，每年金额
    with st.expander("A/B检修每年金额"):
        ab_currency_unit = st.selectbox(
            "货币单位",
            list(unit_conversion.keys())
        )
        ab_inspection_cost = st.number_input(
            f"A/B检修每年金额 ({ab_currency_unit})",
            min_value=0.0,
            format="%.2f"
        )
    
    # 汇率设置
    with st.expander("汇率设置"):
        st.subheader("用于货币转换的汇率")
        usd_to_cny = st.number_input(
            "美元兑人民币汇率",
            min_value=0.0,
            value=7.0,
            format="%.2f"
        )
    
    # 提交按钮
    submit_button = st.form_submit_button("开始计算")

# 主页面内容
if submit_button:
    # 定义货币和单位转换函数
    def get_currency_from_unit(unit):
        return "人民币" if "人民币" in unit else "美元"
    
    def convert_to_base_unit(amount, unit):
        """将金额转换为基础单位（人民币元或美元）"""
        return amount * unit_conversion[unit]
    
    def convert_from_base_unit(amount, from_currency, to_unit):
        """从基础单位转换到目标单位"""
        # 先进行货币转换
        to_currency = get_currency_from_unit(to_unit)
        if from_currency != to_currency:
            if from_currency == "美元" and to_currency == "人民币":
                amount = amount * usd_to_cny
            elif from_currency == "人民币" and to_currency == "美元":
                amount = amount / usd_to_cny
        # 再进行数量级转换
        return amount / unit_conversion[to_unit]
    
    # 计算逻辑
    
    # 转换功率为kW
    power_in_kw = power_value * power_conversion[power_unit]
    
    # 转换热耗率为kj/kwh
    heat_rate_in_kj = heat_rate_value * heat_rate_conversion[heat_rate_unit]
    
    # 计算燃机总发电量（GWH）
    total_electricity_gwh = unit_count * power_in_kw * 8000 / 1000000
    
    # 计算天然气消耗率（Nm³/h）
    natural_gas_consumption = heat_rate_in_kj * power_in_kw * unit_count / fuel_lower_heating_value
    
    # 计算总的机组价格（转换为基础单位）
    total_unit_price_base = convert_to_base_unit(single_unit_price, unit_price_currency_unit) * unit_count
    total_unit_price_display = convert_from_base_unit(total_unit_price_base, get_currency_from_unit(unit_price_currency_unit), result_display_unit)
    
    # 计算每隔几年需要大修
    years_between_overhauls = int(overhaul_period / 8000)
    if years_between_overhauls < 1:
        years_between_overhauls = 1
    
    # 计算工人费用总计（转换为基础单位）
    total_worker_cost_base = 0
    worker_summary = []
    for worker, data in worker_data.items():
        worker_total_base = convert_to_base_unit(data["年薪"], data["货币单位"]) * data["人数"]
        total_worker_cost_base += worker_total_base
        worker_summary.append([worker, data["年薪"], data["人数"], 
                             convert_from_base_unit(worker_total_base, 
                                                  get_currency_from_unit(data["货币单位"]), 
                                                  result_display_unit), 
                             result_display_unit])
    
    # 计算维护费用总计（转换为基础单位）
    total_maintenance_cost_base = 0
    maintenance_summary = []
    for i in range(len(st.session_state.maintenance_items)):
        item = st.session_state.maintenance_items[i]
        cost = st.session_state.maintenance_costs[i]
        currency_unit = st.session_state.maintenance_currency_units[i]
        cost_base = convert_to_base_unit(cost, currency_unit)
        total_maintenance_cost_base += cost_base
        maintenance_summary.append([item, cost, currency_unit, 
                                  convert_from_base_unit(cost_base, 
                                                       get_currency_from_unit(currency_unit), 
                                                       result_display_unit), 
                                  result_display_unit])
    
    # 转换大修费用和A/B检修费用到基础单位
    overhaul_cost_base = convert_to_base_unit(overhaul_cost, overhaul_currency_unit)
    ab_inspection_cost_base = convert_to_base_unit(ab_inspection_cost, ab_currency_unit)
    
    # 转换天然气价格和电价到基础单位
    natural_gas_price_base = convert_to_base_unit(natural_gas_price, gas_price_currency_unit)
    electricity_price_base = convert_to_base_unit(electricity_price, elec_price_currency_unit)
    
    # 准备年度数据计算
    years = 12
    results = {
        "年份": list(range(1, years + 1)),
        "总投资": [0] * years,
        "运维费用": [0] * years,
        "燃料费用": [0] * years,
        "发电量Gwh": [0] * years,
        "年经营成本": [0] * years,
        "年收入": [0] * years,
        "年流水": [0] * years,
        "累计收益": [0] * years
    }
    
    # 第1年的总投资（转换为显示单位）
    results["总投资"][0] = total_unit_price_display
    
    # 计算每年的数据
    cumulative_profit_base = 0
    for i in range(years):
        year = i + 1
        
        # 计算运维费用（转换为显示单位）
        opex_base = total_worker_cost_base + total_maintenance_cost_base + ab_inspection_cost_base
        # 每隔n年增加大修费用
        if year % years_between_overhauls == 0:
            opex_base += overhaul_cost_base
        
        # 计算燃料费用（转换为显示单位）
        fuel_cost_base = natural_gas_consumption * natural_gas_price_base * 8000
        
        # 发电量
        results["发电量Gwh"][i] = total_electricity_gwh
        
        # 年收入（转换为显示单位）
        annual_revenue_base = total_electricity_gwh * electricity_price_base * 1000000  # GWh转换为kWh
        # 联合循环额外收入（暂不实现具体计算）
        if is_combined_cycle:
            st.warning("联合循环额外收入暂按基础收入的10%估算")
            annual_revenue_base *= 1.1
        
        # 年流水和累计收益（基础单位）
        annual_cash_flow_base = annual_revenue_base - (opex_base + fuel_cost_base)
        cumulative_profit_base += annual_cash_flow_base
        
        # 转换为显示单位
        opex_display = convert_from_base_unit(opex_base, get_currency_from_unit(worker_currency_unit), result_display_unit)
        fuel_cost_display = convert_from_base_unit(fuel_cost_base, get_currency_from_unit(gas_price_currency_unit), result_display_unit)
        annual_revenue_display = convert_from_base_unit(annual_revenue_base, get_currency_from_unit(elec_price_currency_unit), result_display_unit)
        annual_cash_flow_display = convert_from_base_unit(annual_cash_flow_base, "人民币", result_display_unit)  # 假设基础货币为人民币
        cumulative_profit_display = convert_from_base_unit(cumulative_profit_base, "人民币", result_display_unit)  # 假设基础货币为人民币
        
        results["运维费用"][i] = opex_display
        results["燃料费用"][i] = fuel_cost_display
        results["年经营成本"][i] = opex_display + fuel_cost_display
        results["年收入"][i] = annual_revenue_display
        results["年流水"][i] = annual_cash_flow_display
        results["累计收益"][i] = cumulative_profit_display
    
    # 计算平均年收益（转换为显示单位）
    avg_annual_profit_base = cumulative_profit_base / years
    avg_annual_profit_display = convert_from_base_unit(avg_annual_profit_base, "人民币", result_display_unit)
    
    # 创建结果表格
    result_df = pd.DataFrame(results)
    
    # 显示计算结果
    st.header("计算结果")
    
    # 显示关键指标
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("燃机总发电量", f"{total_electricity_gwh:.2f} GWH")
    with col2:
        st.metric("天然气消耗率", f"{natural_gas_consumption:.2f} Nm³/h")
    with col3:
        st.metric("总的机组价格", f"{total_unit_price_display:.2f} {result_display_unit}")
    with col4:
        st.metric("大修间隔", f"{years_between_overhauls} 年")
    
    # 显示工人费用表格
    st.subheader("工人费用明细")
    worker_df = pd.DataFrame(worker_summary, columns=["工种", "年薪", "人数", f"总计 ({result_display_unit})", "货币单位"])
    total_worker_display = convert_from_base_unit(total_worker_cost_base, get_currency_from_unit(worker_currency_unit), result_display_unit)
    worker_df.loc[len(worker_df)] = ["总计", "-", "-", total_worker_display, result_display_unit]
    st.dataframe(worker_df)
    
    # 显示维护费用表格
    st.subheader("设备维护费用明细")
    maintenance_df = pd.DataFrame(maintenance_summary, columns=["维护项目", "费用原值", "原值单位", f"费用 ({result_display_unit})", "转换后单位"])
    total_maintenance_display = convert_from_base_unit(total_maintenance_cost_base, "人民币", result_display_unit)  # 假设基础货币为人民币
    maintenance_df.loc[len(maintenance_df)] = ["总计", "-", "-", total_maintenance_display, result_display_unit]
    st.dataframe(maintenance_df)
    
    # 显示年度经济分析表格
    st.subheader("年度经济分析")
    st.dataframe(result_df.style.format(precision=2))
    
    # 显示平均年收益
    st.subheader(f"平均年收益: {avg_annual_profit_display:.2f} {result_display_unit}")
    
    # 添加图表可视化
    st.subheader("经济指标趋势图")
    chart_data = result_df[["年份", "年收入", "年经营成本", "年流水", "累计收益"]]
    st.line_chart(chart_data.set_index("年份"))
    
    # 添加导出功能
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='年度经济分析')
            worker_df.to_excel(writer, index=False, sheet_name='工人费用')
            maintenance_df.to_excel(writer, index=False, sheet_name='维护费用')
        processed_data = output.getvalue()
        return processed_data
    
    excel_data = to_excel(result_df)
    st.download_button(
        label="导出Excel报告",
        data=excel_data,
        file_name="燃气轮机投资分析报告.xlsx",
        mime="application/vnd.ms-excel"
    )

# 添加项目说明
with st.expander("项目说明"):
    st.markdown("""
    ### 燃气轮机投资经济技术分析计算软件
    本软件用于对燃气轮机相关项目投资进行经济技术分析，计算项目的投资回报情况。
    
    ### 计算说明
    1. **燃机总发电量**: 机组数量 * 单台机组功率 * 8000 / 1000
    2. **天然气消耗率**: 热耗率 * 单台机组效率 * 机组数量 / 燃料体积低位热值
    3. **总的机组价格**: 单台机组价格 * 机组数量
    4. **大修间隔**: 取小于（大修周期/8000h）的整数值
    5. **年度经济分析**: 包含总投资、运维费用、燃料费用、发电量、年经营成本、年收入、年流水和累计收益等指标
    
    ### 货币转换说明
    系统支持所有费用项目使用不同的货币类型和数量级（人民币元、万元、百万元、美元、万美元、百万美元），并会自动转换为统一的显示单位进行计算和展示。
    所有计算均在基础单位（人民币元或美元）下进行，确保计算精度。
    
    ### 维护项目管理
    维护项目支持实时添加和删除功能，勾选"删除"或"添加新维护项目"后，项目列表会立即更新，无需等待点击"开始计算"按钮。
    """)