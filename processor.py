import pandas as pd

def load_and_filter_data():
    # 讀取學長的 25 年資料 
    df_old = pd.read_excel('中古車_dataset_2000~2020.xlsx')
    df_new = pd.read_excel('中古車_dataset_2021~2025.xlsx')
    full_df = pd.concat([df_old, df_new])
    
    # 篩選包含關鍵字的資料 (模擬過濾租賃爭議)
    keywords = ['租賃', '合約', '賠償', '違約', '爭議']
    # 假設學長資料中有個欄位叫 '內容' 或 '摘要'，這裡先以全欄位搜尋示範
    mask = full_df.apply(lambda row: row.astype(str).str.contains('|'.join(keywords)).any(), axis=1)
    return full_df[mask].reset_index(drop=True)
