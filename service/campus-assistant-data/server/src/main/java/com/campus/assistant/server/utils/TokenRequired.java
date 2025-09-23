package com.campus.assistant.server.utils;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target(ElementType.METHOD) // 该注解可以用于方法上
@Retention(RetentionPolicy.RUNTIME) // 注解在运行时有效
public @interface TokenRequired {
}
