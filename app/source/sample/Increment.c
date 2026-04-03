/**
 * @file sample/Increment.c
 * @brief Action to increment the running total.
 */

#include "sample/Sample_p.h"

extern sample_housekeeping_t sample_housekeeping;

void sample_Increment(void *context)
{
    sample_incrementCtx_t *ctx = (sample_incrementCtx_t *)context;

    sample_housekeeping.total += ctx->amount;
    sample_housekeeping.incrementCount++;
}
