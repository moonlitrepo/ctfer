# picoCTF2026-Hiddencipher2.md

welcome to my write up again. challenge ini adalah kelanjutan dari hiddencipher1 sebelumnya. namun masalah yang ada pada challenge ini justru lebih sederhana dibanding yang pertama
jadi kita akan di kasi file elf x86-64 bernama hiddencipher2 . awalnya zip tinggal di ekstrak aja. nantinya file program ini akan memberi pertanyaan matematika dasar dan jika jawaban kita
benar, maka program akan mengembalikan string flagnya dalam bentuk hex terenkripsi dengan jawaban benar kita sebagai kuncinya.  

untuk detail nya ada di bawah ini

# recon
formalitas dulu siapa tahu file ini unik, tapi sepertinya ini adalah program biasa.

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher2)
└> file hiddencipher2
hiddencipher2: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=599eedd164a0821201befcb967a2529efa0cc3ce, for GNU/Linux 3.2.0, not stripped
```

saat program dijalankan, ia akan menanyakan pertanyaan matematika tersulit yang pernah aku kerjakan. setelah berhasil menjawabnya program dengan senang hati memberikan flagnya
dalam bentuk terenkripsi. 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher2)
└> ./hiddencipher2
What is 8 - 6? 2
Encoded flag values:
224, 210, 198, 222, 134, 168, 140, 246, 204, 194, 214, 202, 190, 204, 216, 194, 206, 250
```

**Langkah terbaik untuk melihat apa yang terjadi di balik layar adalah dengan mendecompile file program tersebut. aku menggunakan ghidra**  

aku akan mengambilkan potongan kode nya jadi kita tidak perlu membaca full hasil decompilenya. aku juga sudah merename beberapa nama variabel pentingnya jadi ini akan sedikit lebih mudah dibaca 
yang jelas kita harus liat dulu fungsi mainnya.

```
  correct_answer = generate_math_question(&operand,&x,&y);
  printf("What is %d %c %d? ",(ulong)x,(ulong)(uint)(int)operand,(ulong)y);
  fflush(stdout);
  answer = __isoc23_scanf(&DAT_0010201d,&input);
  if (answer == 1) {
    if (correct_answer == input) {
      flag_file = (void *)read_flag_file("flag.txt");
      if (flag_file == (void *)0) {
        uVar2 = 1;
      }
      else {
        encode_flag(flag_file,correct_answer);
        free(flag_file);
        uVar2 = 0;
      }
    }
    else {
      puts("Wrong answer! No flag for you.");
      uVar2 = 1;
```

oke disini main memanggil 2 fungsi lain yaitu 
- generate_math_question(&operand,&x,&y)
- encode_flag(flag_file,correct_answer)

jika kita membaca alur nya program ini meminta jawaban dari soal yang dibuat oleh fungsi generate_math_question itu. lalu jawaban kita disimpan di variabel input. setelah
input dibandingkan dengan corrrect_answer program akan masuk ke fungsi encode_flag.  

namun, ada hal menarik disini. fungsi encode flag itu mengggunakan 2 argumen, yang pertama adalah file flag nya lalu correct answer. apa yang akan program lakukan dengan jawaban matematika
tadi? satu satunya cara untuk mengetahuinya adalah dengan masuk ke fungsi itu.  

```
void encode_flag(long flag,int correct_answer)

{
  int i;
  
  puts("Encoded flag values:");
  for (i = 0; *(char *)(flag + i) != '\0'; i = i + 1) {
    printf("%d",(ulong)(uint)(*(char *)(flag + i) * correct_answer)); <-- enkripsi terjadi disini.
    if (*(char *)(flag + (long)i + 1) != '\0') {
      printf(", ");
    }
  }
  putchar(10);
  return;
```
jadi apa yang dilakukan fungsi ini? . jelas disitu ada perulangan for untuk membaca file flag.txt nya per byte hingga menabrak null bytes (\0) sebagai tanda akhir string. 
lalu potongan flag tersebut akan di kalikan dengan jawaban benar kita. dan di print ke layar kita. rupanya sangat sederhana.  

jika ingin penjelasan bisa baca ini, atau kalau mau langsung exploit skip aja dah bagian ini  
# how it works
mulai dari for (i = 0; *(char *)(flag + i) != '\0'; i = i + 1)  
sebenarnya flag **bukan variabel yang menyimpan string flag**. tapi adalah **pointer yang menunjuk ke suatu alamat di program yang menyimpan kumpulan karakter flag** per byte nya.
nah makannya itu bisa ada flag + i. karena misal alamat 0x01 sudah dibaca maka flag + i = 0x01 + 1 = 0x02 dan akan bertambah seterusnya hingga program menabrak null bytes.

selanjutnya bagian enkripsi kustom. disini bagian intinya adalah (flag + i) * correct_answer. jika karakter pertama flag adalah p dan correct answernya 3 misal.
maka rumusnya akan jadi gini  
- index pertama dari kata pico
enc = p * correct_answer 
enc = 112 * 3  
enc = 336 
- index kedua
enc = i * correct_answer

dan seterusnya. jadi didapatlah angka enkripsi sepert ini  224, 210, 198, 222, 134, 168, 140, 246, 204, 194, 214, 202, 190, 204, 216, 194, 206, 250

# exploit
langkah selanjutnya adalah jelas kita harus membalik logika enkripsi tersebut. jika flag di enkripsi dengan di kali maka kita harus membaliknya dengan **membagi** flagnya dengan 
kunci yang sama yang digunakan untuk mengalikannya.  

```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher2)
└> nc crystal-peak.picoctf.net 50345
What is 7 - 3? 4
Encoded flag values:
448, 420, 396, 444, 268, 336, 280, 492, 436, 208, 464, 416, 380, 392, 204, 416, 196, 440, 400, 380, 396, 196, 448, 416, 204, 456, 380, 204, 196, 224, 212, 404, 400, 200, 404, 500
```
oke kita sudah mendapatkan flag asli dari server, lalu saatnya didecode. 
bisa pakai skrip python sederhana seperti ini:

```

local_encrypt = [1008, 945, 891, 999, 603, 756, 630, 1107, 918, 873, 963, 909, 855, 918, 972, 873, 927, 1125]
c = 9
decrypt = [chr(i // c) for i in local_encrypt]
print(f'flag local : {"".join(decrypt)}')

server_enc = [448, 420, 396, 444, 268, 336, 280, 492, 436, 208, 464, 416, 380, 392, 204, 416, 196, 440, 400, 380, 396, 196, 448, 416, 204, 456, 380, 204, 196, 224, 212, 404, 400, 200, 404, 500]
c = 4
decrypt = [chr(i // c) for i in server_enc]
print(f'flag server : {"".join(decrypt)}')
```
exekusi
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(hidden-cipher2)
└> python3 exploit.py
flag local : picoCTF{fake_flag}
flag server : picoCTF{m4th_b3h1nd_c1ph3r_3185ed2e}
```

done 
flag = **picoCTF{m4th_b3h1nd_c1ph3r_3185ed2e}**
yep kurang lebih begitu. intinya ini adalah proses enkripsi kustom yang sangat sederhana. penting si belajar bahasa c biar bisa ngebaca alur program dari hasil decompilenya
