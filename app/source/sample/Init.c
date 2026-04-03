/**
 * @file sample/Init.c
 * @brief Initialize the sample service state.
 */

#include "sample/Sample_p.h"

sample_housekeeping_t sample_housekeeping;

void sample_Init(void)
{
    sample_housekeeping.incrementCount = 0;
    sample_housekeeping.transformCount = 0;
    sample_housekeeping.total = 0;
    sample_housekeeping.lastTransformResult = 0;
}
