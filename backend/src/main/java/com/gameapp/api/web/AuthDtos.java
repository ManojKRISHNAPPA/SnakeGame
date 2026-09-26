package com.gameapp.api.web;

import com.gameapp.api.model.User;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public final class AuthDtos {
    private AuthDtos() { }

    public record RegisterRequest(
        @NotBlank @Size(min = 3, max = 50) String username,
        @NotBlank @Email @Size(max = 100) String email,
        @NotBlank @Size(min = 6, max = 128) String password,
        @NotBlank String confirmPassword,
        @Size(max = 50) String firstName,
        @Size(max = 50) String lastName) { }

    public record LoginRequest(@NotBlank String username, @NotBlank String password) { }

    public record UserResponse(String username, String email, String displayName) {
        public static UserResponse from(User user) {
            return new UserResponse(user.getUsername(), user.getEmail(), user.getDisplayName());
        }
    }
}