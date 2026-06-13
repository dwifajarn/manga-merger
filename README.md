# 📚 Manga & Manhwa Chapter Merger

A web-based tool built with Python and Streamlit designed to scrape, merge, and display multiple comic chapters into a single, seamless vertical page (Webtoon style). This application bypasses manual clicking by aggregating chapter images dynamically into an ad-free reading interface.

---

## ✨ Features

- **Direct URL Scraping:** Simply copy and paste the main manga profile link.
- **Batch Selection:** Choose a specific range of chapters (e.g., Chapter 1 to 10) via a drop-down menu.
- **Seamless Webtoon Mode:** Images from selected chapters are combined vertically with zero margin spacing.
- **Lazy-Loading Bypass:** Automatically detects and extracts hidden image sources (`data-src`, `data-lazy-src`, etc.).
- **Clean UI:** Responsive layout optimized for both desktop and mobile web browsers.

---

## 🚀 How to Run Locally

If you want to test or run this tool on your local computer, follow these simple steps:

### Prerequisite
Make sure you have **Python 3.8+** installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com
cd YOUR-REPO-NAME
```

### 2. Install Dependencies
Install the required libraries listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Start the Application
Launch the Streamlit server:
```bash
streamlit run app.py
```
After running the command, your local browser will automatically open `http://localhost:8501`.

---

## ☁️ How to Deploy to Streamlit Community Cloud

Since this app requires a Python backend to perform web scraping and bypass browser CORS restrictions, it cannot be hosted directly on static platforms like GitHub Pages. Follow these steps to host it for free online:

1. Go to [share.streamlit.io](https://streamlit.io) and log in using your GitHub account.
2. Click on the **New app** or **Create app** button.
3. Select your repository, branch (`main`), and set the main file path to `app.py`.
4. Click **Deploy**. Your app will be live with a custom URL (e.g., `https://streamlit.app`) within a couple of minutes!

---

## 🛠️ Tech Stack

- **Frontend/Backend:** [Streamlit](https://streamlit.io)
- **Web Scraping:** [BeautifulSoup4](https://crummy.com) & [Requests](https://readthedocs.io)
- **Pattern Matching:** Regular Expressions (`re`)

---

## ⚠️ Disclaimer & Technical Limitations

- **Anti-Bot & Cloudflare Protection:** This tool interacts directly with third-party comic websites. If a target website updates its security or implements heavy Cloudflare anti-bot verification (Error 403), the scraping process may fail.
- **Educational Purposes Only:** This project is intended strictly for personal use, data parsing study, and accessibility experimentation. Please respect the bandwidth and content rights of original website owners.
# manga-merger
