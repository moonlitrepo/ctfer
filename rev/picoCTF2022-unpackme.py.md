# picoCTF2022-unpackme.py

# overview 
<img width="445" height="300" alt="image" src="https://github.com/user-attachments/assets/e9afaad2-ba3a-4442-bed5-e4f475554a31" />

challenge reverse engineering sederhana yang menggunakan enkripsi fermet dari libc python : cryptography.fernet namun kode ini sudah melakukan deskripsinya untuk kita. hanya saja
butuh password untuk mengaksesnya.

# analysis and exploit
source code yang diberikan :

```Python
import base64
from cryptography.fernet import Fernet

payload = b'gAAAAABkzWGO_8MlYpNM0n0o718LL-w9m3rzXvCMRFghMRl6CSZwRD5DJOvN_jc8TFHmHmfiI8HWSu49MyoYKvb5mOGm_Jn4kkhC5fuRiGgmwEpxjh0z72dpi6TaPO2TorksAd2bNLemfTaYPf9qiTn_z9mvCQYV9cFKK9m1SqCSr4qDwHXgkQpm7IJAmtEJqyVUfteFLszyxv5-KXJin5BWf9aDPIskp4AztjsBH1_q9e5FIwIq48H7AaHmR8bdvjcW_ZrvhAIOInm1oM-8DjamKvhh7u3-lA=='
key_str = 'correctstaplecorrectstaplecorrec'
key_base64 = base64.b64encode(key_str.encode())
f = Fernet(key_base64)
plain = f.decrypt(payload)
exec(plain.decode())

```

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(unpackallfromme)
└> python3 unpackme.flag.py
What's the password? idk bruh
That password is incorrect.
```
di bagian source code ternyata program python itu sudah melakukan decrypt dan itu tersimpan di variabel plain. cara bypassnya sederhana. cukup lakukan print plain saja.  

tambahkan : `print(plain.decode())` tepat di paling bawah program. lalu jalankan lagi.
<img width="437" height="236" alt="image" src="https://github.com/user-attachments/assets/bfacb0ff-4e63-4f96-847a-f7c0d9e6edc6" />

weldone. disini aku mendapatkan flag dan passwordnya. well value passwordnya jadi ngga berharga karena sudah ada flagnya ya wkkwkkwkwk
