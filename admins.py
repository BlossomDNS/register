#Admin accounts
class Admin:
    def __init__(self, username, password, id):
        self.id = id
        self.username = username
        self.password = password


admin_accts = []
admin_accts.append(Admin(id=1, username="test@test",password="test"))