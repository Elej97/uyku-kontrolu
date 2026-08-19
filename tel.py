"""
💤 Göz Kapakları Kapanınca Uyku Modu ve Geri Sayım Sistemi
MediaPipe Face Mesh ile gerçek zamanlı yüz ve göz takibi
Gözler kapandığında geri sayım başlar, 3 saniye kapalı kalırsa YouTube linki açılır
Sol üstte yeşil çember + kırmızı geri sayım göstergesi ve EAR kalibrasyon değerleri
"""

import cv2
import webbrowser
import time
import math
from mediapipe.python.solutions import face_mesh as mp_face_mesh

# ─────────────────────────────────────────
# AYARLAR
# ─────────────────────────────────────────
YOUTUBE_URL         = "https://www.youtube.com/shorts/_EiWd-7-hLM"
COOLDOWN_SECONDS    = 15      # Video açıldıktan sonra tekrar açılmaması için bekleme
CAMERA_INDEX        = 0
FRAME_WIDTH         = 1280
FRAME_HEIGHT        = 720

COUNTDOWN_TARGET    = 3       # Kaç saniye gözler kapalı kalırsa video açılır

# Göz Açıklık Oranı (EAR - Eye Aspect Ratio) Eşiği
# Bu değerin altındaki EAR oranları gözün kapalı olduğunu gösterir.
# Ekrandaki EAR değerlerini izleyerek kendinize göre ayarlayabilirsiniz.
EAR_THRESHOLD       = 0.21

# ─── Çember ayarları ───
CX, CY  = 80, 90              # Çember merkezi (sol üst)
RADIUS  = 55                  # Çember yarıçapı

# ─── MediaPipe Göz Landmark İndeksleri ───
# Sağ Göz: Üst, Alt, Sol Köşe, Sağ Köşe
RIGHT_EYE_INDICES   = [159, 145, 33, 133]
# Sol Göz: Üst, Alt, Sol Köşe, Sağ Köşe
LEFT_EYE_INDICES    = [386, 374, 362, 263]


# ─────────────────────────────────────────
# MATEMATİKSEL FONKSİYONLAR
# ─────────────────────────────────────────

def get_distance(p1, p2, width, height):
    """İki nokta arasındaki Euclidean (Öklid) mesafeyi piksel cinsinden hesaplar."""
    return math.sqrt(((p1.x - p2.x) * width) ** 2 + ((p1.y - p2.y) * height) ** 2)


def calculate_ear(eye_indices, landmarks, width, height):
    """Göz Açıklık Oranını (Eye Aspect Ratio - EAR) hesaplar."""
    top = landmarks[eye_indices[0]]
    bottom = landmarks[eye_indices[1]]
    left = landmarks[eye_indices[2]]
    right = landmarks[eye_indices[3]]

    vertical_dist = get_distance(top, bottom, width, height)
    horizontal_dist = get_distance(left, right, width, height)

    if horizontal_dist == 0:
        return 0.0
    return vertical_dist / horizontal_dist


# ─────────────────────────────────────────
# ÇEMBER GERİ SAYIM ÇİZİCİ
# ─────────────────────────────────────────

def draw_countdown_circle(frame, elapsed: float, target: int, eyes_closed: bool):
    """
    Sol üstte yuvarlak geri sayım göstergesi çizer.
      - Dış çember dolum yayı : yeşil
      - İçindeki sayı         : kırmızı
      - Gözler açık/yoksa     : gri nokta bekleme ikonu
    """
    # ── Yarı saydam arka plan diski ──────────────────
    overlay = frame.copy()
    cv2.circle(overlay, (CX, CY), RADIUS + 10, (20, 20, 20), -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    # ── Arka plan halkası (koyu gri) ─────────────────
    cv2.circle(frame, (CX, CY), RADIUS, (60, 60, 60), 10, cv2.LINE_AA)

    if eyes_closed and elapsed > 0:
        # Dolum oranı → saat yönünde yay
        ratio   = min(elapsed / target, 1.0)
        sweep   = int(ratio * 360)

        # Yeşil dolum yayı (12 konumundan başlar = -90°)
        cv2.ellipse(
            frame,
            (CX, CY),
            (RADIUS, RADIUS),
            0,
            -90,
            -90 + sweep,
            (0, 230, 50),   # yeşil
            10,
            cv2.LINE_AA
        )

        # İçindeki sayı
        display_num = min(int(elapsed) + 1, target)
        num_text    = str(display_num)

        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.4
        thickness  = 3
        (tw, th), _ = cv2.getTextSize(num_text, font, font_scale, thickness)
        tx = CX - tw // 2
        ty = CY + th // 2

        # Gölge (okunabilirlik)
        cv2.putText(frame, num_text, (tx + 2, ty + 2), font, font_scale,
                    (0, 0, 0), thickness + 2, cv2.LINE_AA)
        # Kırmızı sayı
        cv2.putText(frame, num_text, (tx, ty), font, font_scale,
                    (0, 0, 220), thickness, cv2.LINE_AA)

    else:
        # Bekleme → üç gri nokta
        for dx in (-16, 0, 16):
            cv2.circle(frame, (CX + dx, CY), 5, (130, 130, 130), -1, cv2.LINE_AA)


# ─────────────────────────────────────────
# GÖZ VE YÜZ LANDMARK ÇİZİCİ
# ─────────────────────────────────────────

def draw_eye_landmarks(frame, landmarks, width, height):
    """Göz kenarlarındaki kritik noktaları ekranda görselleştirir."""
    for idx in RIGHT_EYE_INDICES + LEFT_EYE_INDICES:
        pt = landmarks[idx]
        px = int(pt.x * width)
        py = int(pt.y * height)
        cv2.circle(frame, (px, py), 2, (0, 255, 255), -1, cv2.LINE_AA)


# ─────────────────────────────────────────
# ALT BİLGİ ÇUBUĞU VE EAR BİLGİLERİ
# ─────────────────────────────────────────

def draw_status_bar(frame, eyes_closed, elapsed, target, cooldown_left, ear_r, ear_l):
    h, w = frame.shape[:2]
    
    # Alt bilgi çubuğu arka planı
    cv2.rectangle(frame, (0, h - 50), (w, h), (18, 18, 18), -1)

    # Güncel EAR Değerleri (Kullanıcı kalibrasyonu için sol altta)
    ear_msg = f"EAR Sol: {ear_l:.3f} | EAR Sag: {ear_r:.3f} | Esik Degeri: {EAR_THRESHOLD}"
    cv2.putText(frame, ear_msg, (12, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

    if cooldown_left > 0:
        msg   = f"Bekleniyor - tekrar {cooldown_left}s sonra aktif  |  Cikis: Q"
        color = (60, 160, 255)
    elif eyes_closed:
        remaining_s = max(0, target - int(elapsed))
        msg   = f"Gozler Kapali! {remaining_s}s sonra uyku moduna geciliyor...  |  Cikis: Q"
        color = (0, 220, 80)
    else:
        msg   = "Gozler acik (Uyku Bekleniyor)...  |  Cikis: Q"
        color = (150, 150, 150)

    cv2.putText(frame, msg, (12, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1, cv2.LINE_AA)


# ─────────────────────────────────────────
# ANA DÖNGÜ
# ─────────────────────────────────────────

def main():
    print("=" * 57)
    print("  UYKU  Goz Kapaklari Uyku Kontrol Sistemi | MediaPipe")
    print("=" * 57)
    print(f"  Geri sayim    : {COUNTDOWN_TARGET} saniye")
    print(f"  Cooldown      : {COOLDOWN_SECONDS} saniye")
    print(f"  EAR Esigi     : {EAR_THRESHOLD}")
    print(f"  YouTube URL   : {YOUTUBE_URL}")
    print("=" * 57)

    print("\n[*] MediaPipe Face Mesh yukleniyor...")
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    print("[OK] Moduller hazir.\n")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[HATA] Kamera ({CAMERA_INDEX}) acilamadi!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    eyes_closed_since = None   # Gözlerin ilk kapandığı zaman
    last_triggered   = 0.0     # Son YouTube açılma zamanı
    total_opened     = 0

    print("[*] Kamera aktif. Cikmak icin 'Q' basin.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        # Ayna yansımasını düzeltme
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # BGR'dan RGB'ye dönüştürme (MediaPipe RGB görsel kabul eder)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        eyes_closed = False
        ear_r, ear_l = 0.0, 0.0

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = face_landmarks.landmark

                # Sağ ve Sol gözler için EAR hesaplama
                ear_r = calculate_ear(RIGHT_EYE_INDICES, landmarks, w, h)
                ear_l = calculate_ear(LEFT_EYE_INDICES, landmarks, w, h)

                # Her iki gözün EAR değeri de eşik değerinin altındaysa gözler kapalı kabul edilir
                if ear_r < EAR_THRESHOLD and ear_l < EAR_THRESHOLD:
                    eyes_closed = True

                # Göz noktalarını ekranda çiz
                draw_eye_landmarks(frame, landmarks, w, h)

        now = time.time()
        cooldown_left = max(0, int(COOLDOWN_SECONDS - (now - last_triggered)))

        # ── Geri sayım mantığı ──────────────────────────
        if eyes_closed:
            if eyes_closed_since is None:
                eyes_closed_since = now      # İlk kapanma → saymaya başla
            elapsed = now - eyes_closed_since
        else:
            eyes_closed_since = None         # Gözler açıldı → sıfırla
            elapsed = 0.0

        # Belirlenen saniye doldu + cooldown bitti → YouTube aç!
        if eyes_closed and elapsed >= COUNTDOWN_TARGET and cooldown_left == 0:
            total_opened    += 1
            last_triggered   = now
            eyes_closed_since = None
            elapsed          = 0.0
            print(f"[OK] Gozler Kapandi! Video acildi! (#{total_opened})  YouTube: {YOUTUBE_URL}")
            webbrowser.open(YOUTUBE_URL)

        # ── Çizim ──────────────────────────────────────
        draw_countdown_circle(frame, elapsed, COUNTDOWN_TARGET, eyes_closed)
        draw_status_bar(frame, eyes_closed, elapsed, COUNTDOWN_TARGET, cooldown_left, ear_r, ear_l)

        cv2.imshow("Goz Kapaklari Uyku Modu Kontrolu", frame)

        key = cv2.waitKey(1) & 0xFF
        # Q, ESC tuşlarına basıldıysa veya pencerenin sağ üstündeki (X) kapatma butonuna tıklandıysa çık
        if key in (ord("q"), ord("Q"), 27) or cv2.getWindowProperty("Goz Kapaklari Uyku Modu Kontrolu", cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[*] Program sonlandi. Toplam video acilma: {total_opened}")


if __name__ == "__main__":
    main()