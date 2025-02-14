import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
import pandas as pd

# Veri seti adı
dataset_name = "mimic_perform_af_006_data.csv"

# Veri setini yükleme ve kontrol
try:
    rawsignals = pd.read_csv(dataset_name)
    if "PPG" not in rawsignals.columns:
        raise ValueError("The dataset does not contain a 'PPG' column.")
    if rawsignals["PPG"].isnull().sum() > 0:
        missing_count = rawsignals["PPG"].isnull().sum()
        print(f"Warning: {missing_count} missing values found in 'PPG' column. Filling with mean.")
        mean_value = rawsignals["PPG"].mean()
        rawsignals["PPG"].fillna(mean_value, inplace=True)
except Exception as e:
    print(f"Error loading dataset: {e}")
    sys.exit()

# PPG sinyalini numpy dizisine dönüştürme
ppg_signal = rawsignals["PPG"].to_numpy()

# Örnekleme frekansı
fs = 360
time = np.arange(ppg_signal.size) / fs

# Filtreleme İşlemleri
def butter_filter(signal, cutoff, fs, btype, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype=btype, analog=False)
    return filtfilt(b, a, signal)

# Düşük geçiren ve yüksek geçiren filtreler
low_pass_signal = butter_filter(ppg_signal, cutoff=3, fs=fs, btype='low')
high_pass_signal = butter_filter(low_pass_signal, cutoff=0.8, fs=fs, btype='high')

# Türev hesaplama
ppg_derivative = np.gradient(high_pass_signal, time)

# Sliding window parametreleri
winsize = fs * 5  # 5 saniyelik pencere
winhop = fs  # 1 saniyelik kaydırma
i = 0  # Başlangıç indeksi

# Türev hesaplama (Preprocessed sinyal artık türevlenmiş sinyal olacak)
ppg_derivative = np.gradient(high_pass_signal, time)  # Preprocessed türev sinyali

def on_press(event):
    global i
    sys.stdout.flush()

    lower = i
    upper = i + winsize

    # ax1 (Raw Signal)
    ax1.cla()
    ax1.plot(time, ppg_signal, 'g', label="Raw Signal")
    ax1.axvspan(time[lower], time[upper], color='red', alpha=0.4, label="Sliding Window")
    ax1.set_title(f'Raw Signal - Dataset: {dataset_name}')
    ax1.grid()
    ax1.legend()

    # ax2 (Preprocessed Signal + Peaks)
    ax2.cla()
    x_raw = ppg_signal[lower:upper]
    x_processed = ppg_derivative[lower:upper]  # Preprocessed artık türevlenmiş sinyal
    window_time = time[lower:upper]

    # Zirve noktalarını bulma
    peaks, properties = find_peaks(x_processed, prominence=0.3)

    ax2.plot(window_time, x_raw, 'b', label="Original")
    ax2.plot(window_time, x_processed, 'r', label="Preprocessed (Derivative)")
    ax2.scatter(window_time[peaks], x_processed[peaks], color='black', label="Peaks")
    ax2.set_xlim(window_time[0] - 1, window_time[-1] + 1)
    ax2.grid()
    ax2.legend(loc='lower left')
    ax2.set_title('Sliding Window: Original & Preprocessed (Derivative)')

    # Zirve noktalarına özellik isimlerini ve değerlerini yazdır
    text_offset = 0.1
    if len(peaks) > 1:
        systolic_peak = peaks[0]
        diastolic_peak = peaks[-1]
        systolic_time = window_time[systolic_peak]
        diastolic_time = window_time[diastolic_peak]

        # Sistolik ve diyastolik arasında kalan segmentte dicrotic notch hesaplama
        notch_segment = x_processed[systolic_peak:diastolic_peak]
        dicrotic_notch = np.min(notch_segment)
        dicrotic_notch_idx = np.argmin(notch_segment) + systolic_peak
        dicrotic_notch_time = window_time[dicrotic_notch_idx]

        pwa = x_processed[systolic_peak] - x_processed[diastolic_peak]

        # Sistolik Fazı Göster
        ax2.axvspan(systolic_time, dicrotic_notch_time, color='yellow', alpha=0.3, label="Systolic Phase")

        # Diyastolik Fazı Göster
        ax2.axvspan(dicrotic_notch_time, diastolic_time, color='cyan', alpha=0.3, label="Diastolic Phase")

        # Noktalar ile gösterim ve açıklamalar
        ax2.scatter(window_time[systolic_peak], x_processed[systolic_peak], color='blue', label="Systolic Peak")
        ax2.scatter(window_time[diastolic_peak], x_processed[diastolic_peak], color='red', label="Diastolic Peak")
        ax2.scatter(window_time[dicrotic_notch_idx], dicrotic_notch, color='purple', label="Dicrotic Notch")

        # Sinyal değerlerine göre çakışmadan kaçınarak etiketleme
        ax2.text(window_time[systolic_peak], x_processed[systolic_peak] + text_offset, f"PWSP: {x_processed[systolic_peak]:.2f}",
                 color="blue", fontsize=9, ha='center')
        ax2.text(window_time[diastolic_peak], x_processed[diastolic_peak] - text_offset, f"PWDP: {x_processed[diastolic_peak]:.2f}",
                 color="red", fontsize=9, ha='center')
        ax2.text(window_time[dicrotic_notch_idx], dicrotic_notch + text_offset, f"DN: {dicrotic_notch:.2f}",
                 color="purple", fontsize=9, ha='center')
    # Heart Rate Hesaplama
    feature_texts = []
    if len(peaks) > 1:
        peak_distances = np.diff(peaks) / fs
        heart_rate = 60 / np.mean(peak_distances)

        ppt = np.mean(peak_distances)  # PPT
        pwd =  diastolic_time - systolic_time  # Pulse Wave Duration

        # Özellik metinlerini oluştur
        feature_texts.append(f"PWSP: {x_processed[systolic_peak]:.2f}")
        feature_texts.append(f"PWDP: {x_processed[diastolic_peak]:.2f}")
        feature_texts.append(f"PWA: {pwa:.2f}")
        feature_texts.append(f"Dicrotic Notch: {dicrotic_notch:.2f}")
        feature_texts.append(f"PPT: {ppt:.2f}s")
        feature_texts.append(f"PWD: {pwd:.2f}s")
        feature_texts.append(f"Heart Rate: {heart_rate:.2f} BPM")
        feature_texts.append(f"Systolic Phase Time: {systolic_time:.2f}s (Yellow Area) ")
        feature_texts.append(f"Diastolic Phase Time: {diastolic_time:.2f}s (Blue Area)")

    # Özellik kutusunu yazdır
    plt.figtext(0.5, 0.02, "\n".join(feature_texts), fontsize=10, ha='center', color="black",
                bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

    # Klavye ile pencere kaydırma
    if event.key == 'right':
        i += winhop
        fig.canvas.draw()
    elif event.key == 'left':
        i -= winhop
        fig.canvas.draw()


# Grafik ayarları
fig = plt.figure(figsize=(12, 12))
ax1 = fig.add_subplot(211)
ax1.plot(time, ppg_signal, 'g')
ax1.grid()
ax1.set_title(f'Raw Signal - Dataset: {dataset_name}')

ax2 = fig.add_subplot(212)
ax2.grid()
plt.subplots_adjust(hspace=0.5, bottom=0.4)

fig.canvas.mpl_connect('key_press_event', on_press)
plt.show()