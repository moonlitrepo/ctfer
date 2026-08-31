# picoCTF2026-hiddencipher1


hello yall welcome to my write up again

catatan ini adalah cara ku mengerjakan chall hidden cipher 1 . termasuk chall baru karena rilis tahun ini. 2026. chall hiddencipher1 ini menyajikan file program elf 86-64 dengan 
flag kw nya. curiga pasti disuruh bikin keygen ini wkwkkwww. dan benar saja saat program dijalankan kita langsung diberikan hasil enkripsi dari file flag.txt tersebut. 
jelas tugas kita adalah mereverse nya dan membuat skrip untuk mendekripsi enkripsi tersebut.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher1)
└> ./hiddencipher
Here your encrypted flag:
235a201d70201548251358110c552f135409
```
namun ada sedikit masalah disini. ternyata file program ini memiliki semacam 'anti decompile' membuat kita tidak bisa mendecompile atau melihat isi program tersebut, bahkan gdb
dan ghidra ga ngatasin.

percobaan melihat fungsi di gdb :
```
pwndbg> info functions
All defined functions:
pwndbg>
```

jadi apa yang terjadi disini? kenapa kita gabisa membongkar programnya? 

# upx
UPX (Ultimate Packer for eXecutables) ,alias ini adalah packer yang mengompress ukuran program executable menjadi ukuran yang lebih kecil dan menyembunyikan kode asli
dari program yang di pack. sehingga fungsi yang ada ilang semua. namun cara mengatasinya cukup mudah. kita perlu install dulu tools upx nya 


```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher1)
└> sudo apt install upx -y
```
lalu tinggal unpack aja agar file programnya kembali ke bentuk awalnya

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher1)
└> upx -d -o hidden hiddencipher
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2024
UPX 4.2.2       Markus Oberhumer, Laszlo Molnar & John Reiser    Jan 3rd 2024

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
     24275 <-      7196   29.64%   linux/amd64   hidden

Unpacked 1 file.
```
nah dengan gini kita berhasil membongkar file program hiddencipher dan outputnya file hidden. mari coba gdb file outputnya

```
heap-config shows heap related configuration
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x0000000000001000  _init
0x00000000000010f0  __cxa_finalize@plt
0x0000000000001100  free@plt
0x0000000000001110  putchar@plt
0x0000000000001120  puts@plt
0x0000000000001130  fread@plt
0x0000000000001140  fclose@plt
0x0000000000001150  printf@plt
0x0000000000001160  rewind@plt
0x0000000000001170  ftell@plt
0x0000000000001180  malloc@plt
0x0000000000001190  fseek@plt
0x00000000000011a0  fopen@plt
0x00000000000011b0  perror@plt
0x00000000000011c0  _start
0x00000000000011f0  deregister_tm_clones
0x0000000000001220  register_tm_clones
0x0000000000001260  __do_global_dtors_aux
0x00000000000012a0  frame_dummy
0x00000000000012a9  get_secret
0x00000000000012eb  main
0x000000000000148c  _fini
```

well well well, semua fungsi sudah terlihat. saatnya pake ghidra untuk mulai mengamati apa yang bekerja dibalik layar
aku sudah menganalisis dan merename beberapa variabelnya .ini adalah beberapa kode yang bisa dibilang adalah inti program 

```
      key = get_secret();
      puts("Here your encrypted flag:");
      for (i = 0; (long)i < (long)flag_size; i = i + 1) {
      printf("%02x",(ulong)(*(byte *)(key + i % 6) ^ *(byte *)((long)flag_loc + (long)i)))
```

key :
```

undefined7 * get_secret(void)

{
  s.0._0_1_ = 83;
  s.0._1_1_ = 51;
  s.0._2_1_ = 67;
  s.0._3_1_ = 114;
  s.0._4_1_ = 51;
  s.0._5_1_ = 116;
  s.0._6_1_ = 0;
  return &s.0;
}

```
oke jadi apa aja yang bisa kita ambil dari hasil decompile ghidra ini? apa si maksud programnya? nah jadi program ini akan membuka file flag.txt yang disimpan di sebuah lokasi 
di program , anggap saja variabel flag. setelah itu program mengambil key dari fungsi get_secret() untuk mengenkripsi flag tersebut. itu adalah penjelasan singkatnya. berikut analisis
detail menurut ku :

# data enkripsi
pertama kita coba ambil dulu kunci nya , dari decompiler , get_secret menyimpan angka 83,51,67,114,51,116,0 . kalau diubah jadi ascii jadinya : **S3Cr3t** lalu enc flag dari
nc adalah **235a201d702015483b1d412b265d3313501f0c072d135f0d2002302d0a406a0a701756102e** . 

# proses enkripsi
apa si yang dilakukan program? 
```
for (i = 0; (long)i < (long)flag_size; i = i + 1) {
      printf("%02x",(ulong)(*(byte *)(key + i % 6) ^ *(byte *)((long)flag_loc + (long)i)))
```
baris 1 adalah perulangan for i dengan i yang terus bertambah hingga bernilai dengan ukuran flag , jika dalam python : **for i in range(len(flag)):**  
nah baris e 2 adalah inti enkripsi nya. tiap byte dalam flag akan di xor dengan byte key.  

jika fokus membelah kodenya:
print("%02x, <-- ini untuk mengeluarkan enkripsi dalam bentuk hex  
(ulong)(*(byte *)(key + i % 6)  <-- key beruukuran 6 karakter, jadi dengan i mod6 ketika perulangan xor mencapai string terakhir key , key akan mengulang dari string awal.
^ *(byte *)((long)flag_loc + (long)i))) <-- key tadi akan di xor dengan tiap byte dari flag

aku coba kasi contoh

flag = flag{fake}  
key = omaga  
maka xor nya akan gini :  
```
f ^ o = 102 ^ 111 = 9 (\t)
l ^ m = 108 ^ 109 = 1 (\x01)
a ^ a = 97 ^ 97 = 0 (\x00)
g ^ g = 103 ^ 103 = 0 (\x00)
{ ^ a = 123 ^ 97 = 26 (\x1a)
f ^ o = 102 ^ 111 = 9 (\t)
a ^ m = 97 ^ 109 = 12 (\x0c)
k ^ a = 107 ^ 97 = 10 (\n)
e ^ g = 101 ^ 103 = 2 (\x02)
} ^ a = 125 ^ 97 = 28 (\x1c)
```
kurang lebih itu yang terjadi dengan flag dan key di chall ini. 

karena data yang kita miliki sudah cukup maka tinggal membuat skrip python sederhana yang akan melakukan xor lagi untuk mengembalikan enkripsinya :

```
# flag = "235a201d70201548251358110c552f135409" fake flag local 
flag = "235a201d702015483b1d412b265d3313501f0c072d135f0d2002302d0a406a0a701756102e" #dari nc
byte = bytes.fromhex(flag)
key = "S3Cr3t"
extract = 0
hasil_xor = bytes([b ^ ord(key[i%6]) for i,b in enumerate(byte)])
print(hasil_xor)

```
tinggal di run
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher1)
└> python3 inverse.py
b'picoCTF{xor_unpack_4nalys1s_94993eed}'
```

done nih  
flag : **picoCTF{xor_unpack_4nalys1s_94993eed}**
