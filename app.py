import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Konfigurasi Tampilan Halaman Utama UI
st.set_page_config(
    page_title="Manga & Manhwa Chapter Merger",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk mempercantik UI
st.markdown("""
    <style>
    .main { background-color: #0f111a; }
    h1 { color: #ff4b4b; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    img { margin-bottom: -5px !important; display: block; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 WestManga Chapter Merger")
st.markdown("<p style='text-align: center; color: #888;'>Tempelkan link chapter aktif, lalu pilih rentang chapter berikutnya secara otomatis.</p>", unsafe_allow_html=True)
st.divider()

# Input Link/URL dari halaman baca komik
url_input = st.text_input(
    "🔗 Tempel URL Baca Chapter di Sini:", 
    placeholder="Contoh: https://westmanga.cc"
)

if url_input:
    # Menggunakan regex untuk membedah struktur URL komik WestManga
    match = re.search(r'(.*-chapter-)(\d+)(.*)', url_input)
    
    if match:
        base_url_left = match.group(1)   
        current_ch_str = match.group(2) 
        base_url_right = match.group(3)  
        
        current_ch_num = int(current_ch_str)
        padding_length = len(current_ch_str) 
        
        st.success(f"✅ Sistem berhasil mendeteksi komik! Anda sedang membuka Chapter {current_ch_num}.")
        
        st.write("### 🎛️ Pilih Rentang Chapter yang Ingin Digabungkan")
        col1, col2 = st.columns(2)
        with col1:
            start_ch = st.number_input("Mulai Dari Chapter:", min_value=1, value=current_ch_num, step=1)
        with col2:
            end_ch = st.number_input("Sampai Dengan Chapter:", min_value=1, value=current_ch_num + 4, step=1)
            
        if start_ch > end_ch:
            st.warning("⚠️ Peringatan: Chapter 'Mulai' tidak boleh lebih besar dari Chapter 'Sampai'.")
        else:
            if st.button("🚀 GABUNGKAN & BACA SEKARANG", type="primary"):
                st.divider()
                st.info(f"📖 Memproses penggabungan dari Chapter {start_ch} hingga {end_ch}...")
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Referer': 'https://westmanga.cc'
                }
                
                for ch_num in range(start_ch, end_ch + 1):
                    ch_str_formatted = str(ch_num).zfill(padding_length)
                    target_url = f"{base_url_left}{ch_str_formatted}{base_url_right}"
                    
                    st.markdown(f"<h3 style='text-align: center; color: #ff4b4b; background-color: #1e2235; padding: 10px; border-radius: 5px; margin-top: 20px;'>📌 CHAPTER {ch_num}</h3>", unsafe_allow_html=True)
                    
                    try:
                        response = requests.get(target_url, headers=headers, timeout=15)
                        
                        if response.status_code == 404:
                            st.warning(f"📭 Chapter {ch_num} tidak ditemukan atau belum rilis (Status 404). Proses dihentikan.")
                            break
                        elif response.status_code == 403:
                            st.error(f"❌ Akses diblokir Cloudflare pada Chapter {ch_num}. Coba aktifkan VPN atau deploy ulang aplikasi Anda.")
                            break
                        elif response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            
                            # --- PERBAIKAN STRUKTUR PENCARIAN GAMBAR BARU ---
                            # Mencari kontainer utama gambar dengan class Tailwind yang fleksibel
                            reader_area = soup.find('div', class_=lambda x: x and 'flex-col' in x and 'items-center' in x)
                            
                            # Jika kontainer utama fleksibel di atas tidak ketemu, cari alternatif div pembungkus per halaman gambar
                            if not reader_area:
                                img_containers = soup.find_all('div', class_=lambda x: x and 'relative' in x and 'justify-center' in x)
                                images = []
                                for container in img_containers:
                                    img_tag = container.find('img')
                                    if img_tag:
                                        images.append(img_tag)
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
                                            
                                        st.image(img_url, use_column_width=True)
                                        img_count += 1
                                
                            if img_count == 0:
                                st.caption(f"⚠️ Gambar gagal dimuat. Pola halaman web berubah atau dilindungi sistem hotlinking.")
                            # -----------------------------------------------
                    except Exception as e:
                        st.error(f"❌ Gangguan koneksi saat memuat Chapter {ch_num}: {e}")
                        break
    else:
        st.error("❌ Format URL salah! Pastikan Anda menyalin link halaman baca bab, bukan link profil komik. Format harus mengandung kata '-chapter-XX-'.")
