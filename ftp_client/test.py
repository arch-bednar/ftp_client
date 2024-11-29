from urllib.parse import urlparse
import socket
import os
import asyncio
# dirt = {"-u": 1}
#
# dirt["-u"]=2
#
# o=urlparse("ftp://127.0.0.1/test/")
#
# print(dirt.keys())
#
# print(o)
#
o = urlparse("ftp://user:pass@127.0.0.1:21/test/")
#
print(o)
#
# print(o.scheme)
#
# print(o.netloc.find(":"))
#
# print(ord('_'))
#
#
# i = int("sss")

print(os.linesep)

#
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(("127.0.0.1", 21))

# data = s.recv(1024)
# print(data)
# s.send((f"USER admin{os.linesep}").encode())
# s.send("USER".encode())
# data=s.recv(1024)
# print(data)
# s.close()
#s.setblocking(False)


# while True:
#     print("new jump")
#     data = s.recv(1024)
#
#     if not data:
#         break
#     print(data.decode("utf-8"))
#     i = input("pODAJ COS: ")
#     i = i+'\r'+'\n'
#     i = i.encode()
#     s.send(i)
#
# x = input("")
# x = x+os.linesep
# for char in x:
#     print(ord(char))

x = 177
if x in range(200, 300) or x in range(100, 200):
    print(x)


x = [1,2,3,4,5,6]
print(x[-2])


async def loop1():
    for i in range(1,1000):
        print("i :" + str(i))


def loop2():
    for i in range(1000,2000):
        print("xxxxx :" + str(i))

async def main():
    task1 = asyncio.create_task(loop1())
    task2 = asyncio.create_task(loop2())
    # Czekamy, aż oba zadania zakończą
    await task1
    await task2

if __name__=="__main__":
    asyncio.run(main())