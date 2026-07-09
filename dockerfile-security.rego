package main

#
# Do Not Store Secrets in ENV Variables
#

secrets_env = [
    "passwd",
    "password",
    "pass",
    "secret",
    "key",
    "access",
    "api_key",
    "apikey",
    "token",
    "tkn",
]

deny contains msg if {
    input[i].Cmd == "env"
    val := input[i].Value
    contains(lower(val[_]), secrets_env[_])

    msg := sprintf(
        "Line %d: Potential secret in ENV key found: %s",
        [i, val],
    )
}

#
# Only Use Trusted Base Images
#

deny contains msg if {
    input[i].Cmd == "from"

    val := split(input[i].Value[0], "/")
    count(val) > 1

    msg := sprintf(
        "Line %d: Use a trusted base image",
        [i],
    )
}

#
# Do Not Use 'latest' Tag
#

deny contains msg if {
    input[i].Cmd == "from"

    val := split(input[i].Value[0], ":")
    contains(lower(val[1]), "latest")

    msg := sprintf(
        "Line %d: Do not use 'latest' tag for base images",
        [i],
    )
}

#
# Avoid Curl Bashing
#

deny contains msg if {
    input[i].Cmd == "run"

    val := concat(" ", input[i].Value)

    matches := regex.find_n(
        "(curl|wget)[^|^>]*[|>]",
        lower(val),
        -1,
    )

    count(matches) > 0

    msg := sprintf(
        "Line %d: Avoid curl bashing",
        [i],
    )
}

#
# Do Not Upgrade System Packages
#

warn contains msg if {
    input[i].Cmd == "run"

    val := concat(" ", input[i].Value)

    matches := regex.match(
        ".*?(apk|yum|dnf|apt|pip).+?(install|[dist-|check-|group]?up[grade|date]).*",
        lower(val),
    )

    matches == true

    msg := sprintf(
        "Line %d: Do not upgrade your system packages: %s",
        [i, val],
    )
}

#
# Prefer COPY over ADD
#

deny contains msg if {
    input[i].Cmd == "add"

    msg := sprintf(
        "Line %d: Use COPY instead of ADD",
        [i],
    )
}

#
# USER Checks
#

any_user if {
    input[i].Cmd == "user"
}

deny contains msg if {
    not any_user

    msg := "Do not run as root. Use the USER instruction."
}

forbidden_users = [
    "root",
    "toor",
    "0",
]

deny contains msg if {
    input[i].Cmd == "user"

    user_value := input[i].Value[0]
    lower(user_value) in forbidden_users

    msg := sprintf(
        "Line %d: USER directive (USER %s) is forbidden",
        [i, user_value],
    )
}

#
# Do Not Use sudo
#

deny contains msg if {
    input[i].Cmd == "run"

    val := concat(" ", input[i].Value)
    contains(lower(val), "sudo")

    msg := sprintf(
        "Line %d: Do not use 'sudo' command",
        [i],
    )
}

#
# Multi-stage Build Check
#

default multi_stage = false

multi_stage = true if {
    input[i].Cmd == "copy"

    flags := concat(" ", input[i].Flags)
    contains(lower(flags), "--from=")
}

deny contains msg if {
    multi_stage == false

    msg := "COPY is used, but no multi-stage build was detected. Consider using COPY --from=<stage>."
}