// test with 
// gcc -masm=intel -S test.c -o test.asm
// -S compile only
// intel intel syntax (not att)
#include <stdio.h>
#include <string.h>

int foobar()
{
    //char testStr[] = "pinky";
    //printf("%s", testStr);
    long mark[5] = {19, 10, 8, 17, 9};
    //long xx = 7;
    //long x = 3;
    //char testStr[] = "cool as tangerine, hot as coke";
    //while (xx-- > 33) {
    //printf("%ld\n", xx);
    //};
    return 0;
}

int main()
{
    return foobar();
}
