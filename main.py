from exceptions import (
    MonitoringError,
    InvalidDataError,
    InvalidUrlError,
    ServiceTimeoutError,
    ServerDownError,
)
from models import Server, WebsiteService, ApiService, MonitoringSystem


def jalankan_skenario(judul: str, aksi):
    print(f"\n=== {judul} ===")
    try:
        hasil = aksi()
    except InvalidUrlError as e:
        print(f"[GAGAL - URL TIDAK VALID] {e}")
    except InvalidDataError as e:
        print(f"[GAGAL - DATA TIDAK VALID] {e}")
    except ServiceTimeoutError as e:
        print(f"[PERINGATAN - TIMEOUT] {e}")
    except ServerDownError as e:
        print(f"[KRITIS - SERVER MATI] {e}")
    except MonitoringError as e:
        print(f"[ERROR MONITORING UMUM] {e}")
    else:
        print(f"[SUKSES] Proses berjalan normal. Hasil: {hasil}")
    finally:
        print("[SELESAI] Blok pemeriksaan skenario ditutup.")


if __name__ == "__main__":
    server_utama = Server("Server-01", True)
    web_bsb = WebsiteService.default_website(
        "Website BSB", "https://balisolutionbuilding.com"
    )
    api_bsb = ApiService("API BSB", "https://api.balisolutionbuilding.com/v1", 1.2)
    system = MonitoringSystem(server_utama)

    jalankan_skenario(
        "1. Monitoring Normal Website & API",
        lambda: (system.monitor([web_bsb, api_bsb]), "Semua layanan sehat")[1],
    )

    jalankan_skenario(
        "2. Validasi Setter Waktu Respons Negatif",
        lambda: setattr(web_bsb, "response_time", -1.5),
    )

    jalankan_skenario(
        "3. Pembuatan Layanan dengan URL Tidak Valid",
        lambda: WebsiteService("Web Ilegal", "ftp://balisolutionbuilding.com", 0.4),
    )

    api_lambat = ApiService("API Payment BSB", "https://api.balisolutionbuilding.com/pay", 4.5)
    jalankan_skenario(
        "4. Deteksi Service Timeout pada API",
        lambda: system.monitor([api_lambat]),
    )

    server_cadangan = Server("Server-Backup", False)
    system_cadangan = MonitoringSystem(server_cadangan)
    jalankan_skenario(
        "5. Monitoring Saat Server Mati",
        lambda: system_cadangan.monitor([web_bsb]),
    )

    print("\n=== DAFTAR ALERT TERCATAT ===")
    for alert in system.alerts + system_cadangan.alerts:
        print("-", alert)
