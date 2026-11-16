/**
 * The self-care USSD menu as a finite-state machine: which screen a session is on, what each keypress
 * does, and when the session ends.
 *
 * <p>This is the project's <b>kernel</b>. Keep it free of Spring, Redis and I/O, so it can be
 * unit-tested as pure logic and drawn on a whiteboard; {@code KernelIsolationTest} enforces that.
 * Design it in {@code docs/retention-loop/design/ussd-menu.md} first.
 */
package io.github.lakwan194.telco.ussd.menu;
