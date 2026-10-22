# 夜市老闆配音 v2 粗獷版

六段本機 MP3，由 OpenRouter 的 Gemini TTS 產生，統一 Algenib 聲線。台詞以台羅餵入，語氣提示指定台灣台語、更厚重的低音、明顯沙啞邊緣、台灣夜市攤主的叫賣節奏。品牌喊聲依「保力達 B」發音提示，畫面沿用玩家指定的「保利達 B」。

- 試聽： http://localhost:8092/voice-preview.html
- 台詞與提示： ../voice_lines.json
- 重製：設定 OPENROUTER_API_KEY 環境變數後，執行 `python3 scripts/generate_voice.py`；後面可指定 intro、success 等單句 ID。
- 金鑰不在專案內。產生腳本沿用 shotgameskill 的 PCM 轉 MP3 流程，改由 curl 的標準輸入帶入驗證標頭；不在終端或程序參數列顯示金鑰。
- 修改字幕或台羅時，同步更新 index.html 的 BOSS_LINES；測試會檢查兩邊一致。

遊戲：首次瞄準／蓄力喊開場，落空與敲歪各兩句輪替，釘平喊成功。半途釘入不插話，避免洗版。只有最終判定有效的命中才觸發結果配音。所有聲音共用靜音開關，配音時降低敲擊音效，重開及切到背景時停止對話。預先載入音檔，但必須點擊才啟動音訊。

已檢查六檔解碼、長度、音量峰值、事件觸發與中斷行為。台語口音與硬漢表演仍以實際試聽為準，未經母語者逐句審聽。

台羅用字核對參考：教育部辭典的[疼 thiànn](https://sutian.moe.edu.tw/zh-hant/su/6340/)、[爾爾 niā-niā](https://sutian.moe.edu.tw/zh-hant/su/10653/)。整句與笑點為本遊戲撰寫。

## v2 調整

六句全部重新生成，強化胸腔投射、粗糙嗓音與在地攤主語氣。成功句提示改為三段重音接短暫停頓，再爆喊 B。以低頻與清晰度 EQ、輕度壓縮和峰值限制處理。舊版音檔與提示保存在 backups/voice-v1。

聲線選擇參考 [Google 官方聲線表](https://ai.google.dev/gemini-api/docs/speech-generation)，Algenib 的描述為 Gravelly。最終口音與表演以試聽為準。
