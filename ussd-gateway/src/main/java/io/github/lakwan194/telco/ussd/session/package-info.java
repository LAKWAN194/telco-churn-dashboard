/**
 * USSD session state in Redis, keyed by session ID, with a time-to-live so abandoned sessions
 * disappear on their own.
 *
 * <p>Week 2. What is stored, and for how long, is ADR-003.
 */
package io.github.lakwan194.telco.ussd.session;
