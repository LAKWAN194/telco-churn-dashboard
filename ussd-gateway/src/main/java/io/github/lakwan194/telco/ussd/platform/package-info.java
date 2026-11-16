/**
 * The simulated operator platform, modelled on Ideamart's USSD and SMS APIs: it opens a session
 * when a phone dials the short code, forwards each keypress to the menu's callback, delivers
 * the screens the menu sends back, and expires idle sessions.
 *
 * <p>Week 2. The message shapes are summarised in {@code docs/retention-loop/domain/telco-apis.md}.
 */
package io.github.lakwan194.telco.ussd.platform;
