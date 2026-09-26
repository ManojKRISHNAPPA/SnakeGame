package com.gameapp.api.service;

import com.gameapp.api.model.User;
import com.gameapp.api.repository.UserRepository;
import com.gameapp.api.web.AuthDtos.RegisterRequest;
import java.time.LocalDateTime;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional
public class UserService implements UserDetailsService {
    private final UserRepository users;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository users, PasswordEncoder passwordEncoder) {
        this.users = users;
        this.passwordEncoder = passwordEncoder;
    }

    public User register(RegisterRequest request) {
        String username = request.username().trim();
        String email = request.email().trim().toLowerCase();
        if (!request.password().equals(request.confirmPassword())) throw new IllegalArgumentException("Passwords do not match.");
        if (users.existsByUsername(username)) throw new IllegalArgumentException("Username is already taken.");
        if (users.existsByEmail(email)) throw new IllegalArgumentException("Email is already registered.");
        User user = new User();
        user.setUsername(username);
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(request.password()));
        user.setFirstName(normalizeName(request.firstName()));
        user.setLastName(normalizeName(request.lastName()));
        return users.save(user);
    }

    @Transactional(readOnly = true)
    @Override
    public UserDetails loadUserByUsername(String username) {
        User user = findByUsername(username);
        return org.springframework.security.core.userdetails.User.withUsername(user.getUsername())
            .password(user.getPassword()).roles("USER").build();
    }

    public User findByUsername(String username) {
        return users.findByUsername(username).orElseThrow(() -> new UsernameNotFoundException("User not found."));
    }

    public void recordLogin(String username) {
        User user = findByUsername(username);
        user.setLastLogin(LocalDateTime.now());
    }

    @Transactional(readOnly = true)
    public long count() { return users.count(); }

    private String normalizeName(String name) {
        return name == null || name.isBlank() ? null : name.trim();
    }
}