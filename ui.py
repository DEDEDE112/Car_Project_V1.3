import streamlit as st
from engine import get_legal_summary

def run_ui(search_callback):
    st.set_page_config(page_title="二手車租約風險評估", page_icon="🛡️")
    
    # 標題與簡介
    st.title("🛡️ 二手車租約風險評估系統")
    st.caption("利用向量搜尋技術，比對歷年法院判決大數據，預析您的合約法律風險。")
    st.markdown("---")

    # --- 💡 新增：使用說明與範例欄 ---
    with st.expander("📖 系統使用說明與提問範例 (點擊展開)", expanded=True):
        st.markdown("""
        ### 🛠️ 如何使用本系統？
        1. **輸入條款**：將您擔心的二手車租賃合約條文，或具體發生的爭議情境填入下方輸入框。
        2. **語義比對**：系統會透過 **RAG 架構**，從資料庫中找出最相關的判決書作為參考。
        3. **查看報告**：AI 會根據判決趨勢給出白話建議與風險等級。

        ### 📝 提問範例（複製下方文字試試看）：
        * **情境 A (車損折舊)**：`合約規定車損賠償原廠全新品，法院通常會支持計算『零件折舊』嗎？`
        * **情境 B (營業損失)**：`維修期間合約要求賠償全額營業損失，法律實務上通常如何判定合理天數？`
        * **情境 C (自然損壞)**：`租車期間引擎因過熱損壞，合約說只要壞掉都算我的，這在法律上合理嗎？`
        """)

    # --- 輸入區 ---
    user_input = st.text_area(
        "請輸入合約條款內容或爭議問題：", 
        placeholder="請描述具體情境，例如：倒車撞到牆壁，合約要求賠償全額維修費...",
        height=180
    )
    
    st.info("💡 **小撇步**：描述越具體（包含：折舊、天數、金額），搜尋結果會越精準！")

    # --- 執行分析 ---
    if st.button("🚀 開始法律風險深度分析", use_container_width=True):
        if user_input:
            with st.spinner("⚖️ AI 律師正在檢索大數據並進行語義比對..."):
                try:
                    # 1. 執行檢索 (search_callback)
                    raw_documents = search_callback(user_input)
                    
                    # 2. 執行 AI 總結
                    ai_report = get_legal_summary(user_input, raw_documents)
                    
                    st.success("✅ 分析完成！")
                    st.markdown("---")
                    
                    # 3. 顯示結果
                    st.subheader("🤖 AI 風險評估報告")
                    with st.container(border=True):
                        st.markdown(ai_report)
                    
                    # 4. 原始資料折疊區
                    with st.expander("📄 查看 AI 參考的原始法院判決書"):
                        st.write(raw_documents)
                        
                except Exception as e:
                    st.error(f"分析過程中發生錯誤：{e}")
        else:
            st.warning("⚠️ 請先輸入內容再進行分析喔！")

    # 頁尾免責聲明
    st.markdown("---")
    st.caption("⚠️ 免責聲明：本系統報告僅供學術與初步參考，不代表正式法律建議。")
