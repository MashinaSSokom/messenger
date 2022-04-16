import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        # print({'clsname': clsname, 'bases': bases, 'clsdict': clsdict})

        methods = []
        attrs = []

        for func in clsdict:
            try:
                instructions = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for instruction in instructions:
                    # print(instruction)
                    if instruction.opname == 'LOAD_METHOD':
                        if instruction.argrepr not in methods:
                            methods.append(instruction.argrepr)
                    elif instruction.opname == 'LOAD_GLOBAL':
                        if instruction.argrepr not in attrs:
                            attrs.append(instruction.argrepr)

        # print({'methods': methods, 'attrs': attrs})

        if 'connect' in methods:
            raise TypeError('В классе Server нельзя использовать метод connect!')
        if not ('SOCK_STREAM' in attrs and 'AF_INET' in attrs):
            raise TypeError('Некорректная инициализация сокета согласно протоколу TCP')

        super().__init__(clsname, bases, clsdict)

