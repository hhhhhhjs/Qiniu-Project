package com.campus.assistant.server.utils;

import com.campus.assistant.server.organization.entity.User;
import com.campus.assistant.server.organization.entity.UserDefinition;
import com.campus.assistant.server.organization.service.IUserService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Component;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.lang.reflect.Method;

@Component
@Slf4j
public class TokenInterceptor implements HandlerInterceptor {

    @Resource
    private RedisTemplate redisTemplate;
    @Resource
    private IUserService userService;

    final String userKey = "campus:token:";

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        try {
            // 判断handler是否是HandlerMethod的实例
            if (handler instanceof HandlerMethod) {
                HandlerMethod handlerMethod = (HandlerMethod) handler;
                Method method = handlerMethod.getMethod();

                // 检查方法上是否有@TokenRequired注解
                if (method.isAnnotationPresent(TokenRequired.class)) {
                    String token = request.getHeader("token");
                    if (isValidToken(response, token)) {
                        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED); // 401 Forbidden
                        response.getWriter().write("无效的token！");
                        return false;
                    }
                }
            }
            return true;
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR); // 500 Forbidden
            response.getWriter().write("服务器异常！");
            log.info(e.getMessage());
            return false;
        }
    }

    // 简单的token验证逻辑
    private boolean isValidToken(HttpServletResponse response, String token) throws Exception {
        // 这里可以对token进行一些处理，比如验证token的有效性
        if (token == null || token.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED); // 401 Unauthorized
            response.getWriter().write("token已失效！");
            return true;
        }

        Object object = redisTemplate.opsForValue().get(userKey + token);

        if (object instanceof UserDefinition) {
            UserDefinition userDefinition = (UserDefinition) object; // 强制类型转换
            Long id = userDefinition.getId();
            User byId = userService.getById(id);
            return byId == null;
        }
        return true;
    }
}