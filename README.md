# 🔨 夜市釘孤枝 (Night Market Nail Hammer)

**目前版本：煉獄挑戰 1.3，25 秒／5 根，落空扣 4 秒、敲歪扣 7 秒。**

> 台灣經典夜市遊戲「釘孤枝」！一邊平頭、一邊尖頭的鐵鎚，看準力道一槌把大鋼釘剛好釘平！

🎮 **3D 完整版線上試玩**：[https://nutcelvischen-jpg.github.io/night-market-hammer/](https://nutcelvischen-jpg.github.io/night-market-hammer/)  
📱 **手機極速簡化版**：[https://nutcelvischen-jpg.github.io/night-market-hammer-mobile/](https://nutcelvischen-jpg.github.io/night-market-hammer-mobile/)  
🗣️ **配音試聽頁**：[攤主開講試聽](https://nutcelvischen-jpg.github.io/night-market-hammer/voice-preview.html)

---

## 📸 遊戲畫面

![遊戲主畫面](game_bright_preview.png)

---

## 🎯 遊戲特色與玩法

- **一邊平頭・一邊尖頭**：隨時切換平頭（穩重）與尖頭（暴擊穿透）。
- **蓄力揮擊**：按住空白鍵或點擊按鈕蓄力，放開猛力下砸！
- **電影級慢動作**：揮鎚向下那一刻自動觸發 Bullet-Time 慢動作，細膩呈現每一毫米沉入木頭的過程。
- **道地台語配音**：
  - 開場：「叮叮當！敲壞不用賠！」
  - 落空：「你咧拍空氣喔？」/「哎喲，你咧疼伊喔？」
  - 敲歪：「釘仔咧跳舞喔？」/「免賠啦！我心疼爾爾。」
  - 成功齊平：「保利達 B！！」
- **極致輕量 3D**：所有 GLB 模型總計小於 100KB，全裝置流暢 60FPS。

---

## 🛠️ 技術架構

- **渲染引擎**：Three.js (WebGL) + OrbitControls + GLTFLoader
- **3D 建模**：Blender 5.1 (Procedural bmesh, PBR, GLTF export)
- **音效與配音**：Web Audio API 即時物理合成音效 + Gemini 3.8 Flash TTS 道地台語配音

## 硬漢難度更新（2026-10-22）

每局 45 秒。落空扣 2 秒、敲歪扣 3 秒。尖頭瞄準更快且帶變速，每次重瞄有不同起點；正中區縮至半徑 2mm，擦邊力量上限 45%。釘平高度需落在 2–4mm，尖頭超過 88% 力量會彎釘。隨已完成／打歪釘子數量加快準星與蓄力；綠色力量提示依實際判定更新。原本六段配音保留。修改前備份在 backups/index.before-hard.html。

## 地獄難度 1.2（2026-10-22）

目前版本取代上面的硬漢規則：35 秒、落空扣 3 秒、敲歪扣 5 秒。準星與蓄力再加速；尖頭正中圈半徑 1.5mm，擦邊門檻 4.5mm、力量上限 40%，尖頭最大力量 86%。釘平高度縮為 2.2–3.8mm，綠色力量範圍與判定同步。原六段配音不變。前版程式在 backups/before-hell，相鄰 night_market_hammer_hard_v1.1.zip 為前版完整備份。本機及 ZIP 已更新；線上版本需自行推送。

## 力量提示修正 1.2.1

瞄偏時，一槌釘平所需力道可能高於安全上限，因此原本沒有綠區。現在綠區代表本槌釘平、黃區代表安全輕敲（仍需補槌）；完全瞄空時明確顯示「無命中區，請重瞄」。目標色區置於蓄力色條上方，並顯示實際力量百分比。沒有放寬命中或力道判定，35 秒與扣秒規則、原六段配音不變。

## 煉獄挑戰 1.3

本版取代前述 35 秒規則：25 秒完成五根，落空扣 4 秒，敲歪扣 7 秒。第一根準星約快 27–29%，後續逐根加速，最後一根比前版快約 30%。力量判定、綠區寬度和蓄力節奏沿用 1.2.1，避免小螢幕與低幀率手機錯失提示；綠區釘平、黃區輕敲、瞄空請重瞄，六段音檔不變。前版程式在 backups/before-inferno；完整前版 ZIP 為相鄰的 *_v1.2.1.zip。本機及新 ZIP 已更新，線上版需自行推送。
