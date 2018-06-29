class SMTPRequestParser:
    def __init__(self, request):
        self.request = request
        request = request.rstrip(b'\r\n')
        try:
            (self.verb, self.arg) = request.split(b' ', 1)
        except ValueError:
            (self.verb, self.arg) = (request, b'')

    def get_verb_and_arg(self):
        return (self.verb, self.arg)
