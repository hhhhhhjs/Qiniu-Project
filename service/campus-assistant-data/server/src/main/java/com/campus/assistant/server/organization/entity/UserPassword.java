package com.campus.assistant.server.organization.entity;

import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

@Data
public class UserPassword {
    @ApiModelProperty(value = "旧登录密码")
    private String oldPassword;
    @ApiModelProperty(value = "新登录密码")
    private String newPassword;
}
