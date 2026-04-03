/**
 * @file test/source/sample/test_Increment.c
 * @brief Tests for the sample service Increment action.
 */

#include "sample/Sample_p.h"
#include "UnitTest.h"

Mock_Vars(5);

sample_housekeeping_t sample_housekeeping;
sample_incrementCtx_t test_ctx;

static void setUp(void)
{
    sample_housekeeping.incrementCount = 0;
    sample_housekeeping.transformCount = 0;
    sample_housekeeping.total = 0;
    sample_housekeeping.lastTransformResult = 0;

    test_ctx.amount = 0;
}

static void test_AddsAmountToTotal(void)
{
    setUp();
    test_ctx.amount = 10;

    sample_Increment(&test_ctx);

    Assert_Equals(10, sample_housekeeping.total);
}

static void test_AccumulatesTotal(void)
{
    setUp();
    test_ctx.amount = 7;

    sample_Increment(&test_ctx);
    sample_Increment(&test_ctx);

    Assert_Equals(14, sample_housekeeping.total);
}

static void test_ZeroAmountDoesNotChangeTotal(void)
{
    setUp();
    sample_housekeeping.total = 5;
    test_ctx.amount = 0;

    sample_Increment(&test_ctx);

    Assert_Equals(5, sample_housekeeping.total);
}

static void test_IncrementsCount(void)
{
    setUp();
    test_ctx.amount = 1;

    sample_Increment(&test_ctx);

    Assert_Equals(1, sample_housekeeping.incrementCount);
}

static void test_IncrementsCountEachCall(void)
{
    setUp();
    test_ctx.amount = 1;

    sample_Increment(&test_ctx);
    sample_Increment(&test_ctx);
    sample_Increment(&test_ctx);

    Assert_Equals(3, sample_housekeeping.incrementCount);
}

int main(int argc, char **argv)
{
    Assert_Init();

    test_AddsAmountToTotal();
    test_AccumulatesTotal();
    test_ZeroAmountDoesNotChangeTotal();
    test_IncrementsCount();
    test_IncrementsCountEachCall();

    Assert_Save();
    return 0;
}
