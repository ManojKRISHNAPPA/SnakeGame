package com.gameapp.api.web;

import com.gameapp.api.model.User;
import com.gameapp.api.service.UserService;
import java.util.Map;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {
    private final UserService users;
    public DashboardController(UserService users) { this.users = users; }

    @GetMapping
    Map<String, Object> dashboard(Authentication authentication) {
        User user = users.findByUsername(authentication.getName());
        return Map.of("user", AuthDtos.UserResponse.from(user), "totalUsers", users.count());
    }
}