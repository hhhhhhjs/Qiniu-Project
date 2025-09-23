package com.campus.assistant.server.organization.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.campus.assistant.server.organization.entity.Login;
import com.campus.assistant.server.organization.entity.User;
import com.tangguangdi.base.common.entity.web.Result;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletResponse;

/**
 * <p>
 * 用户信息 服务类
 * </p>
 */
public interface IUserService extends IService<User> {

    void pictureCode(Cookie[] cookies, HttpServletResponse response);

    Result<?> login(Cookie[] cookies, Login login);

    void logout(String token);
}
