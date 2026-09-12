# picoCTF2026-Echo Escape 2

# overview
<img width="441" height="389" alt="image" src="https://github.com/user-attachments/assets/b1aad003-cf07-4953-97d3-4b9ca89bf9c0" />

# kerentanan
- buffer overflow

program ini sudah mengggunakan fungsi input standart di bahasa C yaitu fgets, namun terdapat kesalahan dalam mengisi batas maksimal dari fgets tersebut. value maksimal input di
fgets di isi melebihi kapasitas stack sehingga input user bisa menimpa eip address dan melakukan return ke fungsi yang tidak seharusnya dipanggil program. (win)

# note
karena aku sedang latihan untuk kompetisi maka aku coba solve ini tanpa mendownload source code nya dan tanpa ai.

# analysis
setelah mendownload file binarynya, langsung saja di jalankan. 
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(echo-escape2)
└> ./vuln
Enter the secret key: 1234567890
You entered:, 1234567890
Goodbye!
```

program ini meminta input dan melakukan print input kita tadi, tidak ada kerentana format string disini karena kau sudah coba input format %p dan outputnya juga %p. 
aku coba lanjutkan analisis pakai gdb. dan menemukan fungsi menarik,
```
pwndbg> info funcitons
Undefined info command: "funcitons".  Try "help info".
pwndbg> info functions
All defined functions:

Non-debugging symbols:
0x08049000  _init
0x080490d0  printf@plt
0x080490e0  fflush@plt
0x080490f0  fgets@plt
0x08049100  fclose@plt
0x08049110  perror@plt
0x08049120  puts@plt
0x08049130  exit@plt
0x08049140  __libc_start_main@plt
0x08049150  fopen@plt
0x08049160  _start
0x080491a0  _dl_relocate_static_pie
0x080491b0  __x86.get_pc_thunk.bx
0x080491c0  deregister_tm_clones
0x08049200  register_tm_clones
0x08049240  __do_global_dtors_aux
0x08049270  frame_dummy
0x08049276  win
0x08049328  vuln
0x0804939d  main
0x080493f0  __libc_csu_init
0x08049460  __libc_csu_fini
0x08049465  __x86.get_pc_thunk.bp
0x0804946c  _fini
pwndbg>
```

yep ada win : `0x08049276  win` ini adalah target ku. selanjutnya adalah mencari kerentanan. saat ku coba disassembly main, ada fungsi menarik bernama vuln, seperti namannya
fungsi ini memiliki kerentanan. yaitu buffer overflow.


bagian epilog fungsi vuln:
```Assembly
pwndbg> disas vuln
Dump of assembler code for function vuln:
   0x08049328 <+0>:     endbr32
   0x0804932c <+4>:     push   ebp
   0x0804932d <+5>:     mov    ebp,esp
   0x0804932f <+7>:     push   ebx
   0x08049330 <+8>:     sub    esp,0x24
```

bagian fgets yang meminata input secret key :
```Assembly
   0x08049370 <+72>:    push   0x80
   0x08049375 <+77>:    lea    eax,[ebp-0x28]
   0x08049378 <+80>:    push   eax
   0x08049379 <+81>:    call   0x80490f0 <fgets@plt>
```

pada epilog program membuat stack dengan ukuran 0x24. sedangkan, pada fungsi fgets, malah dibatasi melebihi stack yaitu hingga 0x80. disini ditemkanlah kerentanan **buffer 
overflow**

selanjutnya adalah menghitung offset dari input ke eip address.

--belum selesai--
