package com.campus.assistant.server.utils;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

public class Base64Example {

    // 加密
    public static String encode(String plainText) {
        byte[] encodedBytes = Base64.getEncoder()
                .encode(plainText.getBytes(StandardCharsets.UTF_8));
        return new String(encodedBytes, StandardCharsets.UTF_8);
    }

    // 解密
    public static String decode(String encodedText) {
        byte[] decodedBytes = Base64.getDecoder()
                .decode(encodedText.getBytes(StandardCharsets.UTF_8));
        return new String(decodedBytes, StandardCharsets.UTF_8);
    }

    public static void main(String[] args) {
        String password = "123456";
        String encodedText = encode(password);
        System.out.println(encodedText);
    }
}
