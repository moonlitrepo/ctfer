# Transformer dari China 🤖

## deskripsi
penasaran apa ini sebenarnya...

''.join([chr((ord(flag[i]) << 8) + ord(flag[i + 1])) for i in range(0, len(flag), 2)])

author : aos

file : [enc](enc)

## analisis 
file enc tersebut merupakan file teks. berikut isinya
```
呈偃呆笱㙟扩瑳彩湳琳㑤彯晟㡟〴挰㜶つ紀
```
sekilas terlihat seperti bahasa cina, namun sebenanrnya ini hanya hasil obfuskasi yang dilakukan oleh kode python di deskripsi

```python
''.join([chr((ord(flag[i]) << 8) + ord(flag[i + 1])) for i in range(0, len(flag), 2)])
```

untuk mempermudah pembacaan kode, aku menulis ulang nya dan menggunakan debug flag yang memiliki format yang sama dengan flag asli.

```python
flag = 'THPCTF{debug_flag}'
encrypt = []
for i in range(0, len(flag), 2):
    x = chr((ord(flag[i]) << 8) + ord(flag[i+1]))
    encrypt.append(x)
print("".join(encrypt))
```
result:
```
呈偃呆筤敢畧彦污杽
```
jika di perhatikan secara teliti3 huruf cina pertama yang dihasilkan dari flag debug ini mirip dengan enc . 
```
呈偃呆 | 筤敢畧彦污杽
呈偃呆 | 笱㙟扩瑳彩湳琳㑤彯晟㡟〴挰㜶つ紀
```
ini membuktikan bahwa penulisan kode sudah tepat, sekarang adalah pembalikannya. 

## proses pembalikan algoritma
pertama coba balik operasi shiftleft menjadi shiftright
```python
decs = []
for i in enc:
    ch = ord(i)
    d = ch >> 8
    decs.append(chr(d))
print("".join(decs))
```
result:
```
TPT{6bt_nt4_f80c70}
```
setelah itu pembalikan bagian `+ ord(flag[i+1])`  , ini lebih sederhana. cukup mask dengan **0xff**
```decs = []
for i in enc:
    ch = ord(i)
    l = ch & 0xff
    decs.append(chr(l))
print("".join(decs))
```
result:
```
HCF1_isis3do__406d
```

sekarang tinggal menggabungkan mereka secara berurutan.
```python
decs = []
for i in enc:
    ch = ord(i)
    d = ch >> 8
    l = ch & 0xff
    decs.append(chr(d))
    decs.append(chr(l))
print("".join(decs))
```
result
```
THPCTF{16_bits_inst34d_of_8_04c0760d}
```

flag: `THPCTF{16_bits_inst34d_of_8_04c0760d}`
