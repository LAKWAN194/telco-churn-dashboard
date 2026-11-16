package io.github.lakwan194.telco.ussd;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webtestclient.autoconfigure.AutoConfigureWebTestClient;
import org.springframework.context.annotation.Import;
import org.springframework.data.redis.core.ReactiveStringRedisTemplate;
import org.springframework.test.web.reactive.server.WebTestClient;
import reactor.test.StepVerifier;

/** Boots the gateway against a real Redis. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureWebTestClient
@Import(TestcontainersConfiguration.class)
class UssdGatewayApplicationIT {

    @Autowired
    WebTestClient web;

    @Autowired
    ReactiveStringRedisTemplate redis;

    @Test
    void reportsHealthyIncludingRedis() {
        web.get().uri("/actuator/health").exchange()
                .expectStatus().isOk()
                .expectBody().jsonPath("$.status").isEqualTo("UP");
    }

    @Test
    void exposesPrometheusMetrics() {
        web.get().uri("/actuator/prometheus").exchange()
                .expectStatus().isOk()
                .expectBody(String.class).value(body -> assertThat(body).contains("jvm_memory_used_bytes"));
    }

    @Test
    void redisKeysExpire() {
        // The session store relies on time-to-live; this proves the wiring, not your design.
        StepVerifier.create(redis.opsForValue().set("smoke:session", "screen-1", Duration.ofSeconds(30))
                        .then(redis.getExpire("smoke:session")))
                .assertNext(ttl -> assertThat(ttl).isPositive().isLessThanOrEqualTo(Duration.ofSeconds(30)))
                .verifyComplete();
    }
}
