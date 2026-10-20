# picoCTF2026-Autorev1.md

hello guys welcome to my write up again

# summary
challenge Autorev1 ini termasuk chall baru karena baru dirilis tahun 2026 ini. selain itu, challenge ini cukup unik karena ia memberikan kita file proramnya secara tidak wajar.
bukan di download bukan di unzip tapi langsung dikirimin teks bytes mentahnya lewat koneksi nc nya. setelah itu kita harus memasukkan secret dalam waktu kurang dari 1 detik. itu 
sangat tidak wajar untuk tangan manusia sepertiku. haha

# tools
- xxd
- ghidra
- pwntools (python libc)

# recon
pertama mari kita lihat dulu di picoCTF nya, karena aku tidak di beri file program apapun jadii satu satunya sumber informasi mengenai challenge ini adalah koneksi nc nya.  
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> nc mysterious-sea.picoctf.net 64988
Welcome! I think I'm pretty good at reverse enginnering. There's NO WAY anyone's better than me. Wanna try?
I have 20 binaries I'm going to send you and you have 1 second EACH to get the secret in each one. Good luck >:)
3126571774
Here's the next binary in bytes:
7f454c4602010100000000000000000002003e0001000000501040000000000040000000000000002839000000000000000000004000
38000d00400020001f000600000004000000400000000000000040004000000000004000400000000000d802000000000000d8020000
00000000080000000000000003000000040000001803000000000000180340000000000018034000000000001c000000000000001c00
0000000000000100000000000000010000000400000000000000000000000000400000000000000040000000000068050000000000
006 --> dan seterusnya hingga seluruh teksnya berukuran lebih dari 5kb
```

dan di paling bawah ada input secret
```
0200000000000000000000000000000000000000d83200000000000048030000000000001e0000001200000008000000000000001800000000000000090000000300000000000000000000000000000000000000203
6000000000000cd01000000000000000000000000000001000000000000000000000000000000110000000300000000000000000000000000000000000000ed370000000000003b010000000000000000000000000
00001000000000000000000000000000000
What's the secret?:idonknowbruh

┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└>
```

oke jika kita langsung menyimpulkan nya dari 1 recon singkat ini, ada ribuan karakter yang kemungkinan adalah program elf. lalu ada juga semacam angka beberapa digit di atas
bisa jadi itu adalah secretnya. namun karena teks programnya sangat banyak jadi perlu waktu lebih dari 1 detik untuk scrolling ke atas untuk mengcopy secret dan mempastenya lagi
di bawah. pembuat soal sangat pintar dalam memikirkan pemberian program dalam bentuk bytes ini, GG.  

nah saat aku coba masukkan angka random di atas program mengatakan aku to slow bukan keluar dan mengakhiri koneksi. menarik, mungkin saja ini memang adalah secretnya. 
```
0200000000000000000000000000000000000000d83200000000000048030000000000001e00000012000000080000000000000018000000000000000900000003000000000
000000000000000000000000000002036000000000000cd010000000000000000000000000000010000000000000000000000000000001100000003000000000000000000000
00000000000000000ed370000000000003b01000000000000000000000000000001000000000000000000000000000000
What's the secret?:$ 3093673626
Too slow :(
[*] Got EOF while reading in interactive
$
```
# exploit
aku akan gunakan pwntools untuk mencoba menginput secret tersebut :
```python
from pwn import *

SERVER = 'mysterious-sea.picoctf.net'
PORT = 64988

io = remote(SERVER,PORT)

io.recvuntil(b'\n')
data = io.recvline().strip() #mengambil secret di atas
print(f'[recv] data : {data.decode()}')

io.sendlineafter(b"What's the secret?:",data) # menginput secret 
print(f"[send] berhasil mengirim {data}")

io.interactive() # memberikan akses penuh ke gua
```
namun hal yang lebih aneh terjadi. inputku berhasil dan program mengeluarkan teks CORRECT, tapi dia juga melakukan hal yang sama di awal, print secret dan byte dari programnya lagi
dan meminta secret lagi. hah?
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> python3 auto.py
[+] Opening connection to mysterious-sea.picoctf.net on port 58103: Done
[recv] data : 4076433800
[send] berhasil mengirim b'4076433800'
[*] Switching to interactive mode
Correct!
1703222020
Here's the next binary in bytes:
7f454c4602010100000000000000000002003e000100000050104000000000004000000000000000283900000000000000000000400038000d00400020001f00060000000400000040000
```

jadi server sepertinya ingin kita menginput secret lebih dari 1 kali, kalau sudah begini. akan ada kemungkinan setelah secret ke 2 akan ada secret baru lagi. jadi
untuk berjaga jaga. aku membuat script python ini yang akan berhenti hingga error. (aku menghabiskan waktu 3 sesi koneksi untuk membuat script ini berjalan lancar)

```python
from pwn import *

context.log_level ="error"
SERVER = 'mysterious-sea.picoctf.net'
PORT = 58533
def send():
    io = remote(SERVER,PORT)
    eror = False
    while eror == False:
        try:
            io.recvuntil(b'\n')
            data = io.recvline().strip()
            print(f'[recv] data : {data.decode()}')
            try:
                io.sendlineafter(b"What's the secret?:",data)
                print(f"[send] berhasil mengirim {data}")
            except:
                print("[Bad] error gatau kenapa")
                recv = io.recvall()
                print(recv.decode())
                io.close()
                eror = True
                break
        except:
            print("[Bad] gagal menerima data")
            io.close()
            eror = True
            break
    print("[info] brute force selesai")

send()

```

berikut hasil bruteforcenya :
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> python3 exploit.py
[recv] data : 2212293345
[send] berhasil mengirim b'2212293345'
[recv] data : 2520899008
[send] berhasil mengirim b'2520899008'
[recv] data : 1414263680
[send] berhasil mengirim b'1414263680'
[recv] data : 3969220385
[send] berhasil mengirim b'3969220385'
[recv] data : 931903424
[send] berhasil mengirim b'931903424'
[recv] data : 1321055875
[send] berhasil mengirim b'1321055875'
[recv] data : 2757590588
[send] berhasil mengirim b'2757590588'
[recv] data : 862164915
[send] berhasil mengirim b'862164915'
[recv] data : 1862134710
[send] berhasil mengirim b'1862134710'
[recv] data : 583128206
[send] berhasil mengirim b'583128206'
[recv] data : 3950393721
[send] berhasil mengirim b'3950393721'
[recv] data : 3663004068
[send] berhasil mengirim b'3663004068'
[recv] data : 1505438647
[send] berhasil mengirim b'1505438647'
[recv] data : 3225385166
[send] berhasil mengirim b'3225385166'
[recv] data : 316869191
[send] berhasil mengirim b'316869191'
[recv] data : 197218200
[send] berhasil mengirim b'197218200'
[recv] data : 3682889330
[send] berhasil mengirim b'3682889330'
[recv] data : 2274504848
[send] berhasil mengirim b'2274504848'
[recv] data : 2924392368
[send] berhasil mengirim b'2924392368'
[recv] data : 1021920068
[send] berhasil mengirim b'1021920068'
[recv] data : Woah, how'd you do that??
[Bad] error gatau kenapa
Here's your flag: picoCTF{4u7o_r3v_g0_brrr_78c345aa}


[info] brute force selesai
```
done 
**flag: picoCTF{4u7o_r3v_g0_brrr_78c345aa}**

rupanya ada sekitar 20 secret disini. berkat pwntools ini bisa selesai dalam kurang dari 20 detik.  \

# How it works
harusnya ini ada di atas tapi karena menurutku pengekstrakan file progam tidak terlalu memengaruhi proses pengerjaan chall jadi aku letakkan di bawah aja.  
pertanyaannya, apa teks panjang yang mengganggu itu? saat ku copy semua dan membuatnya menjadi file dengan nama binary, linux belum mendeteksi nya sebagai file elf. dan aku baru
sadar, ini terlihat seperti hex. atau memang hex? jadi aku decode dulu dan meletakkannya ke file lain bernama challenge. dan itu bekerja dengan baik!

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> file binary
binary: ASCII text, with very long lines (33360)
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> xxd -r -p binary challenge
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> file challenge
challenge: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
 BuildID[sha1]=c2d0bd6a2729e38af0e78d0de178a8b65112a43a, for GNU/Linux 3.2.0, not stripped
```

jalankan filenya
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> chmod +x challenge
┌[rotalactf]-[LAPTOP-6QMID52F]-(autorev1)
└> ./challenge
What's the secret?
idk bruh
Nice try :(
```

dengan ini kita berhasil mengekstrak file program nya. jika ingin melihatnya di ghidra kurang lebi programnya seperti ini
```

undefined8 main(void)

{
  int local_10;
  int local_c;
  
  local_c = -1597693467;
  local_10 = 0;
  puts("What\'s the secret?");
  __isoc99_scanf(&DAT_00402023,&local_10);
  if (local_c == local_10) {
    puts("Correct!");
  } 
  else {
    puts("Nice try :(");
  }
  return 0;
}


```  
Sangat amat sederhana bukan? program ini hanya membandingkan input kita dengan variabel local_c disitu, tapi di server tidak begitu karena program ini diulangi sebanyak 20 kali
dan tiap secretnya berbeda, maka karena itu sedikit pengetahuan tentang python akan sangat membantu terutama adanya library pwntools yang sudah menjadi makanan wajib para pwners / 
reverse engineers.

By the way, to the creator of this challenge, SkrubLawd. just so you know, I’m the 2,000th person to solve this Autorev1 challenge—hahaha, interesting, right?
