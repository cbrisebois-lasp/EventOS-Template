/**
 * @file sample/Sample.h
 * @brief Public interface for the sample service.
 */

#pragma once

#include <stdint.h>

/**
 * @brief Context for the Increment action.
 */
typedef struct {
    uint32_t amount;
} sample_incrementCtx_t;

/**
 * @brief Context for the Transform action.
 */
typedef struct {
    uint8_t  id;
    uint16_t value;
    uint8_t  flags;
} sample_transformCtx_t;

/**
 * @brief Initialize the sample service.
 *
 * Zeros all module-level state.
 */
void sample_Init(void);

/**
 * @brief Increment the running total by the amount in the context.
 * @param context Pointer to a sample_incrementCtx_t.
 */
void sample_Increment(void *context);

/**
 * @brief Transform the context and record the result.
 * @param context Pointer to a sample_transformCtx_t.
 */
void sample_Transform(void *context);
