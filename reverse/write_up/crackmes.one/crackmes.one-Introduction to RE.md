# crackmes.one-Introduction to RE

# overview
<img width="743" height="407" alt="image" src="https://github.com/user-attachments/assets/69b327f7-363b-4e7d-9a23-881530fbcf18" />

ini adalah challenge crack password sederhana. kita hanya perlu melakukan decompile atau sedikit analisis jika dengan gdb 
```C

undefined8 main(void)

{
  int iVar1;
  long in_FS_OFFSET;
  char local_118 [264];
  long local_10;
  
  local_10 = *(long *)(in_FS_OFFSET + 0x28);
  printf("Guess The Pass: ");
  __isoc23_scanf("%255s",local_118);
  iVar1 = strcmp(local_118,"7Wtyr");
  if (iVar1 == 0) {
    puts("[OK] Passowrd Found");
  }
  else {
    puts("[ERROR] Password is incorrect");
  }
  if (local_10 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}

```
```
┌[rotalactf]-[LAPTOP-6QMID52F]-(introduction-to-re)
└> ./passguess
Guess The Pass: 7Wtyr
[OK] Passowrd Found
```
