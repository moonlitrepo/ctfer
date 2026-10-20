# Garbage Hell Write Up

## deskripsi

Nama Challenge: Garbage Hell  
Kategori: Reverse Engineering  
description:
  Argh, your final boss rev is in base64 (or dont follow the instruction) ? Should it be easy or mending turu?
  
  Get the correct input!

  author: aseng


 

FLAG: **LKS{F5gSxQkp8ynpGFyvZBeUUAbd}**

## Ringkasan
challenge ini memberikan sebuah file executable dengan format **PE32** yang di compile dari bahasa **Golang**. Semua string serta nama fungsi dihilangkan. main program dapat dicari dengan menelusuri entry point, lalu menganalisis algoritma validasi flag yang ada di main function.

## analisis awal

pemeriksaan metadata dan menjalankannya untuk mencari tahu perilaku dari program yang diberikan:
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(garbagehell)
└> file challenge.exe
challenge.exe: PE32+ executable (console) x86-64, for MS Windows, 8 sections
┌[rotalactf]-[LAPTOP-6QMID52F]-(garbagehell)
└> ./challenge.exe
I only know base64-like LKS flag , so please give me one please? >>flagflag
Bad! :(
┌[rotalactf]-[LAPTOP-6QMID52F]-(garbagehell)
└> strings challenge.exe | grep 'lks{'
[tidak ada hasil]
```
observasi :
- karakteristik file : PE32+ executable
- perilaku : program berkata bahwa dia hanya mengetahui _base64-like LKS Flag_ (flag seperti base64) , lalu meminta input. input random yang di masukkan membuat program mencetak
  teks **Bad! :(** . ini mengindikasikan adanya kondisi khusus yang dapat terpenuhi jika input yang dimasukkan memenuhi syarat syarat tertentu.
- tidak terdeteksi adanya string flag pada file. ini membuktikan bahwa string flag telah di enkripsi, encode atau melewati algoritma obfuskasi kustom sehingga string flag tidak
  tersedia dalam bentuk plaintext

untuk menanggapi file program PE32 saya menggunakan tools DIE dan Ghidra

## analisis lanjutan
hasil analisis statis dari DIE:
```
Operation system: Windows (7) [AMD64, 64-bit, Console]  
Compiler: Go (1.18.X-1.24.0)  
Language: Go
```
file program ini di compile dari bahasa Golang. terferifikasi pada key compiler dan languagenya yang tertulis kata Go (Golang).  

analisis saya lanjutkan menggunakan ghidra. nama fungsi dan strings tidak tersedia. main bisa di lacak melalui entrypoint dan menelusuri mekanisme runtime.

rute navigasi entry ke main:
```
entry : ppuStack_38 = &PTR_FUN_1402a16a8;
PTR_FUN_1402a16a8 : FUN_140037860
FUN_140037860 :
  if ((DAT_1403cf69e == '\0') && (DAT_1403cf69d == '\0')) {
    main(uVar5,param_2); /*nama fungsi sudah saya rename*/
    if (DAT_1403cf6cc != 0)
```
karena mekanisme runtime go da stripped binary, akan cukup merepotkan dalam proses analisis nya. maka saya memotong kode tidak penting dan hanya mengambil bagian yang saya asumsikan memengaruhi alur program
 
Note : source telah di potong dan disederhanakan . kode dibawah bukan kode valid yang siap di eksekusi tapi kode yang memuat inti dari program ini (menurut analisis):
```C
void main(x,y)
  array = (char *)*auVar6._16_8_;
  if (*array == 'L') {
    if (uVar1 < 2) {
      not_valid(1,var,1);
    }
    if (array[1] == 'K') {
      if (uVar1 < 3) {
        not_valid(2,var,2);
      }
      if (array[2] == 'S') {
        if (uVar1 < 4) {
          not_valid(3,var,3);
        }
        if (array[3] == '{') goto validate;
      }
    }
  }
  validate:

    if (*(char *)(*stack + 0x1c) != '}') {
      auVar13 = not_valid(_,param_2);
    }
    if (0x1b < (uint)stack[1]) {
      ptr_stack = *stack;
      local_70 = (sdword *)(ptr_stack + 0x10);
      local_68 = 4;
      local_60 = (sdword *)(ptr_stack + 0x14);
      local_58 = 4;
      local_50 = ptr_stack + 0x18;
      local_48 = 4;
      if (*(sdword *)(ptr_stack + 0x18) != 0x64624155) {
        _ = not_valid(_,param_2);
      }
      if ((local_68 != 4) || (*local_70 != 0x76794647)) {
        _ = not_valid(_,param_2);
      }
      if (*(sdword *)(ptr_stack + 8) != 0x706b5178) {
        _ = not_valid(_,param_2);
      }
      if ((local_58 != 4) || (*local_60 != 0x5565425a)) {
        _ = not_valid(_,param_2);
      }
      if (*(sdword *)(ptr_stack + 0xc) != 0x706e7938) {
        _ = not_valid(_,param_2);
      }
      if (*(sdword *)(ptr_stack + 4) != 0x53673546) {
        not_valid(_,param_2);
      }
    }
```

ternyata flag tersedia dalam bentuk little endian hex. berikut datanya setelah diurutkan 
```
data (setelah diurutkan sesuai stack) :
[0x53673546, 0x706b5178, 0x706e7938, 0x76794647, 0x5565425a, 0x64624155]
```

untuk mengetahui nilai asli dari data yang tersedia bisa di reverse menggunakan python

```python
#         0x4         0xc      0x14       0x8       0x10      0x18
data = [0x53673546,0x706e7938,0x5565425a,0x706b5178,0x76794647,0x64624155]
filtered = []
for i in data:
    chunk = i.to_bytes(4,byteorder='big')
    filtered.append(chunk[::-1].decode())

ke = [0,3,1,4,2,5]
plain = ''
plain += "LKS{"
for i in ke:
    plain += filtered[i]
plain += '}'

print(plain)
```

result :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(garbagehell)
└> python3 solver.py
LKS{F5gSxQkp8ynpGFyvZBeUUAbd}
┌[rotalactf]-[LAPTOP-6QMID52F]-(garbagehell)
└> ./challenge.exe
I only know base64-like LKS flag , so please give me one please? >>LKS{F5gSxQkp8ynpGFyvZBeUUAbd}
Good! :)
```

kesimpulan :
program ini menggunakan algoritma validasi yang sangat sederhana. hanya membandingkan input dengan bentuk little endian hex yang ada di source code.
karena mekanisme go + stripped, algoritma tersebut menjadi sulit dilacak keberadaannya serta sulit di analisis.
