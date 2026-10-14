# gopher_vault Write up

## deskripsi 
None  
kategori : Reverse Engineering  
Kesulitan : easy - med  
file : [gopher_vault](gopher_vault)  

## ringkasan
file yang diberikan merupakan progam yang di compile dari bahasa **golang**, hasil dekompilasi cukup ramai fungsi runtime yang tidak semuanya memengaruhi alur program. 
flag tersedia pada program dalam kondisi terenkripsi. untuk menyelesaikan _challenge_ ini , algoritma enkripsi perlu di balik.

## analisis awal
Pemeriksaan metadata program dan menjalankan program untuk mengetahui _surface behavior_ atau perilaku permukaan dari program tersebut.
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall1)
└> file gopher_vault
gopher_vault: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, Go BuildID=eLugox0ZdO6PntrHFXuF/tvt2ZdO0sxy_ASujWbEh/gdHoJadCb9rs7R5K-6YV/nuu21xY-GSRIVfa67dLX, stripped
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall1)
└> ./gopher_vault
Flag: flag
Access denied.
```
percobaan _strings_
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall1)
└> strings gopher_vault | grep -i 'main.main\|PRALKS'
main.main
```
observasi :
- Karakteristik :  file **ELF x86-64** . _statically linked_, _stripped_
- Bahasa : **golang** , terverifikasi pada metadata : **Go BuildID=--**
- Perilaku program : program meminta input flag , dan membandingkannya dengan string flag dalam kondisi khusus. terverifikasi pada hasil strings yang tidak mendeteksi adanya string
  flag . ini mengindikasikan string flag telah di enkripsi, di encode atau telah melewati algoritma obfuskasi kustom pada saat runtime program. 
- Symbols Recovery : karena mekanisme _runtime Go_ , nama fungsi tidak dihilangkan sepenuhnya. ini dibuktikan dengan adanya string _main.main_ pada program

## analisis lanjutan
untuk mencari informasi lebih lanjut saya lakukan dekompilasi program menggunakan _Ghidra_. fungsi _main.main_ bisa di lacak dengan **string xref** / fitur **string search** di ghidra.

pada hasil dekompilasi fungsi _main.main_ baris ke 75 , _main.main_ memanggil fungsi lain bernama _main.verify_ .
```C
cVar1 = main.verify(sVar8.str,sVar8.len);
```
dekompilasi fungsi _main.verify_ (hasil _reconstruct algorithm_):
```C
undefined8 main::main.verify(int string_input,int string_len)

{
  int i;
  byte c;

  if (0x25 != string_len) {
    return 0;
  }
  i = 0;
  while( true ) {
    if (string_len <= i) {
      return 1;
    }
    c = *(byte *)(string_input + i) ^ ptr_key[uVar1];
    if (ptr_enc[i] != (byte)((char)i * 7 + (c << 3 | c >> 5))) break;
    i = i + 1;
  }
  return 0;
}
```
fungsi ini menyimpan program inti dari teknik enkripsi yang digunakan untuk perbandingan input dengan flag.
observasi :
- panjang flag adalah **0x25 byte** (37 dalam desimal)
- flag tersimpan dalam bentuk terenkripsi di _ptr_enc_ (**DAT_005263e0**)
- kunci xor yang digunakan tersimpan di _ptr_key_ (**DAT_00526124**)
- algoritma enkripsi : tiap _byte_ input di **xor** dengan key[i] , lalu **i*7** dikurangi dengan bit **shiftleft 3** dari hasil **xor** tadi.

value _ptr_enc_ :
```Python
enc = [
    0xb9, 0x1a, 0x97, 0x8e,
    0x55, 0x0c, 0x0a, 0x4b, 
    0x58, 0xc7, 0x30, 0x3d, 
    0x0c, 0x73, 0x02, 0x4a, 
    0xe0, 0x4f, 0x16, 0x00, 
    0x7c, 0x4d, 0xa2, 0x8b, 
    0x48, 0x2a, 0xce, 0x75, 
    0xae, 0xdb, 0x2a, 0x54, 
    0xa0, 0x69, 0xde, 0xdf, 
    0xcc 
    ]
```
value _ptr_key_ :
```Python
key = [0x67, 0x30, 0x70, 0x63, 0x6c, 0x6e]
```

## eksploitasi

_inverse algorithm_
```Python

key = [
    0x67, 0x30, 0x70, 0x63, 
    0x6c, 0x6e
    ]

enc = [
    0xb9, 0x1a, 0x97, 0x8e,
    0x55, 0x0c, 0x0a, 0x4b, 
    0x58, 0xc7, 0x30, 0x3d, 
    0x0c, 0x73, 0x02, 0x4a, 
    0xe0, 0x4f, 0x16, 0x00, 
    0x7c, 0x4d, 0xa2, 0x8b, 
    0x48, 0x2a, 0xce, 0x75, 
    0xae, 0xdb, 0x2a, 0x54, 
    0xa0, 0x69, 0xde, 0xdf, 
    0xcc 
    ]
dec = []

for i,c in enumerate(enc):
    _t = c - i*7 & 0xff
    _t = (_t >> 3 | _t << 5) &0xff
    _t = _t ^ key[i%6]
    dec.append(chr(_t))

print("".join(dec))
```

result :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall1)
└> python3 solver.py
PRALKS{str1pp3d_but_n4m3s_st1ll_h3r3}
┌[rotalactf]-[LAPTOP-6QMID52F]-(chall1)
└> ./gopher_vault
Flag: PRALKS{str1pp3d_but_n4m3s_st1ll_h3r3}
Access granted.
```

## kesimpulan



