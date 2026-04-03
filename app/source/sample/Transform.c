/**
 * @file sample/Transform.c
 * @brief Action to transform a context value and record the result.
 */

#include "sample/Sample_p.h"

extern sample_housekeeping_t sample_housekeeping;

void sample_Transform(void *context)
{
    sample_transformCtx_t *ctx = (sample_transformCtx_t *)context;

    int32_t result = (int32_t)ctx->value * SAMPLE_TRANSFORM_SCALE;

    if (ctx->flags & SAMPLE_FLAG_NEGATE) {
        result = -result;
    }

    if (ctx->flags & SAMPLE_FLAG_SATURATE) {
        if (result > SAMPLE_SATURATION_MAX) {
            result = SAMPLE_SATURATION_MAX;
        } else if (result < -SAMPLE_SATURATION_MAX) {
            result = -SAMPLE_SATURATION_MAX;
        }
    }

    sample_housekeeping.lastTransformResult = result;
    sample_housekeeping.transformCount++;
}
