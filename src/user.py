import os


class AppUser:
    def __init__(self, user_id, email, users_dir):
        self.user_id = user_id
        self.email = email
        self._set_name()
        self._create_user_dirs(users_dir)

    def _set_name(self):
        names = self.email.split("@")[0].split(".")
        if len(names) > 1:
            self.first, *_, self.last = names
        elif names:
            self.first = names[0]
            self.last = ""
        self.name = f"{self.first} {self.last}".strip().title()

    def _create_user_dirs(self, users_dir):
        self.user_dir = os.path.join(users_dir, self.user_id)
        os.makedirs(self.user_dir, exist_ok=True)
