print("Bot is working!")

photo = "assets/welcome.png"

my_chat = 1768792009
my_id = 1768792009

admins = [1768792009] #712989239

def welcome(name):
    return f"Здравствуйте, {name}!\nЯ рад приветствовать вас в нашем боте!\nЧем я могу вам помочь?"

def decode(str: str):
    hastaged = str.split("ᗰ")
    return hastaged

def admin(id: int):
    return id in admins
