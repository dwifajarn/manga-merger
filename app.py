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

# Custom CSS untuk mempercantik UI (Warna latar belakang dan tampilan gambar)
st.markdown("""
    <style>
    .main { background-color: #0f111a; }
    h1 { color: #ff4b4b; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #ff3333; color: white; }
    img { margin-bottom: -5px !important; display: block; margin-left: auto; margin-right: auto; }
    </style>
    """, unsafe_allow_html=True)

# Header UI
st.title("📚 Manga & Manhwa Chapter Merger")
st.markdown("<p style='text-align: center; color: #888; '>Gabungkan banyak chapter menjadi 1 halaman vertikal panjang tanpa gangguan iklan.</p>", unsafe_allow_html=True)
st.divider()

# Input Link/URL
url_input = st.text_input(
    "🔗 Tempel URL Utama Komik di Sini:", 
    placeholder="Contoh: https://westmanga.id"
)

# Proses crawling data setelah user memasukkan URL
if url_input:
    # Set header agar tidak langsung diblokir sebagai bot biasa
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    with st.spinner("⏳ Sedang memindai daftar chapter dari website..."):
        try:
            response = requests.get(url_input, headers=headers, timeout=15)
            
            if response.status_code == 403:
                st.error("❌ Akses Ditolak (Error 403). Website target dilindungi oleh Cloudflare Anti-Bot. Silakan coba link dari situs komik lain.")
            elif response.status_code != 200:
                st.error(f"❌ Gagal memuat situs. Kode Error: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Mendeteksi link chapter (Mendukung tema Madara, Mangastream, dll)
                chapter_elements = soup.find_all('a', href=re.compile(r'/chapter-|/ch-'))
                if not chapter_elements:
                    chapter_elements = soup.find_all('li', class_='wp-manga-chapter')
                
                chapters = []
                for el in chapter_elements:
                    href = el.get('href') if el.name == 'a' else el.find('a').get('href')
                    text = el.text.strip()
                    if href and href not in [c['href'] for c in chapters]:
                        # Bersihkan teks chapter agar rapi di UI dropdown
                        clean_text = re.sub(r'\s+', ' ', text)
                        chapters.append({'text': clean_text, 'href': href})
                
                # Urutkan dari chapter terlama ke terbaru
                chapters.reverse()
                
                if chapters:
                    st.success(f"✅ Berhasil menemukan {len(chapters)} buah chapter!")
                    
                    # Form Pilihan Rentang Chapter (UI Kiri dan Kanan)
                    chapter_labels = [c['text'] for c in chapters]
                    
                    st.write("### 🎛️ Pilih Rentang Chapter")
                    col1, col2 = st.columns(2)
                    with col1:
                        start_ch = st.selectbox("Mulai Dari:", chapter_labels, index=0)
                    with col2:
                        end_ch = st.selectbox("Sampai Dengan:", chapter_labels, index=min(4, len(chapter_labels)-1))
                        
                    idx_start = chapter_labels.index(start_ch)
                    idx_end = chapter_labels.index(end_ch)
                    
                    if idx_start > idx_end:
                        st.warning("⚠️ Peringatan: Chapter 'Mulai' harus lebih kecil atau sama dengan Chapter 'Sampai'.")
                    else:
                        # Tombol Eksekusi Penggabungan
                        if st.button("🚀 GABUNGKAN & BACA SEKARANG", type="primary"):
                            selected_chapters = chapters[idx_start:idx_end+1]
                            
                            st.divider()
                            st.info(f"📖 Menampilkan rentang: {start_ch} hingga {end_ch}")
                            
                            # Proses mengambil gambar dari rentang chapter yang dipilih
                            for ch in selected_chapters:
                                st.markdown(f"<h3 style='text-align: center; color: #ff4b4b; background-color: #1e2235; padding: 10px; border-radius: 5px;'>📌 {ch['text']}</h3>", unsafe_allow_html=True)
                                
                                ch_res = requests.get(ch['href'], headers=headers, timeout=15)
                                ch_soup = BeautifulSoup(ch_res.text, 'html.parser')
                                
                                # Mencari area pembaca gambar utama
                                reader_area = ch_soup.find(id='readerarea') or ch_soup.find(class_='readerarea') or ch_soup.find(id='content')
                                
                                if reader_area:
                                    images = reader_area.find_all('img')
                                    valid_img_count = 0
                                    
                                    for img in images:
                                        # bypass lazy-loading atribut gambar website komik
                                        img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-srcset')
                                        if img_url:
                                            img_url = img_url.strip().split(' ')[0] # ambil URL murninya
                                            if not img_url.startswith('http'):
                                                img_url = "https:" + img_url if img_url.startswith('//') else url_input + img_url
                                            
                                            # Tampilkan gambar tanpa space jarak di UI webtoon mode
                                            st.image(img_url, use_column_width=True)
                                            valid_img_count += 1
                                            
                                    if valid_img_count == 0:
                                        st.caption("⚠️ Gambar gagal dimuat secara otomatis dari chapter ini.")
                                else:
                                    st.warning(f"❌ Gagal memetakan struktur gambar pada {ch['text']}.")
                else:
                    st.error("❌ Tidak dapat mendeteksi daftar chapter di link ini. Pastikan link mengarah ke halaman utama informasi manga.")
        except Exception as e:
            st.error(f"❌ Terjadi gangguan jaringan atau kegagalan sistem: {e}")
