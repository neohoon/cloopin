import socket
import chardet
import random
import string


PORT_NUM = 8889
RECV_BUF_SZ = int(1e8)
HANDSHAKE_ALIVE = "alive?"
HANDSHAKE_REPLY = "yes"


def utf2euc(contents):
    return str(contents, 'utf-8').encode('euc-kr')


def euc2utf(contents):
    return str(contents, 'euc-kr').encode('utf-8')


def convert_to_euc_kr(sent):

    char_type = chardet.detect(sent)

    if char_type['encoding'] == 'utf-8':
        euc_sent = utf2euc(sent)
    elif char_type['encoding'] == 'EUC-KR':
        euc_sent = sent
    else:
        euc_sent = None

    return euc_sent


def gen_random_word(length):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def KoreanTTS_client(txt_sent):

    if isinstance(txt_sent, str):
        txt_sent = txt_sent.encode()
    euc_kr_buf = convert_to_euc_kr(txt_sent)
    fname_core = gen_random_word(16)
    fname_wav = fname_core + '.wav'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    server_address = ('localhost', PORT_NUM)
    print('connecting to %s port %s' % server_address)

    send_buf = HANDSHAKE_ALIVE
    recv_buf = []
    print(" # Client: send data, {}".format(send_buf))
    try:
        sock.connect(server_address)
        sock.sendall(send_buf.encode())
        recv_buf = sock.recv(RECV_BUF_SZ)
    except Exception as e:
        print(e)
        print(" @ Error: TCP alive error in handshaking...\n")
        return None
    sock.close()

    if recv_buf[0:3] == HANDSHAKE_REPLY.encode():

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        server_address = ('localhost', PORT_NUM)
        print('connecting to %s port %s' % server_address)

        try:
            sock.connect(server_address)
            sock.sendall(euc_kr_buf)
            recv_buf = sock.recv(RECV_BUF_SZ)
        except Exception as e:
            print(e)
            print(" @ Error: TCP data error")
            return None
        print(" recv length: {:d}".format(len(recv_buf)))
        sock.close()

        if recv_buf:
            with open(fname_wav, 'wb') as f:
                f.write(recv_buf)
        else:
            return None

    return fname_wav


def main():

    txt_sent = open('kr_euc.txt', 'rb').read()
    # txt_sent = open('kr_utf.txt', 'rb').read()

    out_wav = KoreanTTS_client(txt_sent)

if __name__ == "__main__":

    main()


