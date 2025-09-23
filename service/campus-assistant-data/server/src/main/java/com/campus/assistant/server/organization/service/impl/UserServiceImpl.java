package com.campus.assistant.server.organization.service.impl;

import cn.hutool.captcha.CaptchaUtil;
import cn.hutool.captcha.LineCaptcha;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.campus.assistant.server.organization.entity.Login;
import com.campus.assistant.server.organization.entity.User;
import com.campus.assistant.server.organization.entity.UserDefinition;
import com.campus.assistant.server.organization.mapper.UserMapper;
import com.campus.assistant.server.organization.service.IUserService;
import com.campus.assistant.server.utils.Base64Example;
import com.tangguangdi.base.common.entity.web.Result;
import com.tangguangdi.base.common.util.UUIDGenerator;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.bcrypt.BCrypt;
import org.springframework.stereotype.Service;
import org.springframework.util.ObjectUtils;

import javax.annotation.Resource;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.concurrent.TimeUnit;

/**
 * <p>
 * 用户信息 服务实现类
 * </p>
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements IUserService {

    @Resource
    private RedisTemplate redisTemplate;

    final String cookieName = "cookie";

    final String key = "campus:verification:";

    final String userKey = "campus:token:";

    @Override
    public void pictureCode(Cookie[] cookies, HttpServletResponse response) {
        try {
            LineCaptcha lineCaptcha = CaptchaUtil.createLineCaptcha(100, 40, 4, 20);
            String code = findCookie(cookies);
            if (code == null) {
                code = UUIDGenerator.getUUID();
                Cookie cookie = new Cookie(cookieName, code);
                response.addCookie(cookie);
            }
            redisTemplate.opsForValue().set(key.concat(code), lineCaptcha.getCode(), 60, TimeUnit.SECONDS);
            response.setContentType("image/png");
            response.setHeader("Pragma", "No-cache");
            response.setHeader("Cache-Control", "no-cache");
            lineCaptcha.write(response.getOutputStream());
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private String findCookie(Cookie[] cookies) {
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if (cookie.getName().equals(cookieName)) {
                    return cookie.getValue();
                }
            }
        }
        return null;
    }

    @Override
    public Result<?> login(Cookie[] cookies, Login login) {
        String cookie = findCookie(cookies);
        String code = login.getCode();
        String phone = login.getPhone();
        String password = login.getPassword();
        // 解密password
        password = Base64Example.decode(password);

        if (cookie != null && redisTemplate.hasKey(key.concat(cookie))) {
            if (!redisTemplate.opsForValue().get(key.concat(cookie)).equals(code)) {
                return new Result<>().setMsg("登录失败：验证码错误！");
            }
            QueryWrapper<User> queryWrapper = new QueryWrapper<>();
            queryWrapper.lambda()
                    .eq(User::getPhone, phone);
            User one = this.getOne(queryWrapper);
            if (ObjectUtils.isEmpty(one)) {
                return new Result<>().setMsg("该账号不存在！");
            }
            if (BCrypt.checkpw(password, one.getPassword())) {
                UserDefinition userRegister = new UserDefinition();
                userRegister.setId(one.getId());
                userRegister.setUrls(Arrays.asList(new String[]{"/**/*"}));
                userRegister.setToken(UUIDGenerator.getUUID());
                userRegister.setCrateTime(LocalDateTime.now());
                String key = userKey.concat(userRegister.getToken());
                this.redisTemplate.opsForValue().set(key, userRegister, userRegister.getExpiryTime(), TimeUnit.SECONDS);
                return new Result<String>()
                        .setSuccess(true)
                        .setObj(userRegister.getToken())
                        .setMsg("登录成功：欢迎进入系统！");
            }
            return new Result<>().setMsg("登录失败：用户名密码错误！");
        }
        return new Result<>().setMsg("登录失败：无效验证码！");
    }

    @Override
    public void logout(String token) {
        this.unregisterUser(token);
    }

    private void unregisterUser(String token) {
        String key = userKey.concat(token);
        if (redisTemplate.hasKey(key)) {
            redisTemplate.delete(key);
        }

    }
}
