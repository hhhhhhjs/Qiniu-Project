package com.campus.assistant.api;


import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.stereotype.Component;

@FeignClient(name = "campus-assistant-data", fallback = CampusAssistantClient.FallBack.class)
public interface CampusAssistantClient {

    @Component
    class FallBack implements CampusAssistantClient {

    }
}
