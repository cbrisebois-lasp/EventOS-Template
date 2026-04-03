/**
 * @file test/source/sample/test_Init.c
 * @brief Tests for the sample service Init action.
 */

#include "sample/Sample_p.h"
#include "UnitTest.h"

Mock_Vars(5);

#define TEST_UNSET 0x42

extern sample_housekeeping_t sample_housekeeping;

static void setUp(void)
{
    sample_housekeeping.incrementCount = TEST_UNSET;
    sample_housekeeping.transformCount = TEST_UNSET;
    sample_housekeeping.total = TEST_UNSET;
    sample_housekeeping.lastTransformResult = TEST_UNSET;
}

static void test_ClearsIncrementCount(void)
{
    setUp();

    sample_Init();

    Assert_Equals(0, sample_housekeeping.incrementCount);
}

static void test_ClearsTransformCount(void)
{
    setUp();

    sample_Init();

    Assert_Equals(0, sample_housekeeping.transformCount);
}

static void test_ClearsTotal(void)
{
    setUp();

    sample_Init();

    Assert_Equals(0, sample_housekeeping.total);
}

static void test_ClearsLastTransformResult(void)
{
    setUp();

    sample_Init();

    Assert_Equals(0, sample_housekeeping.lastTransformResult);
}

int main(int argc, char **argv)
{
    Assert_Init();

    test_ClearsIncrementCount();
    test_ClearsTransformCount();
    test_ClearsTotal();
    test_ClearsLastTransformResult();

    Assert_Save();
    return 0;
}
