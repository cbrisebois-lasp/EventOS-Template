/**
 * @file test/source/sample/test_Transform.c
 * @brief Tests for the sample service Transform action.
 */

#include "sample/Sample_p.h"
#include "UnitTest.h"

Mock_Vars(5);

sample_housekeeping_t sample_housekeeping;
sample_transformCtx_t test_ctx;

static void setUp(void)
{
    sample_housekeeping.incrementCount = 0;
    sample_housekeeping.transformCount = 0;
    sample_housekeeping.total = 0;
    sample_housekeeping.lastTransformResult = 0;

    test_ctx.id = 0;
    test_ctx.value = 0;
    test_ctx.flags = 0;
}

static void test_ScalesValueByFactor(void)
{
    setUp();
    test_ctx.value = 10;

    sample_Transform(&test_ctx);

    Assert_Equals(30, sample_housekeeping.lastTransformResult);
}

static void test_NegateFlag(void)
{
    setUp();
    test_ctx.value = 5;
    test_ctx.flags = SAMPLE_FLAG_NEGATE;

    sample_Transform(&test_ctx);

    Assert_Equals(-15, sample_housekeeping.lastTransformResult);
}

static void test_SaturateFlag(void)
{
    setUp();
    test_ctx.value = 500;
    test_ctx.flags = SAMPLE_FLAG_SATURATE;

    sample_Transform(&test_ctx);

    Assert_Equals(SAMPLE_SATURATION_MAX, sample_housekeeping.lastTransformResult);
}

static void test_NegateAndSaturate(void)
{
    setUp();
    test_ctx.value = 500;
    test_ctx.flags = SAMPLE_FLAG_NEGATE | SAMPLE_FLAG_SATURATE;

    sample_Transform(&test_ctx);

    Assert_Equals(-SAMPLE_SATURATION_MAX, sample_housekeeping.lastTransformResult);
}

static void test_NoFlagsBelowSaturation(void)
{
    setUp();
    test_ctx.value = 100;
    test_ctx.flags = SAMPLE_FLAG_SATURATE;

    sample_Transform(&test_ctx);

    Assert_Equals(300, sample_housekeeping.lastTransformResult);
}

static void test_ZeroValue(void)
{
    setUp();
    test_ctx.value = 0;

    sample_Transform(&test_ctx);

    Assert_Equals(0, sample_housekeeping.lastTransformResult);
}

static void test_IncrementsCount(void)
{
    setUp();
    test_ctx.value = 1;

    sample_Transform(&test_ctx);

    Assert_Equals(1, sample_housekeeping.transformCount);
}

static void test_IncrementsCountEachCall(void)
{
    setUp();
    test_ctx.value = 1;

    sample_Transform(&test_ctx);
    sample_Transform(&test_ctx);

    Assert_Equals(2, sample_housekeeping.transformCount);
}

int main(int argc, char **argv)
{
    Assert_Init();

    test_ScalesValueByFactor();
    test_NegateFlag();
    test_SaturateFlag();
    test_NegateAndSaturate();
    test_NoFlagsBelowSaturation();
    test_ZeroValue();
    test_IncrementsCount();
    test_IncrementsCountEachCall();

    Assert_Save();
    return 0;
}
