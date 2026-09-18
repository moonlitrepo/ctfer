# picoCTF2026-secure password database

# overview
Event : picoCTF 2026  
Challenge name : Secure Password Database  
Category : Reverse Engineering  
author : Philip Thayer

kerentanan pada program :
- tidak dilengkapi dengan anti debugger
- simbol program tidak di hilangkan (not stripped)

kerentanan tersebut dapat memungkinkan program untuk di debug dan membocorkan informaasi yang disimpan di register seperti hash password.

# tools
- ghidra
- gdb + pwntools

# analysis
download challenge file dan cek metadatanya 
<img width="1366" height="199" alt="image" src="https://github.com/user-attachments/assets/480dda26-b1aa-4c95-ab3b-14bc8d5423f8" /> 

```
┌──[reno@cybersec]──[~/ctf/rev/securepassworddatabase] [127]
└[]> ./system.out
Please set a password for your account:
helo
How many bytes in length is your password?
4
You entered: 4
Your successfully stored password:
104 101 108 111 10
Enter your hash to access your account!
12345789
```
jadi program disini meminta password, mengubahnya menjadi desimal dan meminta hash dari password tersebut. 

aku lanjutkan analisis dengan ghidra:

decompile:
```C

undefined8 main(void)

{
  uint uVar1;
  char *pcVar2;
  undefined8 uVar3;
  long in_FS_OFFSET;
  int local_128;
  char *local_120;
  ulong local_118;
  char *local_110;
  size_t local_108;
  ulong local_100;
  ulong local_f8;
  FILE *local_f0;
  undefined1 parameter1 [13];
  char local_d8 [31];
  char input [65];
  char local_78 [104];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 40);
  local_110 = calloc(90,1);
  for (local_118 = 0; local_118 < 13; local_118 = local_118 + 1) {
    local_110[local_118 + 60] = obf_bytes[local_118] ^ 170;
  }
  puts("Please set a password for your account:");
  pcVar2 = fgets(input + 1,50,stdin);
  if (pcVar2 != (char *)0) {
    strcpy(local_110,input + 1);
    puts("How many bytes in length is your password?");
    pcVar2 = fgets(local_d8,20,stdin);
    if (pcVar2 != (char *)0) {
      uVar1 = atoi(local_d8);
      printf("You entered: %d\n",(ulong)uVar1);
      puts("Your successfully stored password:");
      for (local_128 = 0; (local_128 <= (int)uVar1 && (local_128 < 90)); local_128 = local_128 + 1)
      {
        printf("%d ",(ulong)(uint)(int)local_110[local_128]);
      }
      putchar(10);
    }
  }
  puts("Enter your hash to access your account!");
  pcVar2 = fgets(input + 1,50,stdin);
  if (pcVar2 != (char *)0) {
    local_108 = strlen(input + 1);
    if ((local_108 != 0) && (input[local_108] == '\n')) {
      input[local_108] = '\0';
    }
    local_100 = strtoul(input + 1,&local_120,10);
    if (local_120 == input + 1) {
      printf("No digits were found");
                    /* WARNING: Subroutine does not return */
      __assert_fail("1 == 0","heartbleed.c",69,"main");
    }
    local_f8 = make_secret(parameter1);
    if (local_f8 == local_100) {
      local_f0 = fopen("flag.txt","r");
      if (local_f0 == (FILE *)0) {
        perror("Could not open flag.txt");
        uVar3 = 1;
        goto LAB_0010173e;
      }
      pcVar2 = fgets(local_78,100,local_f0);
      if (pcVar2 == (char *)0) {
        puts("Failed to read the flag");
      }
      else {
        printf("%s",local_78);
      }
      fclose(local_f0);
    }
  }
  free(local_110);
  uVar3 = 0;
LAB_0010173e:
  if (local_10 != *(long *)(in_FS_OFFSET + 40)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return uVar3;
}

```

jika melihat ke bagian input hash, ada baris yang akan melakukan print flag jika kondisi nya terpenuhi : `local_f8 = make_secret(parameter1);`
```C
    local_f8 = make_secret(parameter1);
    if (local_f8 == local_100) {
      local_f0 = fopen("flag.txt","r");
```

`make_secret`
```C
void make_secret(long param_1)

{
  long local_10;
  
  for (local_10 = 0; obf_bytes[local_10] != '\0'; local_10 = local_10 + 1) {
    *(byte *)(local_10 + param_1) = obf_bytes[local_10] ^ 170;
  }
  *(undefined1 *)(param_1 + 12) = 0;
  hash(param_1);
  return;
}
```

`hash`
```C
long hash(byte *param_1)

{
  byte *local_20;
  long local_10;
  
  local_10 = 5381;
  local_20 = param_1;
  while( true ) {
    if (*local_20 == 0) break;
    local_10 = (long)(int)(uint)*local_20 + local_10 * 33;
    local_20 = local_20 + 1;
  }
  return local_10;
}
```
yep ada hash, tidak mungkin membaliknya. tapi tidak ada value / konstanta password atau semacamnya. artinya fungsi ini dinamis, hasil hashnya sesuai dengan input password. **selama input hash == hasil hash passwrod
maka program akan print flag. **

tapi untungnya program sudah melakukan perhitungan hashnya jadi aku tidak perlu repot repot membuat keygen. 

# exploit
rencana nya : 
- dynamic analysis dengan gdb
- cari kondisi saat program selesai menghitung hash dan mencari dimana hasilnya disimpan
- leak hasil dari register / stack

untuk mencarinya sangat mudah, fungsi yang menghitung hash adalah `make_secret`. maka aku akan memasang breakpoint di alamat setelah fungsi itu dipanggil.
```Assembly
   0x0000000000001672 <+674>:   call   0x135e <make_secret>
   0x0000000000001677 <+679>:   mov    QWORD PTR [rbp-0xf0],rax
   0x000000000000167e <+686>:   mov    rax,QWORD PTR [rbp-0xf0]
   0x0000000000001685 <+693>:   cmp    rax,QWORD PTR [rbp-0xf8]
   0x000000000000168c <+700>:   jne    0x172a <main+858>
```
sepertinya main+679 adalah kandidat terbaik karena register rax , hasil return dari fungsi make_secret masih fresh dari fungsinya.

<img width="677" height="300" alt="image" src="https://github.com/user-attachments/assets/68f2101a-71c1-45b2-8aed-8a8345e72061" />

aku gunakan password `shinobu` dengan ukuran `7` byte. 


<img width="502" height="61" alt="image" src="https://github.com/user-attachments/assets/181e3d65-b6f6-4515-9f47-118f8f59c061" />

karena hasil hash adalah desimal jadi hex value tersebut harus di convert jadi desimal dulu : `15237662580160011234`

cek : 
```
┌──[reno@cybersec]──[~/ctf/rev/securepassworddatabase]
└[]> ./system.out
Please set a password for your account:
shinobu
How many bytes in length is your password?
7
You entered: 7
Your successfully stored password:
115 104 105 110 111 98 117 10
Enter your hash to access your account!
15237662580160011234
Could not open flag.txt: No such file or directory
```
yep lupa bikin flag di lokal, at least program mau print flag. sekarang tinggal lakukan di server dan ambil flag asli.


<img width="563" height="253" alt="image" src="https://github.com/user-attachments/assets/8ec17828-5626-46eb-b19c-229242430258" />

flag = **picoCTF{................}**

kesimpulan : 
sebenarnya cara melakukan solve pada chall ini bisa sangat bervariasi. namun langkah termudah adalah dengan me leak value hasil fungsi hashnya karena program ini sangat rentan dengan debugger. 
