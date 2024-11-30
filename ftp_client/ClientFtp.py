import socket
from sys import argv
from urllib.parse import urlparse
import os
from ftp_exceptions import NumberOfParameters, InvalidUrl, InvalidCommand, InvalidOption
import time


class ClientFtp:
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._port = 21
        self._sep = "\r\n"
        self._restricted_commands = {"cp": ["-u", "-o", "-p", "-s", "-d"],
                                     "mkdir": ["-u", "-o", "-p", "-d"],
                                     "rmdir": ["-u", "-o", "-p", "-d"],
                                     "rm": ["-u", "-o", "-p", "-d"],
                                     "mv": ["-u", "-o", "-p", "-s", "-d"],
                                     "ls": [],
                                     "wget": ["-u", "-o", "-p", "-s", "-d"]}

    def _command_validation(self, argv: list) -> dict:
        # print(argv[1])
        # print(len(argv[1:]))
        restr_command = self._restricted_commands.keys()
        command = argv[1]
        arguments = dict()  #return list of parameters
        arguments["command"] = command

        if command in ("cp", "mv") and len(argv[1:]) == 3:
            arguments["mode"] = "1"
            if self._verify_url(argv[3], arguments["mode"], arguments) == 1:
                self._print_help_for_command(command)
                raise InvalidUrl(-20009, argv[3])
            else:
                arguments["mode"] = "1"
                arguments["-s"] = argv[2]
                # arguments["-d"] = argv[3]
                print("OK")
                return arguments
        elif command == "wget" and len(argv[1:]) == 3:
            arguments["mode"] = "1"
            if self._verify_url(argv[2], arguments["mode"], arguments) == 1:
                self._print_help_for_command(command)
                raise InvalidUrl(-20009, argv[2])
            else:
                arguments["mode"] = "1"
                arguments["-s"] = argv[2]
                arguments["-d"] = argv[3]
                print("OK")
                return arguments
        elif command in ("rm", "mkdir", "rmdir") and len(argv[1:]) == 2:
            arguments["mode"] = "1"
            if self._verify_url(argv[2], arguments["mode"], arguments) == 1:
                self._print_help_for_command(command)
                raise InvalidUrl(-20009, argv[2])
            else:
                print("OK")
                return arguments
        else:
            arguments["mode"] = "2"
            options = dict()
            border = len(argv)
            if argv[1] not in restr_command:
                raise InvalidCommand(-20099, command)

            index = 2
            last_value = str()
            # if argv[1] in ("mkdir", "rmdir", "rm"):
            #     border -= 1

            while index < border:
                if argv[index] not in self._restricted_commands[argv[1]]:
                    raise InvalidOption(-20110, command, argv[index])
                    #print("-20110: Not known option \"{}\" for command \"{}\"".format(argv[index], argv[1]))
                    #return dict()
                else:
                    try:
                        options[argv[index]] = argv[index + 1]
                    except IndexError:
                        #raise Exception("-20111: Wrong number of arguments")
                        raise NumberOfParameters(-20111, command)
                index += 2

            options_keys = set(options.keys())
            # command_params = self._restricted_commands[argv[1]].keys()
            command_params = set(self._restricted_commands[argv[1]])
            print(",,,,,,,,,,,,,,,,,,")
            print(command_params)
            print(options_keys)
            if options_keys != command_params:
                try:
                    raise Exception("-20112: Invalid usage - missing parameters: ",
                          [param for param in command_params if param not in options_keys])
                finally:
                    self._print_help_for_command(command)

            arguments.update(options)
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
        if arguments["command"] == "wget":
            arguments["-s"] = interpret.scheme + "://" + address + interpret.path
            print("arguments[-s]")
            print(arguments["-s"])
        else:
            arguments["-d"] = interpret.scheme + "://" + address + interpret.path
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
            port = int(hex1) * 256 + int(hex2)
            return port
        except ValueError as e:
            print(e)

    def _send_cmd(self, cmd):
        self._socket.send(cmd.encode())

    def _get_data(self) -> str:
        print("_get_data")
        return self._socket.recv(1024).decode("utf-8")

    def _execute_command(self, args: dict):
        data = str()
        status_code = ""
        data = self._get_data()
        print(data)
        command = args["command"]
        if command == "cp":
            self._login(args["-u"], args["-p"])
            self._connect_pasv()
            self._configure_modes()
            self._copying_file(args["-s"], urlparse(args["-d"]).path)
        elif command == "mv":
            self._login(args["-u"], args["-p"])
            self._connect_pasv()
            self._configure_modes()
            self._moving_file(args["-s"], urlparse(args["-d"]).path)
        elif command == "mkdir":
            self._login(args["-u"], args["-p"])
            self._mkdir(urlparse(args["-d"]).path)
        elif command == "rmdir":
            self._login(args["-u"], args["-p"])
            self._rmdir(urlparse(args["-d"]).path)
        elif command == "rm":
            self._login(args["-u"], args["-p"])
            self._del_file(urlparse(args["-d"]).path)
        elif command == "ls":
            self._login(args["-u"], args["-p"])
            self._connect_pasv()
            self._list(urlparse(args["-d"]).path)
        elif command == "wget":
            self._login(args["-u"], args["-p"])
            self._connect_pasv()
            self._configure_modes()
            self._wget(urlparse(args["-s"]).path, args["-d"])

    def _cut_status_code(self, buffer: str) -> str:
        return buffer[:3]

    def _add_sep(self, string: str) -> str:
        return string + chr(13) + chr(10)

    def _login(self, user, password):
        send = self._add_sep("USER " + user)
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        status_code = self._cut_status_code(data)

        if not status_code.startswith("3"):
            self._socket.close()
            raise Exception(data)
        else:
            print(data)

        time.sleep(1)
        send = self._add_sep("PASS " + password)
        print(send)
        self._send_cmd(send)
        time.sleep(1)
        data = self._get_data()
        status_code = self._cut_status_code(data)

        if not status_code.startswith("2"):
            self._socket.close()
            raise Exception(data)
        else:
            print(data)

    def _connect_pasv(self):
        try:
            send = self._add_sep("PASV")
            print(send)
            self._send_cmd(send)
            data = self._get_data()
            print(data)
            status_code = self._cut_status_code(data)

            if status_code.startswith("5"):
                self._socket.close()
                raise Exception(data)

            address = data[data.find("(") + 1:data.find(")")].split(",")
            port = self._calculate_port(address[-2], address[-1])
            self._pasv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._pasv_socket.connect((address[-6] + "." + address[-5] + "." + address[-4] + "." + address[-3], port))
            print("PASV connected")
        except ConnectionError as e:
            print("connection error")
            self._socket.close()
            self._pasv_socket.close()
            print(e)
        finally:
            print("ending _connect_pasv")

    def _configure_modes(self):
        send = self._add_sep("TYPE I")
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        print(data)
        send = self._add_sep("MODE S")
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        print(data)
        send = self._add_sep("STRU F")
        self._send_cmd(send)
        data = self._get_data()
        print(data)

    def _copying_file(self, file, destination):
        try:
            f = open(file, "rb")
            try:
                file_name = file[file.rfind("/")+1:]
                send = self._add_sep(f"STOR {destination}/{file_name}")
                print(send)
                self._send_cmd(send)
                data = self._get_data()
                print(data)
                self._pasv_socket.sendfile(f)
                f.close()
                time.sleep(1)
                self._pasv_socket.close()
                data = self._get_data()
                print(data)
            except Exception as e:
                print(e)
                f.close()
        except Exception as e:
            raise Exception(e)


    def _moving_file(self, file, destination):
        self._copying_file(file, destination)
        os.remove(file)

    def _mkdir(self, directory):
        send = self._add_sep("MKD " + directory)
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        print(data)
        self._socket.close()

    def _rmdir(self, directory):
        send = self._add_sep("RMD " + directory)
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        print(data)
        self._socket.close()

    def _del_file(self, file):
        send = self._add_sep("DELE " + file)
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        print(data)
        self._socket.close()

    def _list(self, directory: str = str()):
        send = self._add_sep("LIST {}".format(directory))
        print(send)
        self._send_cmd(send)
        while True:
            data = self._pasv_socket.recv(1024)
            if not data:
                break
            print(data.decode("utf-8"))

        data = self._get_data()
        print(data)
        self._pasv_socket.close()
        self._socket.close()

    def _wget(self, file, destination):
        send = self._add_sep(f"RETR {file}")
        print(send)
        self._send_cmd(send)
        data = self._get_data()
        print(data)

        if destination.rfind('/') != len(destination)-1:
            destination += '/'

        destination = destination + file[file.rfind('/')+1:]

        with open(destination, "wb") as f:
            while True:
                data = self._pasv_socket.recv(1024)
                if not data:
                    break
                f.write(data)

        self._pasv_socket.close()
        data = self._get_data()
        print(data)
        self._socket.close()
    def start(self, argv: list):
        param = self._command_validation(argv)
        print(param)
        # return

        #param = {"command": "rmdir", "-u": "test", "-o": "21", "-p": "test", "-d": "ftp://127.0.0.1/folder_twojej_starej/3"}
        #param = {"command": "rm", "-u": "test", "-o": "21", "-p": "test", "-d": "ftp://127.0.0.1/folder_twojej_starej/family-guy-css.gif"}
        #param = {"command": "ls", "-u": "test", "-o": "21", "-p": "test", "-d": "ftp://127.0.0.1/folder_twojej_starej"}
        # param = {"command": "mv", "-u": "test", "-o": "21", "-p": "test",
        #          "-s": "/Users/Shared/pliczki/family-guy-css.gif",
        #          "-d": "ftp://127.0.0.1/folder"}
        # param = {"command": "mkdir", "-u": "test", "-o": "21", "-p": "test",
        #          "-d": "ftp://127.0.0.1/folder/3"}
        # param = {"command": "wget", "-u": "test", "-o": "21", "-p": "test",
        #          "-d": "/Users/Shared/pliczki/",
        #          "-s": "ftp://127.0.0.1/folder/family-guy-css.gif"}


        print(urlparse(param["-d"]).netloc, param["-o"])
        self._socket.connect((urlparse(param["-d"]).netloc, int(param["-o"])))
        time.sleep(3)

        try:
            print("execute param")
            self._execute_command(param)
        except (KeyboardInterrupt, BrokenPipeError) as e:
            self._socket.close()
            self._pasv_socket.close()
            print("Connection closed due to error: " + e)



if __name__ == "__main__":
    ftp = ClientFtp()
    print("start")
    ftp.start(argv)
