# picoCTF2019-asm1.md
# overview
<img width="440" height="322" alt="image" src="https://github.com/user-attachments/assets/943cfc59-1d42-4fe0-9cbf-7fb16f8c85fe" />

chall ini berbeda dengan jeopardy umum nya. disini kita tidak disuruh mencari flag. tapi memahami kode bahasa assembly dan menganalisisnya untuk mendapatkan hasil (return) yang
akan menjadi flag kita nanti


# analysis
as usual kita diberi file dari picoctf, dengan format ascii text. rupanya isinya adalah kode bahasa assembly dari fungsi. mungkin namanya adalah fungsi asm1().

```Assembly
asm1:
        <+0>:   endbr32
        <+4>:   push   ebp
        <+5>:   mov    ebp,esp
        <+7>:   cmp    DWORD PTR [ebp+0x8],0x4ee
        <+14>:  jg     0x11d3 <asm1+38>
        <+16>:  cmp    DWORD PTR [ebp+0x8],0x27
        <+20>:  jne    0x11cb <asm1+30>
        <+22>:  mov    eax,DWORD PTR [ebp+0x8]
        <+25>:  add    eax,0x12
        <+28>:  jmp    0x11ea <asm1+61>
        <+30>:  mov    eax,DWORD PTR [ebp+0x8]
        <+33>:  sub    eax,0x12
        <+36>:  jmp    0x11ea <asm1+61>
        <+38>:  cmp    DWORD PTR [ebp+0x8],0x7b8
        <+45>:  jne    0x11e4 <asm1+55>
        <+47>:  mov    eax,DWORD PTR [ebp+0x8]
        <+50>:  sub    eax,0x12
        <+53>:  jmp    0x11ea <asm1+61>
        <+55>:  mov    eax,DWORD PTR [ebp+0x8]
        <+58>:  add    eax,0x12
        <+61>:  pop    ebp
        <+62>:  ret
```
jika melihat dengan seksama, ini adalah fungsi dengan 1 parameter. karena program melakukan kondisi yang mirip if (cmp) yang terus membandingkan nilai konstanta dengan alamat
memori `ebp+0x8` dimana alamat memori itu adalah tempat argumen 1 dari suatu fungsi jika di arsitektur 32 bit.

sepertinya kode assembly ini memiliki beberapa kondisi yang harus ditepati untuk mencapai nilai tertentu. mari lihat instruksi dari picoctf :  
**What does **asm1(0x27)** return? Submit the flag as a hexadecimal value (starting with '0x')**

artinya kode ini dijalankan dengan argumen `0x27` (39 dalam desimal) . jadi alamat memori tersebut menyimpan nilai nya `rbp+0x8 = 0x27`. jadi jika di analisis dengan argumen tersebut:  

pada kondisi pertama :
```Assembly
        <+7>:   cmp    DWORD PTR [ebp+0x8],0x4ee
        <+14>:  jg     0x11d3 <asm1+38>
```
membandingkan ebp+0x8 dengan 0x4ee, karena 0x27 < 0x4ee maka instruksi jg (jump greater) tidak dieksekusi dan program lanjut aja ke bawah.

kondisi kedua :
```Assembly
        <+16>:  cmp    DWORD PTR [ebp+0x8],0x27
        <+20>:  jne    0x11cb <asm1+30>
```
membandingkan argumen dengan 0x27. karena argumen kita rbp+0x8 ini bernilai 0x27. maka program tidak mengeksekusi jne (jump not equal) dan proram lanjut kebawah lagi.

kondisi ketiga :
```Assembly
        <+22>:  mov    eax,DWORD PTR [ebp+0x8]
        <+25>:  add    eax,0x12
        <+28>:  jmp    0x11ea <asm1+61>
...................................................
        <+61>:  pop    ebp
        <+62>:  ret
```
ini adalah kondisi terakhir dari program. setelah melewati berbagai kondisi tadi, argumen dimasukkan ke register eax. lalu melakukan operasi aritmatika tambah `eax + 0x12`
karena** eax bernilai ebp+0x8 yang menyimpan 0x27 **, maka operasinya adalah `0x27 + 0x12 = 0x39` dan program akan melompat ke akhir fungsi (epilog) dengan register eax bernilai
0x39.

done. nilai akhir eax = `0x39` adalah flagnya.
