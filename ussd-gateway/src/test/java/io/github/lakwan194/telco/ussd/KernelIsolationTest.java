package io.github.lakwan194.telco.ussd;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;

/** Keeps the USSD menu state machine pure: no framework, Redis, reactive or web code inside it. */
@AnalyzeClasses(packages = "io.github.lakwan194.telco.ussd", importOptions = ImportOption.DoNotIncludeTests.class)
class KernelIsolationTest {

    @ArchTest
    static final ArchRule menuHasNoFrameworkDependencies = noClasses()
            .that().resideInAPackage("..ussd.menu..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "org.springframework..", "reactor..", "io.lettuce..", "org.reactivestreams..")
            .allowEmptyShould(true);

    @ArchTest
    static final ArchRule menuDependsOnNoOtherPackageInTheService = noClasses()
            .that().resideInAPackage("..ussd.menu..")
            .should().dependOnClassesThat().resideInAnyPackage(
                    "..ussd.platform..", "..ussd.session..", "..ussd.otp..", "..ussd.billing..")
            .allowEmptyShould(true);
}
