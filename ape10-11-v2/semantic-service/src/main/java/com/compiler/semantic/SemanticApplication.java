package com.compiler.semantic;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class SemanticApplication {
    public static void main(String[] args) {
        SpringApplication.run(SemanticApplication.class, args);
    }
}
