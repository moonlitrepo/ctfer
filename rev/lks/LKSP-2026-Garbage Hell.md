# Garbage Hell Write Up

## deskripsi

Nama Challenge: Garbage Hell  
Kategori: Reverse Engineering  
description:
  Argh, your final boss rev is in base64 (or dont follow the instruction) ? Should it be easy or mending turu?
  
  Get the correct input!

  author: aseng

value: 500  
type: standard  

FLAG: LKS{F5gSxQkp8ynpGFyvZBeUUAbd}

## Ringkasan
challenge ini memberikan sebuah file executable format PE yang di compile dari bahasa Golang. Semua string serta nama fungsi benar benar dihilangkan. main program dapat dicari
dengan menelusuri entry point lalu melakukan revere pada algoritma validasi flag yang ada di main function.

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

bagian utama dari fungsi main :
```C

void main(undefined8 param_1,double param_2)
  pcVar2 = (char *)*auVar6._16_8_;
  if (*pcVar2 == 'L') {
    if (uVar1 < 2) {
      not_valid(1,uVar11,1);
    }
    if (pcVar2[1] == 'K') {
      if (uVar1 < 3) {
        not_valid(2,uVar11,2);
      }
      if (pcVar2[2] == 'S') {
        if (uVar1 < 4) {
          not_valid(3,uVar11,3);
        }
        if (pcVar2[3] == '{') goto LAB_14022b45f;
      }
    }
  }
      if (*(sdword *)(iVar3 + 0x18) != 0x64624155) {
        uVar12 = FUN_14022bc40(uVar12,param_2);
      }
      if ((local_68 != 4) || (*local_70 != 0x76794647)) {
        uVar12 = FUN_14022bc40(uVar12,param_2);
      }
      if (*(sdword *)(iVar3 + 8) != 0x706b5178) {
        uVar12 = FUN_14022bc40(uVar12,param_2);
      }
      if ((local_58 != 4) || (*local_60 != 0x5565425a)) {
        uVar12 = FUN_14022bc40(uVar12,param_2);
      }
      if (*(sdword *)(iVar3 + 0xc) != 0x706e7938) {
        uVar12 = FUN_14022bc40(uVar12,param_2);
      }
      if (*(sdword *)(iVar3 + 4) != 0x53673546) {
        FUN_14022bc40(uVar12,param_2);
      }
```

main memiliki alur yang memvalidasi input user. untuk mengetahui nilai asli dari data yang tersedia bisa di reverse menggunakan python

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
