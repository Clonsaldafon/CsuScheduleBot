class ErrorMessage:
    TOKEN_IS_EXPIRED = "token is expired"

    SIGN_UP_FULLNAME_VALIDATION = "Key: 'SignUpWithTelegramRequest.Fullname' Error:Field validation "\
                                  "for 'Fullname' failed on the 'required' tag"

    USER_ALREADY_EXISTS = "user already exists"
    USER_NOT_FOUND = "user not found"

    SIGN_UP_EMAIL_VALIDATION = "Key: 'SignUpRequest.Email' Error:Field validation" \
                               "for 'Email' failed on the 'email' tag"
    LOG_IN_EMAIL_VALIDATION = "Key: 'LogInRequest.Email' Error:Field validation "\
                              "for 'Email' failed on the 'email' tag"
    WRONG_PASSWORD = "wrong password"