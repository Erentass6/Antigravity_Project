from pymongo import MongoClient
from config import Config

class Database:
    def __init__(self, *args, **kwargs):
        self.client = None
        self.db = None
        self.users = None
        self.inventory = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.DATABASE_NAME]
            # Koleksiyonları direkt bağlıyoruz
            self.users = self.db[Config.USERS_COLLECTION]
            self.inventory = self.db[Config.INVENTORY_COLLECTION]
            return True
        except Exception as e:
            return False

    def disconnect(self):
        if self.client:
            self.client.close()

    def get_collection(self, name):
        # Eğer database henüz bağlanmadıysa bağla
        if self.db is None:
            self.connect()
        return self.db[name]

# İŞTE KRİTİK NOKTA: Burayı böyle yazıyoruz ki her yer tanısın
db = Database()