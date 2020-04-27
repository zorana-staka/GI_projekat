class Input_file:

    def __init__(self, path):
        self.path = path
        self.file = path
        self.compressed = False
        self.set_file_type()
        self.body_header_line = None

    def set_file_type(self):
        if self.path.endswith('vcf.gz') or self.path.endswith('vcf.GZ'):
            self.compressed = True
        elif self.path.endswith('.vcf'):
            self.compressed = False
        else:
            self.compressed = None

    def set_body_header_line(self, body_header_line):
        self.body_header_line = body_header_line
