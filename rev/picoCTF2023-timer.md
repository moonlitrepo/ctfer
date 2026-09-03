# picoCTF2023-timer.md
# overview
<img width="509" height="408" alt="image" src="https://github.com/user-attachments/assets/eab95953-c160-478d-afe7-5b8e6d071c6f" />

di challenge pico ini aku diberi file apk yang harus dianalisis. namun flagnya bisa dengan mudah ditemukan dengan grep
# recon
pertama jelas lihat metadatanya dulu , hanya memastikan saja
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(timer-apk)
└> file timer.apk
timer.apk: Android package (APK), with zipflinger virtual entry, with APK Signing Block
```
sepertinya ini memang apk. kabar baiknya file apk itu strukturnya mirip seperti zip. jadi aku bisa mengekstraknya dengan unzip.

# exploit
langsung saja bongkar filenya dengan unzip, agar tidak berantakan hasilnya aku buat folder baru tempat menampung hasil ekstraknya dengan flag `-d nama_folder`
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(timer-apk)
└> unzip timer.apk -d extracted
Archive:  timer.apk
  inflating: extracted/META-INF/com/android/build/gradle/app-metadata.properties
  inflating: extracted/classes3.dex
  inflating: extracted/classes2.dex
  inflating: extracted/AndroidManifest.xml
......................
```
selalnjutnya adalah melakukan grep , akku menggunakan `grep -rwi picoctf .`, flag -rwi itu adalah r = rekursif alias mencari kedalam folder hingga habis. -w = whole word. mencocokkan
seluruh katanya. dan -i = ignore case. walaupun hasilnya uppercase selama karakternya cocook maka hasil akan keluar.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(timer-apk)
└> grep -rwi picoctf
grep: extracted/classes3.dex: binary file matches
```
ditemukan ada string picoctf di `extracted/classes3.dex`. aku akan melakukan strings grep lagi untuk memastikan

<img width="398" height="45" alt="image" src="https://github.com/user-attachments/assets/c996976b-bf38-48ec-be1f-0693a35b6149" />
done 
flag : `picoCTF{....................................}`

# conclusion
kesimpulan nya file apk biasanya memililkli struktur mirip file zip jadi jika flag tertulis secara hardcoded kita tidak perlu repot repot melakukan decompile , cukup unzip saja dan
semua isiannya keluar. maka dari itu cukup penting untuk memahami struktur dari suatu file agar dapat mengetahui bagaimana cara menindaklanjuti file dengan struktur tersebut.
