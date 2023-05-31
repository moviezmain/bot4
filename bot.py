import os,time, requests, json
from urllib.parse import unquote
from pySmartDL import SmartDL
from urllib.error import HTTPError
from telebot import TeleBot
from re import findall
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


BOT_TOKEN = "6093877183:AAGsnqMWR-d2yXPyImJLr6ApZXo9qmBxzzg"
bot = TeleBot(BOT_TOKEN)


login_key = "f13d2b11258ad59462a4" # api login
key = "MeAg79G4lrUmZJq" # api password
def db(payload,method="findOne"):
    url = f"https://ap-south-1.aws.data.mongodb-api.com/app/data-jktzb/endpoint/data/v1/action/{method}"
    headers = {'Content-Type': 'application/json',
               'Access-Control-Request-Headers': '*',
               'api-key': 'oEMu1rIsWSQgMm20dBo9av7uQ1FxIvtNgvR61QwjmcmqEuxAOyIGGl0VwS4QftiA'}
    return requests.post(url, headers=headers, data=payload).json().get('document')


def gToken():
    data = json.dumps({"collection": "credentials", "database": "api", "dataSource": "Cluster0", "filter": {}})
    return db(data).get('gToken')

def auth():
    g_auth = GoogleAuth()
    if not os.path.exists("gToken"):
        credentials = gToken()
        with open('gToken', 'w') as file:
            file.write(credentials)
    g_auth.LoadCredentialsFile('gToken')
    if g_auth.access_token_expired:
        g_auth.Refresh()
        print("refresh")
    else:
        g_auth.Authorize()
        print("auth")
    return g_auth

def get_ticket(file_id):
    headers = {'file':file_id,'login':login_key,'key':key}
    response = requests.get("https://api.strtape.tech/file/dlticket?",headers)
    data = json.loads(response.text)
    result = data.get('result')
    return result

def get_links(data):
    return findall('https://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', data)[0]

def dl_url(ticket,file_id):
    headers = {'file':file_id,'ticket':ticket,'login':login_key,'key':key}
    response = requests.get("https://api.strtape.tech/file/dl?",headers)
    data = json.loads(response.text)
    result = data.get('result')
    if result is not None:
        link = result.get('url')
        return link
    else:
        return "Not Found"
def get_file_id(link):
    lst = []
    for i in link:
        lst.append(i)

    lst2 = lst[25:]

    file_id = ""
    for i in lst2:
        if i == "/":
            break;
        else:
            file_id += i
    #print(file_id)
    return file_id

def get_direct_streamtape(url):
    file_id = get_file_id(url)
    result = get_ticket(file_id)
    ticket = result.get('ticket')
    time.sleep(result.get('wait_time'))
    link = dl_url(ticket,file_id)
    return link

def gUpload(title,file_path):
    g_auth = auth()
    drive = GoogleDrive(g_auth)
    metadata = {
        'parents': [
            {"id": "1044vn2oOlwtGaGRz-_UpjA9VMoB5dmTC"}
        ],
        'title': title,
        'mimeType': 'video/x-matroska',
        'supportsTeamDrives': True, 'includeItemsFromAllDrives': True
    }
    file = drive.CreateFile(metadata)
    file.SetContentFile(file_path)
    file.Upload()
    os.remove(file_path)


def download_file(url, dl_path):
  try:
    dl = SmartDL(url, dl_path, progress_bar=False)
    dl.start()
    filename = dl.get_dest()
    if '+' in filename:
          xfile = filename.replace('+', ' ')
          filename2 = unquote(xfile)
    else:
        filename2 = unquote(filename)
    os.rename(filename, filename2)
    return True, filename2
  except HTTPError as error:
    return False, error




@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "contact @ignore709")


@bot.message_handler(content_types=['text'])
def loader(update):
    dirs = './downloads/'
    if 'streamtape.com' in update.text:
        pass
    elif 'strtapeadblocker.xyz' in update.text:
        pass
    else:
        return
    link = get_links(update.text)
    if '/' in link:
        links = link.split('/')
        if len(links) == 6:
            if link.endswith('mp4'):
                link = link
            else:
                link = link + 'video.mp4'
        elif len(links) == 5:
            link = link + '/video.mp4'
        else:
            return
    else:
        return
    url = get_direct_streamtape(link)
    filename = update.text
    filename = filename[filename.index("n:")+2:filename.index("id:")].strip()
    result, dl_path = download_file(url, dirs)
    custom_path = os.path.join(dirs, filename)
    os.rename(dl_path, custom_path)
    if result == True:
        try:
            gUpload(filename,custom_path)
            bot.reply_to(update, "completed")
        except:
            bot.reply_to(update,"failed")



bot.infinity_polling()
