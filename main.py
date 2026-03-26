import os, base64, requests, json, time

API_KEY = os.getenv("AIzaSyAbNuTeuFMLfbc5MYfIL59BmcUrhsjwK8c")
IMAGE_FOLDER = "images"
DATA_JSON = "data.json"

def get_ai_tags(image_path):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")

    prompt = """你是一個極度嚴謹的時尚管理員。請精確辨識圖片，並嚴格依照以下字典回傳『14 段結構』。若無該屬性，一律填入『無』。
  
    【字典選項】
    [01]風格: 淑女氣質風, 知性通勤風, 休閒日常風, 運動機能風, 性感辣妹風, 街頭潮流風, 韓系簡約風, 日系可愛風, 歐美時尚風, 復古懷舊風, 甜辣混搭風, 御姊極簡風
    [02]上裝: 吊帶,背心,抹胸,馬甲,短版T,基本T,一字領,露肩,襯衫,特殊造型
    [03]褲裝: 熱褲,極短褲,真理褲,破褲,七分褲,直筒褲,寬褲,喇叭褲,瑜珈褲,緊身褲,多口袋工裝褲
    [04]褲材: 牛仔,雪紡,針織,皮革,西裝布,棉質,尼龍,燈芯絨
    [05]裙裝: 包臀裙,百褶裙,A字裙,魚尾裙,傘裙,開衩裙
    [06]裙長: 迷你,膝上,及膝,膝下,及踝,拖地
    [07]連身: 短版,中長版,長版,落地
    [08]外搭: 透膚防曬,針織外套,開衫,西裝外套,皮外套,軍裝工裝,帽T外套,牛仔外套,風衣
    [09]襪類: 隱形襪,短襪,中筒襪,膝下襪,過膝襪,大腿襪,褲襪
    [10]襪屬: 絲滑透膚,純色棉質,網眼,蕾絲,羅紋,厚絨
    [11]鞋履: 低跟鞋,高跟鞋,短靴,長靴,膝上長靴,馬丁靴,運動鞋,涼鞋,拖鞋,瑪莉珍鞋,帆布鞋
    [12]鞋色: 黑色,白色,大地色,銀色,金色,莫蘭迪色,亮色
    [13]材質: 雪紡,針織,皮革,蕾絲,絲絨,純棉,亞麻,亮面,霧面
    [14]細節: 刺繡,破洞,碎花,褶皺,抽繩,繫帶,鏤空,撞色,珍珠,金屬飾品

    【回傳規範】
    1. 格式：[01]_[02]-[03]-[04]-[05]-[06]-[07]-[08]-[09]-[10]-[11]-[12]-[13]-[14]
    2. 僅回傳字串，必須精確包含 1 個底線與 12 個連字號。
    """

    payload = {
        "contents": [{ "parts": [{ "text": prompt }, { "inline_data": { "mime_type": "image/jpeg", "data": img_data } }] }]
    }

    try:
        res = requests.post(url, json=payload, timeout=30).json()
        tag = res['candidates'][0]['content']['parts'][0]['text'].strip()
        return tag.replace('\n', '').replace(' ', '').replace('"', '').replace("'", "")
    except Exception as e:
        print(f"❌ API 異常: {e}")
        return "錯誤"

def run():
    if not API_KEY:
        print("❌ 致命錯誤：找不到 GEMINI_API_KEY。請檢查 GitHub Secrets。")
        return

    if not os.path.exists(IMAGE_FOLDER): 
        os.makedirs(IMAGE_FOLDER)

    files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    for f in files:
        # 如果已經是 14 段格式，則跳過不消耗 API
        if f.count('-') == 12 and '_' in f: 
            continue
        
        print(f"🔍 正在辨識: {f}")
        tag = get_ai_tags(os.path.join(IMAGE_FOLDER, f))
        
        if tag != "錯誤" and "_" in tag and tag.count('-') == 12:
            ext = os.path.splitext(f)[1]
            new_name = f"{tag}_{int(time.time())}{ext}"
            os.rename(os.path.join(IMAGE_FOLDER, f), os.path.join(IMAGE_FOLDER, new_name))
            print(f"✅ 命名成功: {new_name}")
        time.sleep(2) # 避免觸發 API 頻率限制

    # 絕對生成 data.json：重新掃描資料夾內所有已命名的圖片
    all_valid_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f.count('-') == 12]
    new_data = [{"url": f"images/{img}", "tags": img.split('_')[0], "filename": img} for img in all_valid_files]
    
    with open(DATA_JSON, "w", encoding="utf-8") as j:
        json.dump(new_data, j, indent=4, ensure_ascii=False)
    print(f"🚀 data.json 已同步，共記錄 {len(all_valid_files)} 筆資產。")

if __name__ == "__main__":
    run()
