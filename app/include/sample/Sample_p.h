/**
 * @file sample/Sample_p.h
 * @brief Private definitions for the sample service.
 */

#pragma once

#include "sample/Sample.h"

#define SAMPLE_TRANSFORM_SCALE (3)
#define SAMPLE_FLAG_NEGATE     (0x01)
#define SAMPLE_FLAG_SATURATE   (0x02)
#define SAMPLE_SATURATION_MAX  (1000)

/**
 * @brief Housekeeping counters maintained by the sample service.
 */
typedef struct {
    uint32_t incrementCount;
    uint32_t transformCount;
    uint32_t total;
    int32_t  lastTransformResult;
} sample_housekeeping_t;
