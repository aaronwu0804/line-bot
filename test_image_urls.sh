#!/bin/bash
# 測試圖片 URL 是否可訪問

echo "開始測試圖片 URL..."

# 測試函數
test_url() {
    url="$1"
    desc="$2"
    echo ""
    echo "測試: $url ($desc)"
    
    # 使用 curl 測試 URL
    status_code=$(curl -s -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" "$url")
    
    if [ "$status_code" = "200" ]; then
        echo "✅ 狀態碼: $status_code - URL 可用"
    else
        echo "❌ 狀態碼: $status_code - URL 不可用"
    fi
}

# Pinterest 圖片
test_url "https://i.pinimg.com/originals/e5/73/7c/e5737c44dd061635766b6682a3e42d69.jpg" "早安花朵文字"
test_url "https://i.pinimg.com/originals/11/32/7a/11327a45919c5d5104a4ce9eecae58d4.jpg" "水彩風格早安"
test_url "https://i.pinimg.com/originals/69/6a/7e/696a7e415b405bd58b6b8c82e2d8d7ff.jpg" "早安咖啡文字"
test_url "https://i.pinimg.com/originals/d1/27/7d/d1277da3e2cca7c5367c408dac59ccb9.jpg" "早安花環"

# Pixabay 圖片
test_url "https://cdn.pixabay.com/photo/2017/11/06/17/05/good-morning-2924423_1280.jpg" "木牌早安文字"
test_url "https://cdn.pixabay.com/photo/2019/12/07/04/17/good-morning-4678832_1280.jpg" "早安花卉文字"

# Imgur 圖片
test_url "https://i.imgur.com/tSNCNn5.jpg" "早安鮮花"
test_url "https://i.imgur.com/KraJJvg.jpg" "早安日出"

# Unsplash 圖片
test_url "https://images.unsplash.com/photo-1552346989-e069318e20a5?w=800&q=80" "清晨咖啡"
test_url "https://images.unsplash.com/photo-1470240731273-7821a6eeb6bd?w=800&q=80" "早安日出"

echo ""
echo "測試完成！"
