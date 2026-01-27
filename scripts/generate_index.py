#!/usr/bin/env python3
"""
生成 GitHub Pages 索引页面
"""

import os
import glob
from datetime import datetime

reports_dir = "reports"

# 查找所有 HTML 报告
html_files = glob.glob(os.path.join(reports_dir, "btc_analysis_*.html"))
html_files.sort(reverse=True)  # 最新的在前

# 生成 index.html
index_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTC 动能分析报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .report-list {
            list-style: none;
            padding: 0;
        }
        .report-item {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .report-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .report-link {
            text-decoration: none;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .report-title {
            font-weight: bold;
            color: #667eea;
        }
        .report-time {
            color: #666;
            font-size: 0.9em;
        }
        .no-reports {
            text-align: center;
            color: #999;
            padding: 40px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 BTC 动能分析报告</h1>
        <p class="subtitle">多时间级别动能理论分析</p>

        <ul class="report-list">
"""

if html_files:
    for html_file in html_files:
        filename = os.path.basename(html_file)
        # 从文件名提取时间戳
        try:
            # 文件名格式: btc_analysis_20260127_115211.html
            timestamp_str = filename.replace("btc_analysis_", "").replace(".html", "")
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            display_time = filename

        index_content += f"""
            <li class="report-item">
                <a href="reports/{filename}" class="report-link">
                    <span class="report-title">📈 分析报告 - {display_time}</span>
                    <span class="report-time">查看详情 →</span>
                </a>
            </li>
"""
else:
    index_content += """
            <li class="no-reports">
                暂无报告
                <br><br>
                报告会在每小时自动生成
            </li>
"""

index_content += f"""
        </ul>

        <div class="footer">
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>GitHub Pages 自动部署</p>
        </div>
    </div>
</body>
</html>
"""

# 写入根目录的 index.html
with open("index.html", "w", encoding="utf-8") as f:
    f.write(index_content)

print("✅ index.html 已生成")
print(f"   包含 {len(html_files)} 个报告链接")
