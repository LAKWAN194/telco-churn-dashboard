package io.github.lakwan194.telco.ussd;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

/** Starts a throwaway Redis for integration tests and points Spring Data Redis at it. */
@TestConfiguration(proxyBeanMethods = false)
public class TestcontainersConfiguration {

    /** Keep this in step with the image in the repository's docker-compose.yml. */
    static final DockerImageName REDIS = DockerImageName.parse("redis:8.8-alpine");

    @Bean
    @ServiceConnection(name = "redis")
    GenericContainer<?> redis() {
        return new GenericContainer<>(REDIS).withExposedPorts(6379);
    }
}
