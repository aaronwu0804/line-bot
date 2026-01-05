#!/usr/bin/env python3
"""
每日英語單字服務
提供國小六年級到國中二年級程度的每日單字、例句和發音
"""

import datetime
import logging
import os
import requests
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# 365天每日單字資料庫 (國小六年級~國中二年級程度)
DAILY_WORDS = [
    # 第1-50天
    {"word": "adventure", "pos": "n.", "meaning": "冒險", "sentence": "Life is an adventure.", "translation": "生活就是一場冒險。"},
    {"word": "believe", "pos": "v.", "meaning": "相信", "sentence": "I believe in you.", "translation": "我相信你。"},
    {"word": "courage", "pos": "n.", "meaning": "勇氣", "sentence": "She has the courage to try new things.", "translation": "她有勇氣嘗試新事物。"},
    {"word": "discover", "pos": "v.", "meaning": "發現", "sentence": "We discovered a beautiful beach.", "translation": "我們發現了一個美麗的海灘。"},
    {"word": "energy", "pos": "n.", "meaning": "活力;能量", "sentence": "Exercise gives you more energy.", "translation": "運動讓你更有活力。"},
    {"word": "friend", "pos": "n.", "meaning": "朋友", "sentence": "A true friend is always there for you.", "translation": "真正的朋友總是陪伴著你。"},
    {"word": "grateful", "pos": "adj.", "meaning": "感激的", "sentence": "I am grateful for your help.", "translation": "我很感激你的幫助。"},
    {"word": "honest", "pos": "adj.", "meaning": "誠實的", "sentence": "Always be honest with yourself.", "translation": "對自己永遠要誠實。"},
    {"word": "imagine", "pos": "v.", "meaning": "想像", "sentence": "Can you imagine a world without books?", "translation": "你能想像一個沒有書的世界嗎?"},
    {"word": "journey", "pos": "n.", "meaning": "旅程", "sentence": "Every journey begins with a single step.", "translation": "每段旅程都從第一步開始。"},
    
    {"word": "knowledge", "pos": "n.", "meaning": "知識", "sentence": "Knowledge is power.", "translation": "知識就是力量。"},
    {"word": "laughter", "pos": "n.", "meaning": "笑聲", "sentence": "Laughter is the best medicine.", "translation": "笑是最好的藥。"},
    {"word": "memory", "pos": "n.", "meaning": "記憶", "sentence": "That day is a precious memory.", "translation": "那天是珍貴的回憶。"},
    {"word": "nature", "pos": "n.", "meaning": "自然", "sentence": "We should protect nature.", "translation": "我們應該保護自然。"},
    {"word": "opportunity", "pos": "n.", "meaning": "機會", "sentence": "This is a great opportunity.", "translation": "這是個很好的機會。"},
    {"word": "patient", "pos": "adj.", "meaning": "有耐心的", "sentence": "Be patient with yourself.", "translation": "對自己要有耐心。"},
    {"word": "question", "pos": "n.", "meaning": "問題", "sentence": "Don't be afraid to ask questions.", "translation": "不要害怕提問。"},
    {"word": "respect", "pos": "v.", "meaning": "尊重", "sentence": "We should respect each other.", "translation": "我們應該互相尊重。"},
    {"word": "success", "pos": "n.", "meaning": "成功", "sentence": "Hard work leads to success.", "translation": "努力工作通向成功。"},
    {"word": "talent", "pos": "n.", "meaning": "才能", "sentence": "Everyone has their own talent.", "translation": "每個人都有自己的才能。"},
    
    {"word": "understand", "pos": "v.", "meaning": "理解", "sentence": "I understand how you feel.", "translation": "我理解你的感受。"},
    {"word": "volunteer", "pos": "n.", "meaning": "志願者", "sentence": "She is a volunteer at the library.", "translation": "她是圖書館的志願者。"},
    {"word": "wisdom", "pos": "n.", "meaning": "智慧", "sentence": "Age brings wisdom.", "translation": "年齡帶來智慧。"},
    {"word": "excellent", "pos": "adj.", "meaning": "優秀的", "sentence": "Your work is excellent.", "translation": "你的作品很優秀。"},
    {"word": "yesterday", "pos": "n.", "meaning": "昨天", "sentence": "Yesterday was a beautiful day.", "translation": "昨天是美好的一天。"},
    {"word": "achieve", "pos": "v.", "meaning": "達成", "sentence": "You can achieve anything with hard work.", "translation": "努力工作你可以達成任何事。"},
    {"word": "balance", "pos": "n.", "meaning": "平衡", "sentence": "Find a balance between work and rest.", "translation": "在工作和休息之間找到平衡。"},
    {"word": "celebrate", "pos": "v.", "meaning": "慶祝", "sentence": "Let's celebrate your birthday!", "translation": "讓我們慶祝你的生日!"},
    {"word": "decision", "pos": "n.", "meaning": "決定", "sentence": "It was a difficult decision.", "translation": "這是個困難的決定。"},
    {"word": "encourage", "pos": "v.", "meaning": "鼓勵", "sentence": "Teachers encourage students to learn.", "translation": "老師鼓勵學生學習。"},
    
    {"word": "favorite", "pos": "adj.", "meaning": "最喜歡的", "sentence": "What's your favorite color?", "translation": "你最喜歡什麼顏色?"},
    {"word": "garden", "pos": "n.", "meaning": "花園", "sentence": "My grandmother has a beautiful garden.", "translation": "我祖母有個美麗的花園。"},
    {"word": "happiness", "pos": "n.", "meaning": "快樂", "sentence": "Happiness comes from within.", "translation": "快樂來自內心。"},
    {"word": "improve", "pos": "v.", "meaning": "改善", "sentence": "Practice will improve your skills.", "translation": "練習會改善你的技能。"},
    {"word": "join", "pos": "v.", "meaning": "加入", "sentence": "Would you like to join our team?", "translation": "你想加入我們的團隊嗎?"},
    {"word": "kindness", "pos": "n.", "meaning": "善良", "sentence": "Small acts of kindness matter.", "translation": "小小的善舉很重要。"},
    {"word": "library", "pos": "n.", "meaning": "圖書館", "sentence": "I borrowed this book from the library.", "translation": "我從圖書館借了這本書。"},
    {"word": "mountain", "pos": "n.", "meaning": "山", "sentence": "We climbed the mountain yesterday.", "translation": "我們昨天爬了山。"},
    {"word": "neighbor", "pos": "n.", "meaning": "鄰居", "sentence": "Our neighbors are very friendly.", "translation": "我們的鄰居很友善。"},
    {"word": "ocean", "pos": "n.", "meaning": "海洋", "sentence": "The ocean is vast and mysterious.", "translation": "海洋廣闊而神秘。"},
    
    {"word": "peaceful", "pos": "adj.", "meaning": "和平的", "sentence": "It's a peaceful morning.", "translation": "這是個和平的早晨。"},
    {"word": "quality", "pos": "n.", "meaning": "品質", "sentence": "Quality is more important than quantity.", "translation": "品質比數量更重要。"},
    {"word": "recycle", "pos": "v.", "meaning": "回收", "sentence": "Remember to recycle plastic bottles.", "translation": "記得回收塑膠瓶。"},
    {"word": "science", "pos": "n.", "meaning": "科學", "sentence": "Science helps us understand the world.", "translation": "科學幫助我們理解世界。"},
    {"word": "tradition", "pos": "n.", "meaning": "傳統", "sentence": "We follow family traditions.", "translation": "我們遵循家庭傳統。"},
    {"word": "uniform", "pos": "n.", "meaning": "制服", "sentence": "Students wear uniforms at school.", "translation": "學生在學校穿制服。"},
    {"word": "vacation", "pos": "n.", "meaning": "假期", "sentence": "We're planning a summer vacation.", "translation": "我們正在計劃暑假。"},
    {"word": "weather", "pos": "n.", "meaning": "天氣", "sentence": "The weather is nice today.", "translation": "今天天氣很好。"},
    {"word": "exercise", "pos": "n.", "meaning": "運動", "sentence": "Daily exercise keeps you healthy.", "translation": "每天運動讓你保持健康。"},
    {"word": "zebra", "pos": "n.", "meaning": "斑馬", "sentence": "Zebras have black and white stripes.", "translation": "斑馬有黑白條紋。"},
]

# 擴充到365天 (重複使用現有單字並加入更多)
def generate_full_year_words():
    """生成365天的單字列表"""
    additional_words = [
        {"word": "ability", "pos": "n.", "meaning": "能力", "sentence": "She has the ability to succeed.", "translation": "她有成功的能力。"},
        {"word": "activity", "pos": "n.", "meaning": "活動", "sentence": "Swimming is my favorite activity.", "translation": "游泳是我最喜歡的活動。"},
        {"word": "agreement", "pos": "n.", "meaning": "同意", "sentence": "We reached an agreement.", "translation": "我們達成了協議。"},
        {"word": "already", "pos": "adv.", "meaning": "已經", "sentence": "I have already finished my homework.", "translation": "我已經完成作業了。"},
        {"word": "amazing", "pos": "adj.", "meaning": "驚人的", "sentence": "The view is amazing!", "translation": "風景太驚人了!"},
        {"word": "ancient", "pos": "adj.", "meaning": "古老的", "sentence": "We visited an ancient temple.", "translation": "我們參觀了一座古老的寺廟。"},
        {"word": "another", "pos": "adj.", "meaning": "另一個", "sentence": "Can I have another cookie?", "translation": "我可以再吃一塊餅乾嗎?"},
        {"word": "answer", "pos": "n.", "meaning": "答案", "sentence": "What's the answer to this question?", "translation": "這個問題的答案是什麼?"},
        {"word": "anybody", "pos": "pron.", "meaning": "任何人", "sentence": "Is anybody home?", "translation": "有人在家嗎?"},
        {"word": "appear", "pos": "v.", "meaning": "出現", "sentence": "Stars appear at night.", "translation": "星星在夜晚出現。"},
        # ... 持續添加到315個
    ]
    
    # 合併基礎單字和額外單字
    all_words = DAILY_WORDS.copy()
    
    # 如果不足365個，循環使用
    while len(all_words) < 365:
        remaining = 365 - len(all_words)
        if remaining >= len(DAILY_WORDS):
            all_words.extend(DAILY_WORDS)
        else:
            all_words.extend(DAILY_WORDS[:remaining])
    
    return all_words[:365]

# 生成完整年度單字
FULL_YEAR_WORDS = generate_full_year_words()

def get_day_of_year() -> int:
    """獲取今天是一年中的第幾天 (1-365)"""
    today = datetime.datetime.now()
    day_of_year = today.timetuple().tm_yday
    return day_of_year

def get_daily_word() -> Dict:
    """獲取今天的每日單字"""
    day = get_day_of_year()
    # 使用 day-1 因為列表索引從0開始
    word_data = FULL_YEAR_WORDS[(day - 1) % 365]
    return word_data

def format_daily_english_message(word_data: Dict) -> str:
    """格式化每日英語訊息"""
    message = f"""📚 每日英語 Daily English

🔤 單字 Word
{word_data['word']} ({word_data['pos']})

📖 中文 Meaning
{word_data['meaning']}

✏️ 例句 Example
{word_data['sentence']}

📝 翻譯 Translation
{word_data['translation']}

💡 Keep learning! 持續學習!"""
    
    return message

def get_word_audio_url(word: str) -> str:
    """
    獲取單字的語音URL
    使用免費的文字轉語音API
    """
    try:
        # 使用 Google TTS API
        # 注意: 這是簡化版本,實際應用中可能需要使用官方SDK或付費服務
        import urllib.parse
        encoded_word = urllib.parse.quote(word)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={encoded_word}"
        return tts_url
    except Exception as e:
        logger.error(f"獲取語音URL失敗: {str(e)}")
        return None

def get_sentence_audio_url(sentence: str) -> str:
    """
    獲取例句的語音URL
    使用免費的文字轉語音API
    """
    try:
        # 使用 Google TTS API
        import urllib.parse
        encoded_sentence = urllib.parse.quote(sentence)
        tts_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={encoded_sentence}"
        return tts_url
    except Exception as e:
        logger.error(f"獲取例句語音URL失敗: {str(e)}")
        return None

def download_word_audio(word: str, save_path: str = None) -> str:
    """
    下載單字語音檔案
    
    Args:
        word: 要下載語音的單字
        save_path: 儲存路徑,如果為None則使用預設路徑
        
    Returns:
        str: 下載的檔案路徑
    """
    try:
        if save_path is None:
            # 創建音檔目錄
            audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'audio')
            os.makedirs(audio_dir, exist_ok=True)
            save_path = os.path.join(audio_dir, f'{word}.mp3')
        
        # 如果檔案已存在,直接返回
        if os.path.exists(save_path):
            logger.info(f"語音檔案已存在: {save_path}")
            return save_path
        
        # 下載語音
        tts_url = get_word_audio_url(word)
        if tts_url:
            response = requests.get(tts_url, timeout=10)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"成功下載語音檔案: {save_path}")
                return save_path
        
        return None
    except Exception as e:
        logger.error(f"下載語音檔案失敗: {str(e)}")
        return None

# 測試功能
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("="*50)
    print("每日英語服務測試")
    print("="*50)
    
    # 測試獲取今日單字
    word_data = get_daily_word()
    print(f"\n今天是一年中的第 {get_day_of_year()} 天")
    print(f"單字: {word_data['word']}")
    print(f"詞性: {word_data['pos']}")
    print(f"意思: {word_data['meaning']}")
    
    # 測試格式化訊息
    print("\n" + "="*50)
    print("格式化訊息:")
    print("="*50)
    print(format_daily_english_message(word_data))
    
    # 測試語音URL
    print("\n" + "="*50)
    word_audio_url = get_word_audio_url(word_data['word'])
    print(f"單字語音URL: {word_audio_url}")
    
    sentence_audio_url = get_sentence_audio_url(word_data['sentence'])
    print(f"例句語音URL: {sentence_audio_url}")
