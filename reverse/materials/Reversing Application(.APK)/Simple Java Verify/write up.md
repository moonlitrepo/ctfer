# Simple Java Verify

## deskripsi 
```
Description: &gt; A simple Android CrackMe written entirely in Java. The UI is created programmatically without using XML layouts.
​Goal: &gt; Find the correct 8-character license key to trigger the success message and reveal the flag.
​Input: &gt; String/Text in the input field.
​Solution: &gt; Decompile the APK using tools like JADX or Bytecode Viewer. Analyze the checkLicense() method to understand the string constraints (length, prefix, and suffix).
```

## analisis awal
File : [MyApp6_1.0](MyApp6_1.0)

untuk memverifikasi tipe data dilakukan pemeriksaan metadata.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day20-application)
└> file MyApp6_1.0.apk
MyApp6_1.0.apk: Android package (APK), with MANIFEST.MF and resources.arsc
```
sayangnya setelah di _unzip_ atau di bongkar dengan _apktool_ tidak ditemukan sesuatu yang menarik. karena itu analisis dilanjutkan menggunakan tools lain yaitu _jadx-gui_

pada jendela dekompiler saya menemukan suatu fungsi validasi:
```java
  public void checkLicense() {
        String string = this.inputField.getText().toString();
        if (string.length() != 8 || !string.startsWith("77") || !string.endsWith("1")) {
            Toast.makeText(this, "Invalid Key", 0).show();
        } else {
            Toast.makeText(this, "Access Granted", 1).show();
        }
    }
}
```
fungsi ini sederhana, ia hanya memeriksa 3 kondisi
1. panjang string harus 8
2. string diawali dengan 77
3. string di akhiri dengan 1

kesimpulan : string yang di terima minimal berbentuk : 77xxxxx1
