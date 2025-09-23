package com.campus.assistant.server.organization.controller;


import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.campus.assistant.server.organization.entity.Login;
import com.campus.assistant.server.organization.entity.User;
import com.campus.assistant.server.organization.entity.UserPassword;
import com.campus.assistant.server.organization.service.IUserService;
import com.campus.assistant.server.utils.Base64Example;
import com.campus.assistant.server.utils.TokenRequired;
import com.tangguangdi.base.common.entity.web.Result;
import com.tangguangdi.base.common.enums.register.PermissionRule;
import com.tangguangdi.base.common.variable.MAX;
import com.tangguangdi.base.core.annotation.Permission;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import org.springframework.security.crypto.bcrypt.BCrypt;
import org.springframework.util.ObjectUtils;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.List;

/**
 * <p>
 * 用户信息 前端控制器
 * </p>
 */
@RestController
@RequestMapping("organization/user")
@Api(tags = {"用户信息"})
public class UserController {

    @Resource
    private IUserService userService;

    /**
     * 用户信息列表
     */
    @TokenRequired
    @GetMapping("list")
    @ApiOperation("用户信息列表")
    @Permission(rule = PermissionRule.None)
    public Result<List<User>> list() {
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        return new Result<List<User>>()
                .setSuccess(true)
                .setObj(userService.list(wrapper));
    }

    /**
     * 用户信息
     */
    @TokenRequired
    @GetMapping("userInfo")
    @ApiOperation("用户信息")
    @Permission(rule = PermissionRule.None)
    public Result<?> userInfo(@RequestParam Long userId) {
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.lambda().eq(User::getId, userId);
        User one = userService.getOne(wrapper);
        return new Result<>().setSuccess(true).setObj(one);
    }

    /**
     * 用户信息分页
     */
    @TokenRequired
    @GetMapping
    @ApiOperation("用户信息分页")
    @Permission(rule = PermissionRule.None)
    public Result<Page<User>> page(@RequestParam Integer current, @RequestParam Integer size) {
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        return new Result<Page<User>>()
                .setSuccess(true)
                .setObj(userService.page(new Page<>(current, size), wrapper));
    }

    /**
     * 用户信息新增
     */
//    @TokenRequired
    @PostMapping
    @ApiOperation("用户信息新增")
    @Permission(rule = PermissionRule.None)
    public Result<?> save(@RequestBody User user) {
        String phone = user.getPhone();
        // 手机号唯一性校验，只校验该企业下的
        QueryWrapper<User> wrapper = new QueryWrapper<>();
        wrapper.lambda().eq(User::getPhone, phone);
        User one = userService.getOne(wrapper);
        if (!ObjectUtils.isEmpty(one)) {
            return new Result<>().setMsg("该手机已存在！");
        }
        String password = user.getPassword();
        // 解密password
        password = Base64Example.decode(password);
        user.setId(null);
        user.setPassword(BCrypt.hashpw(password, BCrypt.gensalt()));
        return new Result<>()
                .setSuccess(userService.save(user));
    }


    /**
     * 用户信息删除
     */
    @TokenRequired
    @DeleteMapping("{id}")
    @ApiOperation("用户信息删除")
    @Permission(rule = PermissionRule.None)
    public Result<?> removeById(@PathVariable Long id) {
        return new Result<>()
                .setSuccess(userService.removeById(id));
    }

    /**
     * 用户信息修改
     */
    @TokenRequired
    @PutMapping("updateUser")
    @ApiOperation("用户信息修改")
    @Permission(rule = PermissionRule.None)
    public Result<?> updateById(@RequestBody User user) {
        user.setPassword(null);
        return new Result<>()
                .setSuccess(userService.updateById(user));
    }

    /**
     * 用户密码修改
     */
    @TokenRequired
    @PutMapping("password/{id}")
    @ApiOperation("用户密码修改")
    @Permission(rule = PermissionRule.None)
    public Result<?> updateById(@PathVariable Long id, @RequestBody UserPassword userPassword) {
        User user = userService.getById(id);
        // 判断旧密码是否正确
        String oldPassword = userPassword.getOldPassword();
        // 解密Password
        oldPassword = Base64Example.decode(oldPassword);
        String newPassword = userPassword.getNewPassword();
        newPassword = Base64Example.decode(newPassword);

        if (!BCrypt.checkpw(oldPassword, user.getPassword())) {
            return new Result<>().setMsg("旧密码不正确！");
        }
        user.setPassword(BCrypt.hashpw(newPassword, BCrypt.gensalt()));
        userService.updateById(user);
        return new Result<>().setSuccess(true).setMsg("密码重置成功");
    }

    /**
     * 用户密码重置
     */
    @TokenRequired
    @PutMapping("reset/{id}")
    @ApiOperation("用户密码重置")
    @Permission(rule = PermissionRule.None)
    public Result<?> reset(@PathVariable Long id) {
        User user = userService.getById(id);
        String phone = user.getPhone();
        String substring = phone.substring(phone.length() - 6);

        user.setPassword(BCrypt.hashpw(substring, BCrypt.gensalt()));
        userService.updateById(user);
        return new Result<>().setSuccess(true).setMsg("密码重置成功");
    }

    /**
     * 系统图片验证码
     */
    @GetMapping("pictureCode")
    @ApiOperation("图片验证码")
    @Permission(rule = PermissionRule.None)
    public void pictureCode(HttpServletRequest request, HttpServletResponse response) {
        userService.pictureCode(request.getCookies(), response);
    }

    /**
     * 系统用户登录
     */
    @PostMapping("login")
    @ApiOperation("用户登录")
    @Permission(rule = PermissionRule.None)
    public Result<?> login(HttpServletRequest request, @RequestBody Login login) {
        return userService.login(request.getCookies(), login);
    }

    /**
     * 系统用户登出
     */
    @TokenRequired
    @DeleteMapping
    @ApiOperation("用户登出")
    @Permission(rule = PermissionRule.None)
    public Result<?> logout(@RequestHeader(MAX.TOKEN) String token) {
        userService.logout(token);
        return new Result<>().setSuccess(true);
    }
}
