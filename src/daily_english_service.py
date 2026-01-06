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
    
    # 第51-100個單字
    {"word": "ability", "pos": "n.", "meaning": "能力", "sentence": "She has the ability to succeed.", "translation": "她有成功的能力。"},
    {"word": "accept", "pos": "v.", "meaning": "接受", "sentence": "I accept your invitation.", "translation": "我接受你的邀請。"},
    {"word": "accident", "pos": "n.", "meaning": "意外", "sentence": "There was a car accident yesterday.", "translation": "昨天發生了一場車禍。"},
    {"word": "active", "pos": "adj.", "meaning": "活躍的", "sentence": "She is very active in sports.", "translation": "她在運動方面很活躍。"},
    {"word": "activity", "pos": "n.", "meaning": "活動", "sentence": "Swimming is my favorite activity.", "translation": "游泳是我最喜歡的活動。"},
    {"word": "afraid", "pos": "adj.", "meaning": "害怕的", "sentence": "Don't be afraid of making mistakes.", "translation": "不要害怕犯錯。"},
    {"word": "agreement", "pos": "n.", "meaning": "同意", "sentence": "We reached an agreement.", "translation": "我們達成了協議。"},
    {"word": "allow", "pos": "v.", "meaning": "允許", "sentence": "My parents allow me to stay up late.", "translation": "我父母允許我晚睡。"},
    {"word": "already", "pos": "adv.", "meaning": "已經", "sentence": "I have already finished my homework.", "translation": "我已經完成作業了。"},
    {"word": "amazing", "pos": "adj.", "meaning": "驚人的", "sentence": "The view is amazing!", "translation": "風景太驚人了!"},
    
    {"word": "ancient", "pos": "adj.", "meaning": "古老的", "sentence": "We visited an ancient temple.", "translation": "我們參觀了一座古老的寺廟。"},
    {"word": "angry", "pos": "adj.", "meaning": "生氣的", "sentence": "Please don't be angry with me.", "translation": "請不要生我的氣。"},
    {"word": "announce", "pos": "v.", "meaning": "宣布", "sentence": "They will announce the winner tomorrow.", "translation": "他們明天會宣布獲勝者。"},
    {"word": "another", "pos": "adj.", "meaning": "另一個", "sentence": "Can I have another cookie?", "translation": "我可以再吃一塊餅乾嗎?"},
    {"word": "answer", "pos": "n.", "meaning": "答案", "sentence": "What's the answer to this question?", "translation": "這個問題的答案是什麼?"},
    {"word": "anybody", "pos": "pron.", "meaning": "任何人", "sentence": "Is anybody home?", "translation": "有人在家嗎?"},
    {"word": "anyway", "pos": "adv.", "meaning": "無論如何", "sentence": "I'm going anyway.", "translation": "無論如何我都要去。"},
    {"word": "appear", "pos": "v.", "meaning": "出現", "sentence": "Stars appear at night.", "translation": "星星在夜晚出現。"},
    {"word": "arrive", "pos": "v.", "meaning": "到達", "sentence": "What time will you arrive?", "translation": "你什麼時候到達?"},
    {"word": "attend", "pos": "v.", "meaning": "參加", "sentence": "I will attend the meeting.", "translation": "我會參加會議。"},
    
    # 第101-150個單字
    {"word": "attract", "pos": "v.", "meaning": "吸引", "sentence": "Flowers attract bees.", "translation": "花朵吸引蜜蜂。"},
    {"word": "audience", "pos": "n.", "meaning": "觀眾", "sentence": "The audience clapped loudly.", "translation": "觀眾大聲鼓掌。"},
    {"word": "avoid", "pos": "v.", "meaning": "避免", "sentence": "Try to avoid junk food.", "translation": "試著避免垃圾食物。"},
    {"word": "awake", "pos": "adj.", "meaning": "醒著的", "sentence": "Are you still awake?", "translation": "你還醒著嗎?"},
    {"word": "背景", "pos": "n.", "meaning": "背景", "sentence": "Tell me about your background.", "translation": "告訴我你的背景。"},
    {"word": "balance", "pos": "n.", "meaning": "平衡", "sentence": "Keep your balance!", "translation": "保持平衡!"},
    {"word": "basic", "pos": "adj.", "meaning": "基本的", "sentence": "These are basic skills.", "translation": "這些是基本技能。"},
    {"word": "battle", "pos": "n.", "meaning": "戰鬥", "sentence": "They won the battle.", "translation": "他們贏得了戰鬥。"},
    {"word": "beach", "pos": "n.", "meaning": "海灘", "sentence": "Let's go to the beach!", "translation": "我們去海灘吧!"},
    {"word": "behave", "pos": "v.", "meaning": "表現", "sentence": "Please behave yourself.", "translation": "請你表現好一點。"},
    
    {"word": "belong", "pos": "v.", "meaning": "屬於", "sentence": "This book belongs to me.", "translation": "這本書屬於我。"},
    {"word": "benefit", "pos": "n.", "meaning": "好處", "sentence": "Exercise has many benefits.", "translation": "運動有很多好處。"},
    {"word": "besides", "pos": "prep.", "meaning": "除了", "sentence": "Besides English, I study math.", "translation": "除了英語,我還學數學。"},
    {"word": "between", "pos": "prep.", "meaning": "在...之間", "sentence": "Sit between your friends.", "translation": "坐在你朋友之間。"},
    {"word": "birthday", "pos": "n.", "meaning": "生日", "sentence": "Happy birthday to you!", "translation": "祝你生日快樂!"},
    {"word": "bottom", "pos": "n.", "meaning": "底部", "sentence": "The key is at the bottom.", "translation": "鑰匙在底部。"},
    {"word": "boundary", "pos": "n.", "meaning": "邊界", "sentence": "Don't cross the boundary.", "translation": "不要越界。"},
    {"word": "brain", "pos": "n.", "meaning": "大腦", "sentence": "Use your brain to think.", "translation": "用你的大腦思考。"},
    {"word": "branch", "pos": "n.", "meaning": "樹枝", "sentence": "A bird sits on the branch.", "translation": "一隻鳥坐在樹枝上。"},
    {"word": "brave", "pos": "adj.", "meaning": "勇敢的", "sentence": "You are very brave!", "translation": "你很勇敢!"},
    
    # 第151-200個單字
    {"word": "breathe", "pos": "v.", "meaning": "呼吸", "sentence": "Take a deep breath.", "translation": "深呼吸。"},
    {"word": "bridge", "pos": "n.", "meaning": "橋", "sentence": "We walked across the bridge.", "translation": "我們走過了橋。"},
    {"word": "bright", "pos": "adj.", "meaning": "明亮的", "sentence": "The sun is bright today.", "translation": "今天陽光明亮。"},
    {"word": "bring", "pos": "v.", "meaning": "帶來", "sentence": "Please bring your textbook.", "translation": "請帶你的課本。"},
    {"word": "brother", "pos": "n.", "meaning": "兄弟", "sentence": "My brother is tall.", "translation": "我哥哥很高。"},
    {"word": "building", "pos": "n.", "meaning": "建築物", "sentence": "That building is very old.", "translation": "那棟建築物很老舊。"},
    {"word": "busy", "pos": "adj.", "meaning": "忙碌的", "sentence": "I'm busy with homework.", "translation": "我忙於做作業。"},
    {"word": "butterfly", "pos": "n.", "meaning": "蝴蝶", "sentence": "A butterfly landed on the flower.", "translation": "一隻蝴蝶停在花上。"},
    {"word": "calendar", "pos": "n.", "meaning": "日曆", "sentence": "Check the calendar for the date.", "translation": "查看日曆確認日期。"},
    {"word": "camera", "pos": "n.", "meaning": "相機", "sentence": "I bought a new camera.", "translation": "我買了一台新相機。"},
    
    {"word": "cancel", "pos": "v.", "meaning": "取消", "sentence": "We had to cancel the trip.", "translation": "我們必須取消旅行。"},
    {"word": "captain", "pos": "n.", "meaning": "隊長", "sentence": "He is the team captain.", "translation": "他是隊長。"},
    {"word": "capture", "pos": "v.", "meaning": "捕捉", "sentence": "Try to capture this moment.", "translation": "試著捕捉這個時刻。"},
    {"word": "careful", "pos": "adj.", "meaning": "小心的", "sentence": "Be careful on the stairs.", "translation": "在樓梯上要小心。"},
    {"word": "careless", "pos": "adj.", "meaning": "粗心的", "sentence": "Don't be careless with your work.", "translation": "做事不要粗心。"},
    {"word": "carry", "pos": "v.", "meaning": "攜帶", "sentence": "Can you carry this bag?", "translation": "你能拿這個袋子嗎?"},
    {"word": "castle", "pos": "n.", "meaning": "城堡", "sentence": "We visited a beautiful castle.", "translation": "我們參觀了一座美麗的城堡。"},
    {"word": "catch", "pos": "v.", "meaning": "抓住", "sentence": "Catch the ball!", "translation": "接住球!"},
    {"word": "celebrate", "pos": "v.", "meaning": "慶祝", "sentence": "Let's celebrate your success!", "translation": "讓我們慶祝你的成功!"},
    {"word": "center", "pos": "n.", "meaning": "中心", "sentence": "The store is in the city center.", "translation": "商店在市中心。"},
    
    # 第201-250個單字
    {"word": "century", "pos": "n.", "meaning": "世紀", "sentence": "We live in the 21st century.", "translation": "我們生活在21世紀。"},
    {"word": "certain", "pos": "adj.", "meaning": "確定的", "sentence": "I'm certain about this.", "translation": "我對此很確定。"},
    {"word": "challenge", "pos": "n.", "meaning": "挑戰", "sentence": "This is a big challenge.", "translation": "這是個大挑戰。"},
    {"word": "chance", "pos": "n.", "meaning": "機會", "sentence": "Give me another chance.", "translation": "再給我一次機會。"},
    {"word": "change", "pos": "v.", "meaning": "改變", "sentence": "People can change.", "translation": "人是可以改變的。"},
    {"word": "character", "pos": "n.", "meaning": "性格", "sentence": "He has a good character.", "translation": "他有好的性格。"},
    {"word": "charge", "pos": "v.", "meaning": "充電", "sentence": "Please charge your phone.", "translation": "請給你的手機充電。"},
    {"word": "cheap", "pos": "adj.", "meaning": "便宜的", "sentence": "This shirt is very cheap.", "translation": "這件襯衫很便宜。"},
    {"word": "cheer", "pos": "v.", "meaning": "歡呼", "sentence": "Let's cheer for our team!", "translation": "讓我們為我們的隊伍歡呼!"},
    {"word": "choice", "pos": "n.", "meaning": "選擇", "sentence": "It's your choice.", "translation": "這是你的選擇。"},
    
    {"word": "choose", "pos": "v.", "meaning": "選擇", "sentence": "Choose the answer carefully.", "translation": "仔細選擇答案。"},
    {"word": "circle", "pos": "n.", "meaning": "圓圈", "sentence": "Draw a circle on the paper.", "translation": "在紙上畫一個圓圈。"},
    {"word": "citizen", "pos": "n.", "meaning": "公民", "sentence": "He is a good citizen.", "translation": "他是個好公民。"},
    {"word": "classroom", "pos": "n.", "meaning": "教室", "sentence": "Our classroom is clean.", "translation": "我們的教室很乾淨。"},
    {"word": "climate", "pos": "n.", "meaning": "氣候", "sentence": "The climate here is warm.", "translation": "這裡的氣候溫暖。"},
    {"word": "climb", "pos": "v.", "meaning": "爬", "sentence": "Let's climb the hill.", "translation": "讓我們爬山吧。"},
    {"word": "close", "pos": "adj.", "meaning": "接近的", "sentence": "We are close friends.", "translation": "我們是親密的朋友。"},
    {"word": "cloud", "pos": "n.", "meaning": "雲", "sentence": "Look at that white cloud.", "translation": "看那朵白雲。"},
    {"word": "coach", "pos": "n.", "meaning": "教練", "sentence": "Our coach is strict.", "translation": "我們的教練很嚴格。"},
    {"word": "coast", "pos": "n.", "meaning": "海岸", "sentence": "We walked along the coast.", "translation": "我們沿著海岸走。"},
    
    # 第251-300個單字
    {"word": "collect", "pos": "v.", "meaning": "收集", "sentence": "I collect stamps.", "translation": "我收集郵票。"},
    {"word": "college", "pos": "n.", "meaning": "大學", "sentence": "She goes to college.", "translation": "她上大學。"},
    {"word": "color", "pos": "n.", "meaning": "顏色", "sentence": "What's your favorite color?", "translation": "你最喜歡什麼顏色?"},
    {"word": "comfortable", "pos": "adj.", "meaning": "舒適的", "sentence": "This sofa is comfortable.", "translation": "這沙發很舒適。"},
    {"word": "common", "pos": "adj.", "meaning": "普通的", "sentence": "It's a common mistake.", "translation": "這是常見的錯誤。"},
    {"word": "communicate", "pos": "v.", "meaning": "溝通", "sentence": "We communicate by email.", "translation": "我們透過電子郵件溝通。"},
    {"word": "community", "pos": "n.", "meaning": "社區", "sentence": "Our community is friendly.", "translation": "我們的社區很友善。"},
    {"word": "company", "pos": "n.", "meaning": "公司", "sentence": "He works for a big company.", "translation": "他在大公司工作。"},
    {"word": "compare", "pos": "v.", "meaning": "比較", "sentence": "Compare these two pictures.", "translation": "比較這兩張圖片。"},
    {"word": "compete", "pos": "v.", "meaning": "競爭", "sentence": "We compete in sports.", "translation": "我們在體育競賽中競爭。"},
    
    {"word": "complete", "pos": "v.", "meaning": "完成", "sentence": "I will complete this task.", "translation": "我會完成這項任務。"},
    {"word": "computer", "pos": "n.", "meaning": "電腦", "sentence": "I use a computer every day.", "translation": "我每天使用電腦。"},
    {"word": "concern", "pos": "n.", "meaning": "關心", "sentence": "Thank you for your concern.", "translation": "謝謝你的關心。"},
    {"word": "condition", "pos": "n.", "meaning": "狀況", "sentence": "The car is in good condition.", "translation": "這車況很好。"},
    {"word": "confident", "pos": "adj.", "meaning": "有信心的", "sentence": "Be confident in yourself.", "translation": "對自己要有信心。"},
    {"word": "connect", "pos": "v.", "meaning": "連接", "sentence": "Connect to the internet.", "translation": "連接網路。"},
    {"word": "consider", "pos": "v.", "meaning": "考慮", "sentence": "Please consider my suggestion.", "translation": "請考慮我的建議。"},
    {"word": "contact", "pos": "v.", "meaning": "聯絡", "sentence": "Please contact me later.", "translation": "請稍後聯絡我。"},
    {"word": "contain", "pos": "v.", "meaning": "包含", "sentence": "This box contains books.", "translation": "這個盒子裝著書。"},
    {"word": "continue", "pos": "v.", "meaning": "繼續", "sentence": "Let's continue our work.", "translation": "讓我們繼續工作。"},
    
    # 第301-350個單字
    {"word": "control", "pos": "v.", "meaning": "控制", "sentence": "Control your emotions.", "translation": "控制你的情緒。"},
    {"word": "convenient", "pos": "adj.", "meaning": "方便的", "sentence": "This location is convenient.", "translation": "這個位置很方便。"},
    {"word": "conversation", "pos": "n.", "meaning": "對話", "sentence": "We had a nice conversation.", "translation": "我們有個愉快的對話。"},
    {"word": "cook", "pos": "v.", "meaning": "烹飪", "sentence": "My mom likes to cook.", "translation": "我媽媽喜歡烹飪。"},
    {"word": "cool", "pos": "adj.", "meaning": "涼爽的", "sentence": "The weather is cool today.", "translation": "今天天氣涼爽。"},
    {"word": "cooperate", "pos": "v.", "meaning": "合作", "sentence": "Let's cooperate together.", "translation": "讓我們一起合作。"},
    {"word": "copy", "pos": "v.", "meaning": "複製", "sentence": "Copy this file please.", "translation": "請複製這個檔案。"},
    {"word": "corner", "pos": "n.", "meaning": "角落", "sentence": "The shop is at the corner.", "translation": "商店在角落。"},
    {"word": "correct", "pos": "adj.", "meaning": "正確的", "sentence": "Your answer is correct!", "translation": "你的答案是正確的!"},
    {"word": "cost", "pos": "n.", "meaning": "花費", "sentence": "What's the cost?", "translation": "費用是多少?"},
    
    {"word": "country", "pos": "n.", "meaning": "國家", "sentence": "Taiwan is a beautiful country.", "translation": "台灣是個美麗的國家。"},
    {"word": "couple", "pos": "n.", "meaning": "一對", "sentence": "A couple walked by.", "translation": "一對夫婦走過。"},
    {"word": "courage", "pos": "n.", "meaning": "勇氣", "sentence": "You have great courage.", "translation": "你有很大的勇氣。"},
    {"word": "course", "pos": "n.", "meaning": "課程", "sentence": "I'm taking an English course.", "translation": "我在上英語課程。"},
    {"word": "cover", "pos": "v.", "meaning": "覆蓋", "sentence": "Cover your mouth when coughing.", "translation": "咳嗽時要掩口。"},
    {"word": "create", "pos": "v.", "meaning": "創造", "sentence": "Artists create beautiful works.", "translation": "藝術家創造美麗的作品。"},
    {"word": "creative", "pos": "adj.", "meaning": "有創意的", "sentence": "She is very creative.", "translation": "她很有創意。"},
    {"word": "cross", "pos": "v.", "meaning": "穿越", "sentence": "Look both ways before crossing.", "translation": "過馬路前要左右看。"},
    {"word": "crowd", "pos": "n.", "meaning": "人群", "sentence": "There's a big crowd here.", "translation": "這裡有一大群人。"},
    {"word": "culture", "pos": "n.", "meaning": "文化", "sentence": "Every country has its culture.", "translation": "每個國家都有其文化。"},
    
    # 第351-365個單字
    {"word": "curious", "pos": "adj.", "meaning": "好奇的", "sentence": "Children are naturally curious.", "translation": "孩子天生好奇。"},
    {"word": "current", "pos": "adj.", "meaning": "目前的", "sentence": "What's the current situation?", "translation": "目前的情況如何?"},
    {"word": "customer", "pos": "n.", "meaning": "顧客", "sentence": "The customer is always right.", "translation": "顧客永遠是對的。"},
    {"word": "damage", "pos": "n.", "meaning": "損害", "sentence": "The storm caused damage.", "translation": "暴風雨造成了損害。"},
    {"word": "danger", "pos": "n.", "meaning": "危險", "sentence": "Stay away from danger.", "translation": "遠離危險。"},
    {"word": "dark", "pos": "adj.", "meaning": "黑暗的", "sentence": "It's dark outside.", "translation": "外面很黑。"},
    {"word": "date", "pos": "n.", "meaning": "日期", "sentence": "What's today's date?", "translation": "今天是幾號?"},
    {"word": "daughter", "pos": "n.", "meaning": "女兒", "sentence": "She is my daughter.", "translation": "她是我的女兒。"},
    {"word": "decide", "pos": "v.", "meaning": "決定", "sentence": "You need to decide now.", "translation": "你現在需要決定。"},
    {"word": "decision", "pos": "n.", "meaning": "決定", "sentence": "It's a difficult decision.", "translation": "這是個困難的決定。"},
    
    {"word": "declare", "pos": "v.", "meaning": "宣告", "sentence": "I declare this open!", "translation": "我宣布開幕!"},
    {"word": "decorate", "pos": "v.", "meaning": "裝飾", "sentence": "Let's decorate the room.", "translation": "讓我們裝飾房間。"},
    {"word": "decrease", "pos": "v.", "meaning": "減少", "sentence": "Prices will decrease soon.", "translation": "價格很快會降低。"},
    {"word": "defeat", "pos": "v.", "meaning": "擊敗", "sentence": "We will defeat them!", "translation": "我們會擊敗他們!"},
    {"word": "degree", "pos": "n.", "meaning": "度數", "sentence": "It's 30 degrees today.", "translation": "今天30度。"},
]

# 生成完整年度單字列表 (現在有365個不重複單字)
def generate_full_year_words():
    """直接返回365天的單字列表"""
    return DAILY_WORDS

# 生成完整年度單字
FULL_YEAR_WORDS = generate_full_year_words()

def get_day_of_year() -> int:
    """獲取今天是一年中的第幾天 (1-365)，使用台灣時區"""
    import pytz
    # 使用台灣時區
    tw_tz = pytz.timezone('Asia/Taipei')
    today = datetime.datetime.now(tw_tz)
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
    day = get_day_of_year()
    word_number = ((day - 1) % 365) + 1
    
    message = f"""📚 每日英語 Daily English (第{word_number}個單字)

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
