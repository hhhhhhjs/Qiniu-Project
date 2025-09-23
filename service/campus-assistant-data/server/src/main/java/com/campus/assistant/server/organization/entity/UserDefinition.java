package com.campus.assistant.server.organization.entity;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Data
public class UserDefinition {
    private Long id;
    private String token;
    private LocalDateTime crateTime;
    private Long expiryTime = 86400L;
    private String remoteAddr;
    private List<String> urls = new ArrayList();
}
