import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import base64

# Konfigurasi Tampilan Halaman Utama UI
st.set_page_config(
    page_title="Manga & Manhwa Chapter Merger",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk mempercantik UI dan menyatukan gambar rapat ke bawah
st.markdown("""
    <style>
    .main { background-color: #0f111a; }
    h1 { color: #ff4b4b; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    img { margin-bottom: -6px !important; display: block; margin-left: auto; margin-right: auto; width: 100%; }
    div[data-testid="stImage"] { margin-bottom: -20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 WestManga Chapter Merger")
st.markdown("<p style='text-align: center; color: #888;'>Sistem Bypass Hotlink Aktif - Gambar Dimuat Lewat Jalur Proksi Server.</p>", unsafe_allow_html=True)
st.divider()

# Input Link/URL dari halaman baca komik
url_input = st.text_input(
    "🔗 Tempel URL Baca Chapter di Sini:", 
    placeholder="Contoh: https://westmanga.cc"
)

# Fungsi untuk mengunduh gambar dan mengubahnya menjadi format Base64 agar lolos Hotlink Protection
def get_proxied_image_base64(image_url, referer_url):
    proxy_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Referer': referer_url,
        'Connection': 'keep-alive'
    }
    try:
        img_response = requests.get(image_url, headers=proxy_headers, timeout=10)
        if img_response.status_code == 200:
            # Mengubah biner gambar menjadi string teks Base64 aman
            encoded_string = base64.b64encode(img_response.content).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded_string}"
    except:
        pass
    return None

if url_input:
    match = re.search(r'(.*-chapter-)(\d+)(.*)', url_input)
    
    if match:
        base_url_left = match.group(1)   
        current_ch_str = match.group(2) 
        base_url_right = match.group(3)  
        
        current_ch_num = int(current_ch_str)
        padding_length = len(current_ch_str) 
        
        st.success(f"✅ Komik Terdeteksi! Bersiap memproses Chapter {current_ch_num}.")
        
        st.write("### 🎛️ Pilih Rentang Chapter yang Ingin Digabungkan")
        col1, col2 = st.columns(2)
        with col1:
            start_ch = st.number_input("Mulai Dari Chapter:", min_value=1, value=current_ch_num, step=1)
        with col2:
            end_ch = st.number_input("Sampai Dengan Chapter:", min_value=1, value=current_ch_num + 2, step=1) # Default 3 chapter agar loading stabil
            
        if start_ch > end_ch:
            st.warning("⚠️ Peringatan: Chapter 'Mulai' tidak boleh lebih besar dari Chapter 'Sampai'.")
        else:
            if st.button("🚀 GABUNGKAN & BYPASS HOTLINK", type="primary"):
                st.divider()
                st.info(f"📖 Sedang menjahit gambar dari Chapter {start_ch} hingga {end_ch}...")
                
                html_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': 'https://westmanga.cc'
                }
                
                for ch_num in range(start_ch, end_ch + 1):
                    ch_str_formatted = str(ch_num).zfill(padding_length)
                    target_url = f"{base_url_left}{ch_str_formatted}{base_url_right}"
                    
                    st.markdown(f"<h3 style='text-align: center; color: #ff4b4b; background-color: #1e2235; padding: 10px; border-radius: 5px; margin-top: 20px;'>📌 CHAPTER {ch_num}</h3>", unsafe_allow_html=True)
                    
                    try:
                        response = requests.get(target_url, headers=html_headers, timeout=15)
                        
                        if response.status_code == 404:
                            st.warning(f"📭 Chapter {ch_num} tidak ditemukan. Proses dihentikan.")
                            break
                        elif response.status_code == 403:
                            st.error(f"❌ Server memblokir akses ke halaman web Chapter {ch_num}.")
                            break
                        elif response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # Menggunakan pencarian berbasis pola flex-col untuk struktur web baru WestManga
                            reader_area = soup.find('div', class_=lambda x: x and 'flex-col' in x and 'items-center' in x)
                            
                            if not reader_area:
                                # Skema cadangan jika kontainer fleksibel gagal ditangkap
                                img_containers = soup.find_all('div', class_=lambda x: x and 'relative' in x and 'justify-center' in x)
                                images = [container.find('img') for container in img_containers if container.find('img')]
                            else:
                                images = reader_area.find_all('img')
                            
                            img_count = 0
                            if images:
                                for img in images:
                                    img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                                    if img_url:
                                        img_url = img_url.strip()
                                        if ' ' in img_url:
                                            img_url = img_url.split(' ')[0]
                                        if img_url.startswith('//'):
                                            img_url = "https:" + img_url
                                            
                                        # PROSES BYPASS: Ambil stream data gambar asli lewat Proksi internal backend
                                        proxied_img_data = get_proxied_image_base64(img_url, target_url)
                                        
                                        if proxied_img_data:
                                            st.image(proxied_img_data, use_column_width=True)
                                            img_count += 1
                                
                                if img_count == 0:
                                    st.caption(f"⚠️ Gambar di Chapter {ch_num} terdeteksi namun proksi gagal mengunduhnya.")
                            else:
                                st.warning(f"❌ Struktur HTML tag gambar tidak ditemukan pada halaman Chapter {ch_num}.")
                    except Exception as e:
                        st.error(f"❌ Gangguan teknis pada Chapter {ch_num}: {e}")
                        break
    else:
        st.error("❌ Format URL tidak dikenali. Pastikan menyalin tautan halaman baca bab aktif.")
