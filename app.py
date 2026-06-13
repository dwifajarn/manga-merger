import streamlit as st
import re

# Konfigurasi Tampilan Halaman Utama UI
st.set_page_config(
    page_title="Manga & Manhwa Chapter Merger",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0f111a; }
    h1 { color: #ff4b4b; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.title("📚 WestManga Local Browser Merger")
st.markdown("<p style='text-align: center; color: #888;'>Sistem Menggunakan Sesi Browser Anda Sendiri (100% Bebas Blokir Cloudflare).</p>", unsafe_allow_html=True)
st.divider()

# Input Link/URL dari halaman baca komik
url_input = st.st.text_input(
    "🔗 Tempel URL Baca Chapter di Sini:", 
    placeholder="Contoh: https://westmanga.cc"
)

if url_input:
    # Membedah struktur penomoran URL komik
    match = re.search(r'(.*-chapter-)(\d+)(.*)', url_input)
    
    if match:
        base_url_left = match.group(1)   
        current_ch_str = match.group(2) 
        base_url_right = match.group(3)  
        
        current_ch_num = int(current_ch_str)
        padding_length = len(current_ch_str) 
        
        st.success(f"✅ Komik Terdeteksi! Silakan tentukan rentang chapter di bawah.")
        
        col1, col2 = st.columns(2)
        with col1:
            start_ch = st.number_input("Mulai Dari Chapter:", min_value=1, value=current_ch_num, step=1)
        with col2:
            end_ch = st.number_input("Sampai Dengan Chapter:", min_value=1, value=current_ch_num + 2, step=1)
            
        if start_ch > end_ch:
            st.warning("⚠️ Peringatan: Chapter 'Mulai' tidak boleh lebih besar dari Chapter 'Sampai'.")
        else:
            # Membuat daftar URL target yang akan digabung
            urls_to_load = []
            for ch_num in range(int(start_ch), int(end_ch) + 1):
                ch_str_formatted = str(ch_num).zfill(padding_length)
                urls_to_load.append({
                    "num": ch_num,
                    "url": f"{base_url_left}{ch_str_formatted}{base_url_right}"
                })
            
            # --- INJEKSI JAVASCRIPT SANDBOX ---
            # Menggunakan Iframe dan JavaScript Fetch agar browser pengguna yang menembus Cloudflare
            html_js_injector = f"""
            <div id="status-log" style="color: #888; font-family: sans-serif; text-align: center; margin-bottom: 15px;">
                ⏳ Memulai proses penggabungan langsung via browser Anda...
            </div>
            <div id="manga-container" style="background-color: #0f111a; width: 100%; display: flex; flex-direction: column; align-items: center;"></div>
            
            <script>
            const chapters = {urls_to_load};
            const container = document.getElementById('manga-container');
            const log = document.getElementById('status-log');
            
            async function loadManga() {{
                log.innerText = "⏳ Sedang memproses "+chapters.length+" chapter. Mohon tunggu...";
                
                for (let ch of chapters) {{
                    // Membuat judul pembatas per chapter
                    let header = document.createElement('h3');
                    header.innerText = "📌 CHAPTER " + ch.num;
                    header.style.color = "#ff4b4b";
                    header.style.backgroundColor = "#1e2235";
                    header.style.padding = "10px";
                    header.style.borderRadius = "5px";
                    header.style.textAlign = "center";
                    header.style.width = "90%";
                    header.style.fontFamily = "sans-serif";
                    header.style.marginTop = "20px";
                    container.appendChild(header);
                    
                    try {{
                        // Memanggil halaman lewat proksi CORS AllOrigins agar browser diizinkan membaca HTML situs lain
                        let response = await fetch(`https://allorigins.win{{encodeURIComponent(ch.url)}}`);
                        if (!response.ok) throw new Error("Gagal memuat");
                        
                        let data = await response.json();
                        let parser = new DOMParser();
                        let doc = parser.parseFromString(data.contents, 'text/html');
                        
                        // Mencari semua gambar di dokumen hasil fetch
                        let images = doc.querySelectorAll('img');
                        let count = 0;
                        
                        images.forEach(img => {{
                            let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
                            if (src && src.includes('westmanga')) {{
                                if (src.startsWith('//')) src = "https:" + src;
                                
                                let newImg = document.createElement('img');
                                newImg.src = src;
                                newImg.style.width = "100%";
                                newImg.style.display = "block";
                                newImg.style.marginBottom = "-5px"; // Menghilangkan jarak antar gambar (Webtoon mode)
                                container.appendChild(newImg);
                                count++;
                            }}
                        }});
                        
                        if(count === 0) {{
                            let warning = document.createElement('p');
                            warning.innerText = "⚠️ Gagal mengekstrak gambar untuk chapter ini (Halaman terproteksi).";
                            warning.style.color = "yellow";
                            warning.style.fontFamily = "sans-serif";
                            container.appendChild(warning);
                        }}
                        
                    }} catch (err) {{
                        let errorLog = document.createElement('p');
                        errorLog.innerText = `❌ Gagal memuat Chapter ${{ch.num}}: Jaringan sibuk.`;
                        errorLog.style.color = "red";
                        errorLog.style.fontFamily = "sans-serif";
                        container.appendChild(errorLog);
                    }}
                }}
                log.innerText = "✅ Selesai menggabungkan! Selamat membaca.";
            }}
            
            // Jalankan fungsi otomatis saat elemen selesai dimuat
            loadManga();
            </script>
            """
            
            # Merelasikan kode HTML/JS ke dalam UI Streamlit dengan tinggi fleksibel
            st.components.v1.html(html_js_injector, height=2000, scrolling=True)
            
    else:
        st.error("❌ Format URL salah. Pastikan menyalin tautan halaman baca bab aktif.")
