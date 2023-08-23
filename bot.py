from telebot import TeleBot
import requests


bot = TeleBot("")


def getSize(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


remove = "1 2 3 4 5 6 7 8 9 0 1gb 2gb 4gb 5gb 6gb 7gb 8gb 9gb 3gb vish xxx prt mp4 esub info moviesrequest da rips " \
         "tbpindex cinesandhadi telexmovies blaster originals viewcinemas x264 prolover hq hdtv 720p 1080p 10bit web " \
         "webrip minx x265 480p nf galaxytv tvseriesbay nsmovies7 " \
         "2ch psa iboxtv hevc ion265 amzn hs dl aac 0 h 264 aha mkv tvbay t4tvseries ion10 atvp 6ch rarbg mkvcinemas " \
         "korea aac2 robots ddp5 ntb bluray viewott wdym ysteam brrip imediashare multi hdrip".split(
    " ")


def getTitle(title):
    title = title.split("\n")[0]
    title = title.translate(str.maketrans("[]()-+._@—", "          ")).strip().lower().split()
    title = " ".join([x for x in title if x not in remove])
    return title.title().strip()


def getDetails(message, method="add"):
    title = message.caption if message.caption else message.document.file_name if message.document else message.video.file_name
    Id = message.id
    size = message.document.file_size if message.document else message.video.file_size
    size = getSize(size)
    if method == "add":
        title = getTitle(title)
    return title + " - " + size, Id


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "contact @ignore709")


@bot.channel_post_handler(content_types=['document', 'video'])
def add(message):
    title, Id = getDetails(message)
    category = None
    channel = 0
    if message.chat.id == -1001672758629:
        channel = 1001672758629
        category = "movies"
    elif message.chat.id == -1001885286768:
        channel = 1001885286768
        category = "series"
    elif message.chat.id == -1001805372983:
        channel = 1001805372983
        category = "dramas"
    elif message.chat.id == -1001943439473:
        channel = 1001943439473
        category = "anime"

    if category:
        try:
            requests.post(f"https://api.moviezdude.site/{category}",
                          json={"title": title, "Id": Id, "channel": channel})
        except:
            pass


@bot.edited_channel_post_handler(content_types=['document', 'video'])
def update(message):
    title, Id = getDetails(message, "update")
    category = None
    if message.chat.id == -1001672758629:
        category = "movies"
    elif message.chat.id == -1001885286768:
        category = "series"
    elif message.chat.id == -1001805372983:
        category = "dramas"
    elif message.chat.id == -1001943439473:
        category = "anime"

    if category:
        try:
            requests.put(f"https://api.moviezdude.site/{category}",
                         json={"title": title, "Id": Id})
        except:
            pass


bot.infinity_polling()
