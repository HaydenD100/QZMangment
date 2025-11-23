class Software:
    def __init__(self):
        self.ID = None
        self.Name = None
        self.Version = None
        self.CVE = None
        self.Summary = None
        self.Recommnedation = None
        self.LastScan = None #Time Stamp
        self.UserID = None
        pass
class User:
    def __init__(self):
        self.ID = None
        self.HashedPassword = None
        self.Name = None
        pass
