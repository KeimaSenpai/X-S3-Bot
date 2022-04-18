class toDus():

    def __init__(self, token: str):
        """
        token from todus
		
		a regular Json Web Token
        """
        self.token = token
        self.timer = 0
        self.maxtimer = 10000;

    def Get_Upload_URL(self, size: int):
        """
        atenticates to the todus server and get an s3 url to the wich upload the file

        returns the post url and the get url to share the file

        up , down
        """
        def AUTH_BASE64():
            # TELEFONO + TOKEN en Base64
            TOKEN = self.token
            import base64
            try:
                import ujson as json
            except:
                import json
            PHONE = json.loads(base64.decodebytes(TOKEN.split('.')[1].encode('utf-8')).decode('utf-8'))["username"]
            auth_im_todus = chr(0) + PHONE + chr(0) + TOKEN
            auth_im_todus = bytes(auth_im_todus, encoding='utf-8')
            encoded_auth_im_todus = base64.encodebytes(auth_im_todus)
            encoded_auth_im_todus = encoded_auth_im_todus.decode('utf-8')
            return encoded_auth_im_todus

        def ID_SESION():
            # ID-SESION
            charset = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                       "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
                       "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7",
                       "8", "9"]
            ids = ""
            import random
            for i in range(5):
                ids += charset[random.randrange(0, len(charset))]
            return ids

        id_sesion = ID_SESION()
        encoded_auth_im_todus = AUTH_BASE64()

        # SOCKET
        import socket
        from OpenSSL import SSL
        # print("= SOCKET SSL =")
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl = SSL.Connection(ctx, s)
        # print("= CONECTANDO =")
        ssl.connect(("im.todus.cu", 1756))  # 5000

        # esperando a recibir respuesta
        def waiting(expected):
            new = ""
            self.timer = 0
            while expected not in new:
                self.timer+=1
                if(self.timer>=self.maxtimer):
                    break;
                new = ssl.recv(4096)
                new = new.decode("utf-8")
                print("RESPONSE", new)
                if 'Invalid username or password' in new:
                    return 'token error'
                if not new:
                    s.close()
                    break
            return new

        ssl.sendall(
            b"<stream:stream xmlns='jc' o='im.todus.cu' xmlns:stream='x1' v='1.0'>")
        waiting(
            "<stream:features><es xmlns='x2'><e>PLAIN</e><e>X-OAUTH2</e></es><register xmlns='http://jabber.org/features/iq-register'/></stream:features>")
        ssl.sendall(
            bytes(f"<ah xmlns='ah:ns' e='PLAIN'>"+encoded_auth_im_todus+"</ah>", 'utf-8'))
        response = waiting("<ok xmlns='x2'/>")
        if response == 'token error':
            return 'token error'
        ssl.sendall(
            b"<stream:stream xmlns='jc' o='im.todus.cu' xmlns:stream='x1' v='1.0'>")
        waiting("<stream:features><b1 xmlns='x4'/>")
        ssl.sendall(
            bytes(
                f"<iq i='"+id_sesion+"-1' t='set'><b1 xmlns='x4'></b1></iq>", 'utf-8'))
        waiting(f"i='{id_sesion}-1'")
        ssl.sendall(
            bytes(
                f"<iq i='{id_sesion}-2' t='get'><query xmlns='todus:purl' type='2' persistent='false' size='"+str(size)+"' room=''></query></iq>", 'utf-8'))
        response = waiting(f"i='{id_sesion}-2'")

        import xmltodict
        response = xmltodict.parse(response)
        return response['iq']['query']['@put'], response['iq']['query']['@get']


    def Get_DOWNLOAD_URL(self,url):
        """
        atenticates to the todus server and get an s3 url to the wich upload the file

        returns the post url and the get url to share the file

        up , down
        """
        def AUTH_BASE64():
            # TELEFONO + TOKEN en Base64
            TOKEN = self.token
            import base64
            try:
                import ujson as json
            except:
                import json
            PHONE = json.loads(base64.decodebytes(TOKEN.split('.')[1].encode('utf-8')).decode('utf-8'))["username"]
            auth_im_todus = chr(0) + PHONE + chr(0) + TOKEN
            auth_im_todus = bytes(auth_im_todus, encoding='utf-8')
            encoded_auth_im_todus = base64.encodebytes(auth_im_todus)
            encoded_auth_im_todus = encoded_auth_im_todus.decode('utf-8')
            return encoded_auth_im_todus

        def ID_SESION():
            # ID-SESION
            charset = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                       "U", "V", "W", "X", "Y", "Z", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
                       "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7",
                       "8", "9"]
            ids = ""
            import random
            for i in range(5):
                ids += charset[random.randrange(0, len(charset))]
            return ids

        id_sesion = ID_SESION()
        encoded_auth_im_todus = AUTH_BASE64()

        # SOCKET
        import socket
        from OpenSSL import SSL
        # print("= SOCKET SSL =")
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl = SSL.Connection(ctx, s)
        # print("= CONECTANDO =")
        ssl.connect(("im.todus.cu", 1756))  # 5000

        # esperando a recibir respuesta
        def waiting(expected):
            new = ""
            while expected not in new:
                new = ssl.recv(4096)
                new = new.decode("utf-8")
                print("RESPONSE", new)
                if 'Invalid username or password' in new:
                    return 'token error'
                if not new:
                    s.close()
                    break

            return new
        ssl.sendall(
            b"<stream:stream xmlns='jc' o='im.todus.cu' xmlns:stream='x1' v='1.0'>")
        waiting(
            "<stream:features><es xmlns='x2'><e>PLAIN</e><e>X-OAUTH2</e></es><register xmlns='http://jabber.org/features/iq-register'/></stream:features>")
        ssl.sendall(
            bytes(f"<ah xmlns='ah:ns' e='PLAIN'>"+encoded_auth_im_todus+"</ah>", 'utf-8'))
        response = waiting("<ok xmlns='x2'/>")
        if response == 'token error':
            return 'token error'
        ssl.sendall(
            b"<stream:stream xmlns='jc' o='im.todus.cu' xmlns:stream='x1' v='1.0'>")
        waiting("<stream:features><b1 xmlns='x4'/>")
        ssl.sendall(
            bytes(
                f"<iq i='"+id_sesion+"-1' t='set'><b1 xmlns='x4'></b1></iq>", 'utf-8'))
        waiting(f"i='{id_sesion}-1'")
        ssl.sendall(
            bytes(
                f"<iq i='{id_sesion}-2' t='get'><query xmlns='todus:gurl' url='"+str(url)+"'></query></iq>", 'utf-8'))
        response = waiting(f"t='result' i='{id_sesion}-2'")

        import xmltodict
        response = xmltodict.parse(response)
        return response['iq']['query']['@du']