# IMPORT LIBRARY
import os #membantu dalam mengelola file, membaca folder, dan bekerja dengan pengaturan sistem.
import sys #membantu dalam mengelola jalur eksekusi Python dan mengontrol perilaku interpreter.
import subprocess #membantu dalam menjalankan perintah sistem operasi dari dalam skrip Python.

# FUNGSI PENGECEKAN MODUL
def check_and_install_requirements():
    """Fungsi untuk Mengecek dan menginstal modul dari requirements.txt secara otomatis."""
    req_file = "requirements.txt"
    # requirements.txt berisi modul yang di perlukan, yaitu yt-dlp dan ffmpeg
    
    # pengecekan: apakah file requirements.txt ada di folder yang sama
    if not os.path.exists(req_file):
        print(f"[!] File {req_file} tidak ditemukan. Program melewati pengecekan.")
        return

    print(f"[*] Mengecek modul dari {req_file}...")
    
    try:
        # Menggunakan importlib.metadata (built-in Python 3.8+) untuk mengecek modul terinstal
        from importlib.metadata import distributions, PackageNotFoundError
        
        with open(req_file, 'r') as f:
            # Membaca isi file, mengabaikan baris kosong atau baris komentar (#)
            dependencies = [line.strip().split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].split('>')[0].split('<')[0] for line in f if line.strip() and not line.startswith("#")]
        
        # Mengecek apakah semua dependencies di dalam list sudah terpenuhi
        installed_packages = {dist.metadata['Name'].lower(): dist for dist in distributions()}
        missing = [dep for dep in dependencies if dep.lower() not in installed_packages]
        
        if missing:
            raise PackageNotFoundError(f"Missing packages: {', '.join(missing)}")
        
        # jika sudah terinstall semua module
        print("[+] STATUS: Semua modul sudah terinstal dengan baik! Program dilanjutkan...\n")
        
    except (PackageNotFoundError, Exception) as e:
        # jika belum terinstall/versi semua modul salah 
        print(f"[-] Terdeteksi modul yang belum lengkap atau versi tidak sesuai: {str(e)}")
        print("[*] Memulai instalasi otomatis... Mohon tunggu sebentar.\n")
        
        try:
            """Menggunakan sys.executable untuk memanggil Python yang sedang berjalan
            Ini sangat aman dan kebal dari error "pip is not recognized" di Windows"""
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
            print("\n[+] OUTPUT: Instalasi otomatis berhasil! Semua modul sudah siap.\n")
            
        except subprocess.CalledProcessError:
            print("\n[GAGAL] Terjadi kesalahan fatal saat mencoba menginstal modul.")
            print("[!] Silakan coba jalankan perintah: python -m pip install -r requirements.txt secara manual.")
            sys.exit(1) # Mematikan program secara paksa agar tidak terjadi error lanjutan

# pengecekan modul pertama kali
check_and_install_requirements()

# FUNGSI TAMPILAN UI
def display_welcome():
    """Menampilkan pesan selamat datang dan judul aplikasi."""
    welcome_text = "    MUSIC DOWNLOADER    "
    
    print(welcome_text)
    print("\n   Download music from YouTube \n")

# FUNGSI DOWNLOAD UTAMA
# hasil download lagunya di simpan di directory music
def download_music_from_url(url, output_dir="music"):
    """Download audio dari URL YouTube dan konversi ke MP3."""
    from yt_dlp import YoutubeDL # library untuk download audio dari YouTube
    # Buat folder output jika belum ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Konfigurasi yt-dlp untuk download audio
    ydl_opts = {
        "format": "bestaudio/best",  # Pilih format audio terbaik
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),  # Template = judul.extention
        "postprocessors": [{
            "key": "FFmpegExtractAudio",  # Ekstrak audio menggunakan FFmpeg
            "preferredcodec": "mp3",  # Konversi ke MP3
            "preferredquality": "320",  # Kualitas 320kbps
        }],
        "quiet": True,  # Mode silent (tanpa output log)
        "no_warnings": True,  # Tanpa peringatan
        "progress_hooks": [progress_hook],  # Hook untuk progress
    }
    
    # Eksekusi download dengan progress bar
    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Tampilkan progress bar saat download
                task_progress = ("Downloading music...")
                
                # Download dan ekstrak info video
                info = ydl.extract_info(url, download=True)
                title = info.get('title', 'music')
                
                # Sanitasi nama file (hapus karakter yang tidak valid)
                # Hanya biarkan: huruf, angka, spasi, -, dan _
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()

                # menampilkan status ketika selesai mendownload
                print("Download completed!")
                
            # Return judul dan path file yang didownload
                return safe_title, os.path.join(output_dir, f"{safe_title}.mp3")

        except Exception as e:
            print(f"Error: {str(e)}")
            return None, None

# FUNGSI PROGRESS HOOK
def progress_hook(d):
    """Callback untuk memantau progress download (opsional untuk UI)."""
    if d['status'] == 'downloading':
        # Bisa tambahkan logika untuk update progress bar real-time di sini
        pass
    elif d['status'] == 'finished':
        # Bisa tambahkan logika saat download selesai
        pass

# FUNGSI PENCARIAN
def search_and_download(query):
    """Cari lagu di YouTube berdasarkan query dan download hasil pertama."""
    from yt_dlp import YoutubeDL # library untuk download audio dari YouTube
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
    }
    
    print(f"Searching for: {query}")
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Cari di YouTube (hanya info, tidak download)
            search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
            
            # Cek apakah ada hasil pencarian
            if search_results and 'entries' in search_results:
                entries = search_results['entries']
                if entries:
                    # Ambil hasil pertama
                    first_result = entries[0]
                    url = first_result['webpage_url']
                    title = first_result.get('title', 'Unknown')
                    
                    # Tampilkan hasil pencarian
                    print(f"Found: {title}")
                    print(f"URL: {url}")
                    
                    # Minta konfirmasi user sebelum download
                    def confirm():
                        return input("Download this track? (y/n): ").lower() == 'y'
                    
                    # Download jika user setuju
                    if confirm():
                        return download_music_from_url(url)
                    else:
                        return None, None
            else:
                print("No results found")
                return None, None
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return None, None

# main function
def main():
    """Fungsi utama: menampilkan menu dan menangani input user."""
    # Tampilkan layar pembuka
    display_welcome()
    
    # Loop utama - program terus berjalan sampai exit
    while True:
        # Tampilkan menu opsi
        print("Choose an option:")
        print("  1. Enter YouTube URL")
        print("  2. Search by song title")
        print("  3. Exit")
        
        # Minta input user dengan validasi otomatis (hanya 1,2,3)
        choice = int(input("\nEnter your choice: "))
        
        # Handle setiap pilihan
        if choice == 3:
            # Exit program
            print("Goodbye!")
            sys.exit(0)
        
        elif choice == 1:
            # Download dari URL
            url = input("Enter YouTube URL: ")
            if url:
                title, filepath = download_music_from_url(url)
                if title and filepath:
                    print(f"Downloaded: {title}")
                    print(f"Saved to: {filepath}")
        
        elif choice == 2:
            # Cari dan download
            query = input("Enter song title or artist: ")
            if query:
                title, filepath = search_and_download(query)
                if title and filepath:
                    print(f"Downloaded: {title}")
                    print(f"Saved to: {filepath}")
        
        # Separator antar iterasi
        print("\n" + "="*50 + "\n")

"""ENTRY POINT
if __name__ == '__main__': memastikan kode hanya berjalan saat 
file dijalankan langsung, bukan saat di-import
"""
if __name__ == '__main__':
    main()