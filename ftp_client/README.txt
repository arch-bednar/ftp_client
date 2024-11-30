Instrukcja obsługi komend FTP:
cp, mv
Składnia dla komendy cp lub mv:
<command> -u <user> -p <password> -o <port> <absolute_path_from> <absolute_path_to>
---or---
<command> <link_path_from> <link_path_to>
Gdzie:
<absolute_path_from> - pełna ścieżka do pliku lub katalogu na serwerze FTP.
<absolute_path_to> - pełna ścieżka do miejsca docelowego na serwerze FTP.
Format dla <absolute_path_to>: ftp://absolute/path/to/file_or_directory.
<link_path_to> - ścieżka z linkiem zawierającym dane logowania: ftp://<user>:<password>@<server_address>/absolute/path/to/file_or_directory.

1. wget
Składnia dla komendy wget:
wget -u <user> -p <password> -o <port> <absolute_path_from> <absolute_path_to>
---or---
wget <link_path_from> <link_path_to>
Gdzie:
<absolute_path_from> - pełna ścieżka do pliku lub katalogu na serwerze FTP.
Format: ftp://absolute/path/to/file_or_directory.
<link_path_from> - ścieżka z linkiem zawierającym dane logowania: ftp://<user>:<password>@<server_address>/absolute/path/to/file_or_directory.

2. mkdir
Składnia dla komendy mkdir:
mkdir -u <user> -p <password> -o <port> <absolute_path_to_create_directory>
---or---
mkdir <absolute_path_to>
Gdzie:
<absolute_path_to_create_directory> - pełna ścieżka, gdzie nowy katalog ma zostać utworzony.
Format: ftp://<user>:<password>@<server_address>/path/for/directory.

3. rmdir
Składnia dla komendy rmdir:
rmdir -u <user> -p <password> -o <port> <absolute_path_to_delete_directory>
---or---
rmdir <absolute_path_to>
Gdzie:
<absolute_path_to_delete_directory> - pełna ścieżka katalogu, który ma zostać usunięty.
Format: ftp://<user>:<password>@<server_address>/path/to/directory.

4. rm
Składnia dla komendy rm:
rm -u <user> -p <password> -o <port> <absolute_path_to_delete_file>
---or---
rm <absolute_path_to>
Gdzie:
<absolute_path_to_delete_file> - pełna ścieżka pliku, który ma zostać usunięty.
Format: ftp://<user>:<password>@<server_address>/path/to/file
