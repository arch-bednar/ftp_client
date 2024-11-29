import socket
from logging import raiseExceptions
from sys import argv
from urllib.parse import urlparse
import readchar
import threading
import os  # <<<====== for os.linesep (CR+LF)
import ftp_exceptions
from ftp_exceptions import NumberOfParameters, InvalidUrl, InvalidCommand, InvalidUser
import time


class ClientFtp:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._port = 21
        self._event = threading.Event()
        self._sep = "\r\n"
        self._restricted_commands = {"cp": ["-u", "-o", "-p", "-s", "-d"],
                                     "mkdir": ["-u", "-o", "-p"],
                                     "rmdir": ["-u", "-o", "-p"],
                                     "rm": ["-u", "-o", "-p"],
                                     "mv": ["-u", "-o", "-p", "-s", "-d"],
                                     "ls": []}

    def _command_validation(self, argv: list) -> dict:
        # print(argv[1])
        # print(len(argv[1:]))
        restr_command = self._restricted_commands.keys()
        command = argv[1]
        arguments = dict()  #return list of parameters

        if command in ("cp", "mv") and len(argv[1:]) == 3:
            arguments["mode"] = "1"
            if self._verify_url(argv[3], arguments["mode"], arguments) == 1:
                self._print_help_for_command(command)
                raise InvalidUrl(-20009, argv[3])
            else:
                arguments["command"] = command
                arguments["mode"] = "1"
                arguments["-s"] = argv[2]
                # arguments["-d"] = argv[3]
                print("OK")
                return arguments
        elif command in ("rm", "mkdir", "rmdir") and len(argv[1:]) == 2:
            arguments["mode"] = "1"
            if self._verify_url(argv[2], arguments["mode"], arguments) == 1:
                self._print_help_for_command(command)
                raise InvalidUrl(-20009, argv[2])
            else:
                arguments["command"] = command
                # arguments["param1"] = argv[2]
                print("OK")
                return arguments
        else:
            arguments["mode"] = "2"
            options = dict()
            border = len(argv)
            if argv[1] not in restr_command:
                raise InvalidCommand(command)

            index = 2
            last_value = str()
            if argv[1] in ("mkdir", "rmdir", "rm"):
                last_value = argv[border - 1]
                border -= 1

            while index < border:
                if argv[index] not in self._restricted_commands[argv[1]]:
                    print("Not known option \"{}\" for command \"{}\"".format(argv[index], argv[1]))
                    return dict()
                else:
                    try:
                        options[argv[index]] = argv[index + 1]
                    except IndexError:
                        print("Wrong number od arguments")
                        return dict()
                index += 2

            options_keys = options.keys()
            # command_params = self._restricted_commands[argv[1]].keys()
            command_params = self._restricted_commands[argv[1]]

            if options_keys != command_params:
                print("Invalid usage - missing parameters: ",
                      [param for param in command_params if param not in options_keys])
                self._print_help_for_command(command)

            print(options["-u"])
            # if self._verify_user(options["-u"]) == 1:
            #     raise InvalidUser()

            if last_value != "":
                if self._verify_url(last_value, arguments["mode"]) == 1:
                    self._print_help_for_command(command)
                    raise InvalidUrl(-20009, last_value)
                options["-d"] = last_value
            print(options)

            arguments.update(options)
            arguments["command"] = command
            print("_command_validation: OK")

            return arguments

    def _verify_url(self, adrr_url: str, mode: str, arguments: dict = None) -> int:
        interpret = urlparse(adrr_url)  # we take final destination for moving or copying
        if interpret.scheme != "ftp":
            print("Wrong scheme passed! {} is given, but {} required", interpret.scheme, "ftp")
            return 1
        if not interpret.path.strip():
            print("Wrong path passed! Path cannot be empty")
            return 1

        # region: weryfikacja linku

        if mode == "2":
            return 0

        url = interpret.netloc
        user = url[:url.find(":")]
        # if self._verify_user(user) == 1:
        #     return 1
        password = url[url.find(":") + 1:url.find("@")]

        temp_addr_port = url[url.find("@") + 1:]
        address = temp_addr_port[:temp_addr_port.find(":")]
        port = temp_addr_port[temp_addr_port.find(":") + 1:]
        concat_url = user + ":" + password + "@" + address + ":" + port

        if concat_url != url:
            print(url)
            print(concat_url)
            print("Invalid url! Expected syntax: <user>:<password>@<address>:<port>")
            return 1

        arguments["-u"] = user
        arguments["-p"] = password
        arguments["-o"] = port
        arguments["-d"] = interpret.scheme + "://" + address + interpret.path
        return 0

    def _verify_user(self, user: str) -> int:
        for char in user:
            c = ord(char)
            print(c)
            if c not in range(65, 90 + 1) or c not in range(61, 122 + 1) or c not in (45, 95):
                print(f"User \"{user}\"contains illegal characters")
                return 1
        return 0

    def _print_help_for_command(self, command):
        if command in ("cp", "mv"):
            print(f"Syntax for command {command}")
            print(f"{command} -u <user> -p <password> -o <port> <absolute_path_from> <absolute_path_to>")
            print("---or---")
            print(f"{command} <link_path_from> <link_path_to")
            print("format for <absolute_path_to>: ftp://absolute/path/to/file_or_directory")

            print("format for <link_path_to>: ", end="")
            print("ftp://<user>:<password>@<server_address>/absolute/path/to/file_or_directory")
        elif command == "mkdir":
            print(f"Syntax for command {command}")
            print(f"{command} -u <user> -p <password> -o <port> <absolute_path_to_create_directory>")
            print("---or---")
            print(f"{command} <absolute_path_to")
            print("format for <absolute_path_to>: ftp://<user>:<password>@<server_address>/path/for/directory")
        elif command == "rmdir":
            print(f"Syntax for command {command}")
            print(f"{command} -u <user> -p <password> -o <port> <absolute_path_to_delete_directory>")
            print("---or---")
            print(f"{command} <absolute_path_to")
            print("format for <absolute_path_to>: ftp://<user>:<password>@<server_address>/path/to/directory")
        elif command == "rm":
            print(f"Syntax for command {command}")
            print(f"{command} -u <user> -p <password> -o <port> <absolute_path_to_delete_file>")
            print("---or---")
            print(f"{command} <absolute_path_to>")
            print("format for <absolute_path_to>: ftp://<user>:<password>@<server_address>/path/to/file")

    def _calculate_port(self, hex1: str, hex2: str) -> int:
        try:
            port = int(hex1) * 16 + int(hex2)
            return port
        except ValueError as e:
            print(e)

    def _execute_command(self, args: dict):
        data = bytes()
        data = self._socket.recv(1024)

        command = args["command"]
        if command == "cp":
            send = self._add_sep("USER " + args["-u"])
            send = self._add_sep("PASS " + args["-p"])
            send = self._add_sep("PASV")
            send = self._add_sep("LIST")
            pass
        elif command == "mv":
            send = self._add_sep("USER " + args["-u"])
            send = self._add_sep("PASS " + args["-p"])
        elif command == "mkdir":
            send = self._add_sep("USER " + args["-u"])
            send = self._add_sep("PASS " + args["-p"])
        elif command == "rmdir":
            send = self._add_sep("USER " + args["-u"])
            send = self._add_sep("PASS " + args["-p"])
        elif command == "rm":
            send = self._add_sep("USER " + args["-u"])
            send = self._add_sep("PASS " + args["-p"])

    def _cut_status_code(self, buffer: bytes) -> str:
        return str(buffer)[:3]

    def _add_sep(self, string: str) -> str:
        return string + chr(13) + chr(10)

    def _connect_pasv(self, data: bytearray):
        line = data.decode("utf-8")
        address = line[line.find("(") + 1:line.find(")")].split(",")
        port = self._calculate_port(address[-2], address[-1])
        pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pasv_socket.connect((address, port))

    def _listen(self):
        print(self._event.is_set())
        while self._event.is_set():
            print("Listening...")
            try:
                data = self._socket.recv(1024)
                if not data:
                    break
                print(data.decode("utf-8"))
            except BrokenPipeError:
                self._event.clear()
                print("Connection is broken")

    def start(self, argv: list):
        localhost = "127.0.0.1"
        address = None
        port = None
        thread = None
        print(">>>>>>>>")
        param = self._command_validation(argv)
        print(param)
        address = urlparse(param["-d"]).netloc
        port = param["-o"]
        print("param - port" + port)
        print(type(port))
        print("++++++++ print param")
        print(param)
        print("========")
        # return

        choice = ""
        # while choice not in ('y', 'Y', 'n', 'N'):
        #     print("Do you want to use localhost to connect with port 21, or enter your destination? [y/N]: ", end="")
        #     choice = readchar.readchar()
        #     print("")
        #
        # if choice in ('y', 'Y'):
        #     address = input("Server address: ")
        #     port = input("Port: ")

        if len(argv) < 2:
            print("Not enough parameters")
            return

        # if choice in ('y', 'Y'):
        #     self._socket.connect((address, port))
        # else:
        #     self._socket.connect((localhost, 21))
        self._socket.connect((address, int(port)))
        # self._event.set()
        # self._socket.setblocking(False)
        # thread = threading.Thread(target=self._listen, args=())
        # thread.start()
        time.sleep(3)

        try:
            # while self._event.is_set():
            #     line = input("#> ")
            print("execute param")
            self._execute_command(param)
        except KeyboardInterrupt:
            print("Caught an exception")
            self._socket.close()
            self._event.clear()

        #self._command_validation(argv)
        #self._socket.connect((localhost, self._port))


if __name__ == "__main__":
    ftp = ClientFtp()
    print("start")
    ftp.start(argv)
