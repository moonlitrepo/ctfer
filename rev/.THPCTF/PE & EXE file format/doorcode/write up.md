# Write Up

## deskripsi
None  
Kategori : Reverse Engineering  
Tingkat kesulitan : Mudah -Sedang  
File : [doorcode](doorcode)

## Ringkasan
file program _exe_ ini menyimpan string flag dalam kondisi terekripsi. algoritma enkripsi tersebut hanya melibatkan operasi xor dan index string yang _reverse-able_ 

## analisis awal
pemeriksaan metadata dan perilaku program.
```
└> file doorcode.exe
doorcode.exe: PE32+ executable (console) x86-64, for MS Windows, 19 sections
┌[rotalactf]-[LAPTOP-6QMID52F]-(day14-win-analysis)
└> ./doorcode.exe
Code: kode1234
Locked.
┌[rotalactf]-[LAPTOP-6QMID52F]-(day14-win-analysis)
└> strings doorcode.exe| grep -i PRALKS
[tidak ada hasil]
```
Observasi :
- file : PE32+ executable
- perilaku : program ini meminta _code_ input lalu mencetak teks _Locked_ . ini mengindikasikan adanya _compare_ yang membutuhkan input khusus untuk membuka sesuatu tersebut.
- flag Recovery : tidak terdeteksi adanya string flag pada file ini. membuktikan bahwa flag telah melewati algoritma obfuskasi, enkripsi atau encode sehingga _plaintext_ dari flag tidak tersedia pada program. terverifikasi pada percobaan _strings grep format flag_ yang tidak menghasilkan apapun.

menurut hasil observasi, dibutuhkan input yang memenuhi suatu kondisi yang membuat program membuka kunci tersebut (kondisi _unlocked_) . untuk mengetahui syarat yang memenuhi kondisi tersebut saya lanjutkan analisis lanjutan menggunakan **x64dbg**

## analisis lanjutan
**x64dbg** : main bisa ditemukan melalui xref string yang sebelumnya tercetak saat runtime program. string : **Code** digunakan pada alamat **0x7FF75F0D158A**
alamat tersebut adalah alamat kode dari fungsi main, ini di verifikasi dengan adanya fungsi lain seperti fgets dan puts yang sempat dieksekusi saat runtime.

pada alamat **0x7FF75F0D15F8**, program memanggil fungsi dengan 2 argumen, string input, dan panjang dari string input.
disassembly :
```assembly
push rbp
mov rbp,rsp
sub rsp,70
mov qword ptr ss:[rbp+10],rcx
mov qword ptr ss:[rbp+18],rdx
mov qword ptr ss:[rbp-10],4
cmp qword ptr ss:[rbp+18],16
je doorcode.7FF75F0D14FA
mov eax,0
jmp doorcode.7FF75F0D1574
mov qword ptr ss:[rbp-8],0
jmp doorcode.7FF75F0D1548
mov rdx,qword ptr ss:[rbp+10]
mov rax,qword ptr ss:[rbp-8]
add rax,rdx
movzx eax,byte ptr ds:[rax]
mov ecx,eax
mov rax,qword ptr ss:[rbp-8]
mov edx,0
div qword ptr ss:[rbp-10]
lea rax,qword ptr ds:[7FF75F0D9016]
movzx eax,byte ptr ds:[rdx+rax]
xor ecx,eax
mov edx,ecx
mov rax,qword ptr ss:[rbp-8]
add edx,eax
lea rcx,qword ptr ss:[rbp-50]
mov rax,qword ptr ss:[rbp-8]
add rax,rcx
mov byte ptr ds:[rax],dl
add qword ptr ss:[rbp-8],1
mov rax,qword ptr ss:[rbp-8]
cmp rax,qword ptr ss:[rbp+18]
jb doorcode.7FF75F0D1504
mov rdx,qword ptr ss:[rbp+18]
lea rax,qword ptr ss:[rbp-50]
mov r8,rdx
lea rdx,qword ptr ds:[7FF75F0D9000]
mov rcx,rax
call <JMP.&memcmp>
test eax,eax
sete al
movzx eax,al
add rsp,70
pop rbp
ret 
```
terdapat dua array yang bisa saya definisikan sebagai key, dan data terenkripsi. key terdeteksi pada instuksi **: lea rax,qword ptr ds:[7FF75F0D9016]** yang menyimpan data
**[0x6b, 0x33, 0x79, 0x21] #k4y!**, lalu data terenkripsi di temukan pada proses _compare_ antara hasil enkripsi input dengan data di fungsi _memcmp_ : 
```assembly
lea rdx,qword ptr ds:[7FF75F0D9000]
mov rcx,rax
call <JMP.&memcmp>
```
data tersimpan : 
```
[0x3B, 0x62, 0x3A, 0x70, 0x24, 0x65, 0x08, 0x4B, 0x19, 0x75, 0x0B, 0x1C, 0x25, 0x79, 0x26, 0x54, 0x1F, 0x7D, 0x2E, 0x6C, 0x22, 0x63]
```

untuk memudahkan analisis saya melakukan _reconstruct algorithm_ / penulisan ulang kode, saya menggunakan bahasa _python_
```
enc = [
    0x3B, 0x62, 0x3A, 0x70,
    0x24, 0x65, 0x08, 0x4B,
    0x19, 0x75, 0x0B, 0x1C,
    0x25, 0x79, 0x26, 0x54,
    0x1F, 0x7D, 0x2E, 0x6C,
    0x22, 0x63
    ]

key = [0x6b, 0x33, 0x79, 0x21] #k4y!
str_enc = []
str_input = input('Code: ')
if len(str_input) == 0x16:
    for i in range(0x16):
        tmp = ord(str_input[i]) ^ key[i%4]
        str_enc.append(tmp + i)
    enc = "".join(str(i)for i in enc)
    str_enc = "".join(str(i)for i in str_enc)
    if  str_enc == enc: #memcmp
        print('Unlocked')
else:
    print('Locked')
```
hasil :

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(day14-win-analysis)
└> python3 solver3.py
PRALKS{AAAAAAAAAAAAAA}
[59, 98, 58, 112, 36, 101, 8, 75, 25, 117, 11, 28, 37, 121, 38, 84, 31, 125, 46, 108, 34, 99]
PRALKS{ez_x0r_add_exe}
Code: PRALKS{ez_x0r_add_exe}
Unlocked
┌[rotalactf]-[LAPTOP-6QMID52F]-(day14-win-analysis)
└> ./doorcode.exe
Code: PRALKS{ez_x0r_add_exe}
Unlocked.
```
