package com.campus.assistant.server.organization.entity;

import lombok.Data;

@Data
public class Login {
    private String code;
    private String phone;
    private String password;
}
