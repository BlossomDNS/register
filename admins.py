emails = ["test@123.com"]
passwords = ["test"]

#Admin accounts
class Admin:
    def __init__(self, username, password, id):
        self.id = id
        self.username = username
        self.password = password


admin_accts = []
admin_accts.append(Admin(id=1, username="test",password="test"))
admin_accts.append(Admin(id=2, username="3",password="3"))