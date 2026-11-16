package io.github.lakwan194.telco.selfcare

import kotlin.math.absoluteValue

/**
 * Formats an amount held in cents as Sri Lankan rupees, for example `Rs 1,234.50`.
 *
 * Amounts stay in whole cents (a [Long]) everywhere else in the app, so no floating-point
 * rounding can creep in; this is the only place they become text.
 */
fun formatRupees(cents: Long): String {
    val sign = if (cents < 0) "-" else ""
    val absolute = cents.absoluteValue
    val rupees = (absolute / 100).toString().reversed().chunked(3).joinToString(",").reversed()
    val remainder = (absolute % 100).toString().padStart(2, '0')
    return "${sign}Rs $rupees.$remainder"
}
