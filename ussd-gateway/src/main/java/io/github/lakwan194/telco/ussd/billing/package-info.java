/**
 * Mock carrier billing ("charging as a service") for bundle purchases: a direct debit with an
 * external transaction ID that makes retries safe.
 *
 * <p>Week 4. The same idempotency ideas as the payment switch project.
 */
package io.github.lakwan194.telco.ussd.billing;
