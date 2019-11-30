// test with 
// gcc -masm=intel -S test.c -o test.asm
// -S compile only
// intel intel syntax (not att)
// test run,
// gcc -Wall test.c
// ./a.out
#include <stdio.h>
#include <string.h>

//int main()
//{
    ////char testStr[] = "pinky";
    ////printf("%s", testStr);
    ////long xx = 7;
    ////long x = 3;
    ////char testStr[] = "cool as tangerine, hot as coke";
    ////while (xx-- > 33) {
    ////printf("%ld\n", xx);
    ////};
    ////long arry[5] = {19, 10, 8, 17, 9};
    //struct Strut {
      //long id;
      //int value;
      //};  


    //struct Strut ex1;  
    //ex1.id = 6495700;
    //ex1.value = 77;
    //printf( "Ex1 id : %ld\n", ex1.id);
    //printf( "done\n");
    //printf(" ,");
    //return 0;
//}

void testCall() 
{
    printf("%s\n", "block called!");
}

int main()
{
    printf("%s\n", "block call?");
    testCall();
    return 0;
}
