# GO GO GO Write Up

## deskripsi

My first crackme.Let me know if I need to change the difficulty. I don't really know what I'm doing.

Author: s0k1t  
Language: Go  
Upload: 2021-03-06 22:54  
Platform: Unix/linux etc.  
Difficulty: 2.0  
Quality: 4.0  
Arch:x86-64  

flag : None

## Ringkasan
Challenge ini berupa file biner ELF x86-64 (statically linked,stripped). Langkah penyelesaian yang digunakan adalah membedah file biner dengan teknik _static analysis_ menggunakan _strings_ dan _ghidra_. Flag berhasil di ambil dengan membalik algoritma hex encode pada proses manipulasi string yang dilakukan file biner tersebut.

## analisis awal
pemeriksaan metadata dan mencoba menjalankan file biner untuk mencari informasi perilaku _runtime_ file biner.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall4)
└> file main
main: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, BuildID[unknown]=3768317334696e377433485034353577337244, stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall4)
└> ./main
Password Plox:
admin1234
try again loser
```

Observasi
- Karakteristik: file biner _executable x86-64, statically linked, stripped_
- Bahasa yang digunakan: belum diketahui _BuildID[unknown]=_
- Perilaku file biner: program ini meminta input setelah mencetak teks _Password Plox_ . dan program menolak input yang dimasukkan lalu memberi arahan kepada user
  untuk mencoba lagi. ini mengindikasikan adanya suatu perbandingan input yang memiliki syarat tertentu untuk memicu kondisi selain mencetak _try again loser_.
  kesimpulannya kita perlu mencari tahu apa password nya.

upaya lain dilakukan dengan melakukan strings pada file biner untuk mencari strings yang mungkin berguna.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall4)
└> strings main
[terdeteksi banyak strings runtime.]
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall4)
└> strings main | grep main.main
main.main
```

runtime.xxxx merupakan karakteristik dari file biner yang di kompilasi dari bahasa Golang. Mekanisme runtime Golang membuat kondisi _stripped_ menjadi tidak
berarti karena semua nama fungsi masih tersedia. umumnya tersimpan di _gopclntab_ . pada kasus ini fungsi utama (_main.main_) masih terdeteksi.

## analisis lanjutan dan eksploitasi
proses analisis dilanjutkan menggunakan Tools dekompilasi _Ghidra_ untuk mendekompilasi fungsi utama _main.main_ .

mengingat pada metadata tertulis _statically linked_ maka semua fungsi runtime. golang akan ikut terdekompilasi sehingga mengganggu pembacaan / proses analisis
program. saya menerapkan teknik _reconstruct algorithm_ / penulisan ulang alur program. (Python)

main : 
```Python
dat = [
    0x37, 0x33, 0x36, 0x66,
    0x36, 0x63, 0x36, 0x31, 
    0x37, 0x32, 0x37, 0x37, 
    0x36, 0x39, 0x36, 0x65, 
    0x36, 0x34, 0x37, 0x33, 
    0x33, 0x31, 0x33, 0x32, 
    0x33, 0x33
    ]
dec = ''

print('Password Plox:')
_inp = str(input())

for i,c in enumerate(dat):
    dec += chr(c)

if _inp == bytes.fromhex(dec).decode():
    print('Welcome')
else:
    print('try again loser')

```
referensi data :
```
dat : **DAT_004cd928**
```
data tersimpan dalam bentuk nomor _ascii hex_. bentuk data dalam karakter : `736f6c617277696e6473313233` . 

referensi _hex decode_ :
```
mVar3 = encoding/hex::encoding/hex.Decode(dst,src);
```
proses decode dalam bahasa python :
```
_inp = bytes.fromhex(dec).decode()
```
result : **solarwinds123**

PASSWORDNYA adalah **solarwinds123**

**Percobaan eksploitasi**
pecobaan di mulai dengan menjalankan kode hasil penulisan ulang program.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall4)
└> echo solarwinds123 | python3 solver.py
Password Plox:
Welcome
```

eksekusi pada file biner asli

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall4)
└> echo solarwinds123 | ./main
Password Plox:
Welcome
```

kondisi win / berhasil dari biner ini berhasil di picu dengan password **solarwinds123** 

## kesimpulan
Challenge **crackme** kali ini mengharuskan _ctfer_ untuk membaca alur program yang sederhana di tengah _garbage Golang Runtime_ yang rumit tersebut. diperlukan 
ketelitian dan pembacaan pola runtime yang akurat agar dapat memfilter kode mana yang merupakan alur program dan mana yang merupakan mekanisme runtime Golang
