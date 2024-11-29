class NumberOfParameters(Exception):
    def __init__(self, command):
        super().__init__(f"Wrong number of parameters for command {command}.")


class InvalidUrl(Exception):
    def __init__(self, error_code, url):
        if error_code == -20009:
            super().__init__(f"InvalidUrl {error_code}:Invalid format for URL {url}.")
        elif error_code == -20010:
            super().__init__(f"InvalidUrl {error_code}Invalid path in URL {url}.")
        else:
            super().__init__(f"InvalidUrl {error_code}: undefined error code")


class InvalidCommand(Exception):
    def __init__(self, command):
        super().__init__(f"InvalidCommand: Command {command} not found.")


class InvalidOption(Exception):
    def __init__(self, command, option):
        super().__init__(f"InvalidOption: Invalid option {option} for command {command}.")


class InvalidUser(Exception):
    def __init__(self):
        super().__init__("InvalidUser: User contains illegal characters!")
