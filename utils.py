from skpy import Skype
from skpy.core import SkypeAuthException, SkypeApiException
from skpy.user import SkypeContact, SkypeObj

def authenticate(username, password):
    try:
        sk = Skype(username, password)
        # sk.conn.setUserPwd(user=username, pwd=password)
        return sk

    except (SkypeAuthException, SkypeApiException) as e:
        return None


def fetch_all_contacts(obj):
    if isinstance(obj, SkypeObj):
        contacts = []
        for each in obj.contacts:
            contacts.append(each)
    return contacts


def create_group(obj, group_title="default", users=[]):
    if isinstance(obj, SkypeObj):
        try:
            # new_list = [group_title] + users
            created = obj.chats.create(users)
            return created
        except Exception as e:
            print(str(e))
            return None