package io.github.lakwan194.telco.selfcare

import org.junit.Assert.assertEquals
import org.junit.Test

class MoneyTest {

    @Test
    fun formatsRupeesWithThousandsSeparatorsAndCents() {
        assertEquals("Rs 1,234.50", formatRupees(123_450))
        assertEquals("Rs 1,000,000.00", formatRupees(100_000_000))
    }

    @Test
    fun formatsSmallAmountsAndZero() {
        assertEquals("Rs 0.00", formatRupees(0))
        assertEquals("Rs 0.05", formatRupees(5))
        assertEquals("Rs 999.99", formatRupees(99_999))
    }

    @Test
    fun formatsNegativeAmounts() {
        assertEquals("-Rs 49.00", formatRupees(-4_900))
    }
}
