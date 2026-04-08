import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from openai import OpenAI

class RAGEngine:
    def __init__(self, documents):
        # 使用支援多國語言的模型，適合處理台灣法院判決書
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.documents = documents
        self.index = self.build_index()

    def build_index(self):
        # 將資料轉換為向量
        embeddings = self.model.encode(self.documents)
        # 轉換為 float32 以符合 FAISS 要求
        embeddings = np.array(embeddings).astype('float32')
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index

    def search(self, query, k=3): # 將預設檢索數 k 改為 3，增加參考樣本
        query_vec = self.model.encode([query]).astype('float32')
        D, I = self.index.search(query_vec, k)
        
        # 將多份相關判決書合併成一段文字，並加上編號供 AI 區分
        combined_docs = ""
        for i in range(len(I[0])):
            idx = I[0][i]
            combined_docs += f"--- 參考判決案例 {i+1} ---\n{self.documents[idx]}\n\n"
        return combined_docs

# --- OpenAI 客戶端設定 ---
# 提醒：建議使用環境變數 os.getenv("OPENAI_API_KEY") 替換硬編碼金鑰
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_legal_summary(user_query, legal_documents):
    """把使用者的問題和找出來的多份判決書，一起丟給 GPT 做綜合風險評估"""
    
    # 優化後的指令：明確要求 AI 進行「判決傾向分析」而非單一故事總結
    prompt = f"""
你是一位專業的台灣二手車法律顧問，擅長分析民事租賃爭議。
請根據以下提供的『多份法院判決書內容』，綜合分析客戶面臨的法律風險。
回答時請嚴格依照以下【報告格式】回覆，不得自行增加其他開場白或結語。

### 報告格式
---
#### 1. 客戶問題核心
(簡述客戶擔心的爭議點)

#### 2. 歷年判決趨勢分析
(根據提供的判決書，說明法院通常如何判定此類案件，例如：是否計算折舊、營業損失認定等)

#### 3. 實務判賠參考
(列出判決書中常見的賠償金額範圍或計算公式)

#### 4. 專業防範建議
(告訴客戶在簽署合約或處理爭議時應注意的事項)

---
**🚩 風險等級：[高 / 中 / 低]**
根據實務判決對承租人的不利程度進行判定
### 判定標準：
- **風險等級：高** (若合約顯失公平，且實務判決通常支持對造求償)
- **風險等級：中** (雙方各有勝負空間，需視證據而定)
- **風險等級：低** (法律明確保障承租人，或實務判決多傾向支持承租人)
"""

    prompt = f"""
客戶問題：{user_query}

參考判決書資料：
{legal_documents}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "你是一位嚴謹的法律風險評估專家，只根據提供的判決書事實進行回覆。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0,      # 關鍵：保持輸出穩定
            seed=42             # 關鍵：增加可重現性
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"發生錯誤，請稍後再試：{str(e)}"