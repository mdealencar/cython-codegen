#include "foo.h"

double foo(double a)
{
        return 2 * a;
}

float foof(float a)
{
        return 2 * a;
}

long double fool(long double a)
{
        return 2 * a;
}

void mega_foo1(foo_int32_t a)
{
        (void)a;
}

void mega_foo2(const int a)
{
        (void)a;
}

void mega_foo3(const int *a)
{
        (void)a;
}

void mega_struct_foo(struct yoyo* a)
{
        (void)a;
}

void mega_foo4(foo_func2_t a)
{
}

void mega_foo5(void (*a)())
{
}
