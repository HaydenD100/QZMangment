class Software:
    def __init__(self):
        self.ID
        self.Name
        self.CVSS
        self.Summary
        self.Recommnedation
        self.LastScan #Time Stamp
        self.UserID
        pass
class User:
    def __init__(self, user_id, name, hashed_password):
        self.ID = user_id
        self.Name = name
        self.HashedPassword = hashed_password
        pass
