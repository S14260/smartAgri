package com.example.dormitoryadmin;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.web.client.RestTemplate;

//@EnableScheduling
@SpringBootApplication
public class DormitoryAdminApplication {

    public static void main(String[] args) {
        SpringApplication.run(DormitoryAdminApplication.class, args);
    }
    @Configuration
    public class AppConfig {
        @Bean
        public RestTemplate restTemplate() {
            return new RestTemplate();
        }
    }
}
