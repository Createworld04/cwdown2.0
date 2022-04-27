import requests, json, zipfile, io, re, os
import subprocess
import helper
from pyromod import listen
from pyrogram.types import Message
import tgcrypto
import pyrogram
from pyrogram import Client, filters
import time
from pyrogram.types import User, Message
# from p_bar import progress_bar
from subprocess import getstatusoutput
import logging
#from jinja2 import Template
# from details import api_id, api_hash, bot_token
from urllib.parse import urlparse
from urllib.parse import unquote

# import requests
# bot = Client(
#     "bot",
#     api_id=api_id,
#     api_hash=api_hash,
#     bot_token=bot_token)


bot = Client(
    "Utkarsh",
    bot_token=os.environ.get("BOT_TOKEN"),
    api_id=int(os.environ.get("API_ID")),
    api_hash=os.environ.get("API_HASH")
)
@bot.on_message(filters.command(["start"]))
async def start(bot, update):
       await update.reply_text("Hi i am **Utkarsh Downloader**.\n\n"
                              "**NOW:-** "
                                       
                                       "Press **/login** to continue..\n\n"
                                     "Bot made by **ACE**" )



logger = logging.getLogger()
utk_url = "https://live-wsshop.e-utkarsh.com/log/login"
utk_books_url =  "https://live-wsuser.e-utkarsh.com/api/getBooksListForUser"
utk_book_url = "https://live-wsbook.e-utkarsh.com/metainfo/getAllChaptersMetaInfo?siteId=1&bookId={}"

data = {"username":"","password":"","siteId":"1"}
cleanr = re.compile("<.*?>")
os.makedirs("./htmls", exist_ok=True)

@bot.on_message(filters.command(["login"])& ~filters.edited)
async def account_login(bot: Client, m: Message):
    editable = await m.reply_text("Send **ID & Password** in this manner otherwise bot will not respond.\n\nSend like this:-  **ID*Password**"
    )
    
    input1: Message = await bot.listen(editable.chat.id)
    raw_text = input1.text
    data["username"] = raw_text.split("*")[0]
    data["password"] = raw_text.split("*")[1]

    res = requests.post(utk_url, data=data).json()
    token = res["access_token"]

    hdr = {"X-Auth-Token": token}
    books_response = requests.post(utk_books_url, headers=hdr).json()
    try:
        books_dict = json.loads(books_response["books"])
    except:
        exit()

    main_books = {}
    for book in books_dict:
        if 'packageBookIds' in book and 'packageBookId' not in book:
            main_books[book["id"]] = {"title": book["title"], "books": book["packageBookIds"]}
        if 'packageBookIds' not in book and 'packageBookId' not in book:
            main_books[book["id"]] = {"title": book["title"]}

    msg = f"You have {len(main_books)} main books:\n\n"
    msg += "<b>BatchId - MainBookName - SubBooksIds</b>\n\n"
    
    for __id, book in main_books.items():
        msg += f"**{__id} - {book['title']}**"
        try:
            msg += f" - {book['books']}\n"
        except KeyError:
            msg += "\n"
        
    tt = ""
    for __id, book in main_books.items():
        name = book["title"]
        pdf_title = f"{__id}. {name}"
        # pdf_file = f"{u_path}/{pdf_title}.pdf"
        # options.update({'title': pdf_title})
        books_list = [str(__id)]
        try:
            books_list += book["books"].split(",")
        except KeyError:
            pass
        # print(books_list)
        bb = f'**{pdf_title}**\n'
        if len(f'{tt}{bb}')>4096:
            await m.reply_text(tt)
            tt =""
        tt+=bb
    await m.reply_text(msg)
        # await m.reply_text(name)
        #await m.reply_text(pdf_title)
    # await m.reply_text("**Send resolution in which you want to download course :**")
    # input2: Message = await bot.listen(editable.chat.id)
    # raw_text1 = input2.text
    
    # await m.reply_text("**Send Batch id:**")
    # input3: Message = await bot.listen(editable.chat.id)
    # raw_text3 = input3.text

    # editable4= await m.reply_text("Now send the **Thumb url**\nEg : ```https://telegra.ph/file/d9e24878bd4aba05049a1.jpg```\n\nor Send **no**")
    # input6 = message = await bot.listen(editable.chat.id)
    # raw_text6 = input6.text

    # thumb = input6.text
    # if thumb.startswith("http://") or thumb.startswith("https://"):
    #     getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
    #     thumb = "thumb.jpg"
    # else:
    #     thumb == "no"
        
    xx =await m.reply_text("Genrating Course txt in this id")
    count =1
    try:
        vv =""
        
        for book in books_dict:
            _id = book["id"]
            name = book["title"]
            title = f"{_id}. {name}"
            html_file = f"./htmls/{title}.html"
            book_res = requests.get(utk_book_url.format(_id))
            z = zipfile.ZipFile(io.BytesIO(book_res.content))
            file_json = json.loads(z.read("json.txt"))
            topics = {}
            for i, topic in enumerate(file_json["chaptersList"]):
                topic_name = topic["name"]
                topics.update({i: {"name": topic_name, "videos": []}})
                topic_res = file_json["jsonChapterDetails"][i]["defaultResources"]
                if isinstance(topic_res, str):
                    topic_res = topic_res.replace('\r\n', '').replace('\r', '')
                    topic_res = re.sub(cleanr, "", topic_res)
                    topic_res = eval(topic_res)
                videos = []
                
                for res in topic_res:
                    res_id = res["id"]
                    res_type = res["resType"]
                    res_name = unquote(res["resName"]).replace("+", " ").replace("'","_").replace('"', "_").replace("/","_")
                    res_link = unquote(res["resLink"]).replace("#", "")
                    if "drive" in res_link:
                        if "https://drive.google.com/file" in res_link:
                            parts = urlparse(res_link)
                            directories = parts.path.strip('/').split('/')[2]
                            res_link=f"https://drive.google.com/u/0/uc?id={directories}&export=download"
                        elif "https://drive.google.com/open" in res_link:
                            y = res_link.split("=")[1]
                            res_link = f"https://drive.google.com/u/0/uc?id={y}&export=download"
#                         res_link=f"https://drive.google.com/u/0/uc?id={res_link[32:-17]}&export=download"
                    res_player = res["videoPlayer"]
                    if res_type == "Reference Videos":
                        if res_player == "youtube":
                            res_link = f"https://youtube.com/watch?v={res_link}"
                        elif res_player == "custom":
                            link_parts = res_link.split("/")
                            if len(link_parts) != 5:
                                res_link = f"https://youtube.com/watch?v={res_link}"
                            else:
                                res_id = res_link.split("/")[4].split("-")[0]
                                res_link = f"http://cdn.jwplayer.com/manifests/{res_id}.m3u8"
                    elif res_type == "Reference Web Links":
                        pass
                    else:
                        continue
                    # print(res_name + ":" + res_link)
                    dd =f'{res_name}:{res_link}\n'
                    with open(f"file.txt", "w", encoding='utf-8') as f:
                        vv+=dd 
                        f.write(vv)
        await m.reply_document(f"file.txt",caption=tt)





                # await m.reply_text(res_name + ":" + res_link) 
                


        #     if "drive" in res_link:
        #         try:
        #             gd = res_link[32:-17]
        #             link=f"https://drive.google.com/u/0/uc?id={gd}&export=download"
        #                 # print(link)
        #         except Exception:
        #             continue
                
        #     elif ("youtube") in res_link:
                    
        #         link = res_link
        #     elif ("jwplayer") in res_link:
        #         link =res_link
        #     else:
        #         pass
                
        #     dd =f'{res_name}:{link}\n'
        #     with open(f"file.txt", "w", encoding='utf-8') as f:
        #             vv+=dd 
        #             f.write(vv)
        # await m.reply_document(f"file.txt",caption=msg)
        


            #     dd = f'**{res_name}**({topic_name}):```{res_link}```\n'
            #     if len(f"{vv}{dd}")>4096:
            #         await m.reply_text(dd)
            #         vv = ""
            #     vv+=dd  
            # await m.reply_text(vv)
    #         if "youtu" in res_link:
    #             if raw_text1 in ["144", "240", "480"]:
    #                 ytf = f'bestvideo[height<={raw_text1}][ext=mp4]+bestaudio[ext=m4a]'
    #             elif raw_text1 == "360":
    #                 ytf = 18
    #             elif raw_text1 == "720":
    #                 ytf = 22
    #             else:
    #                 ytf = 18
    #         else:
    #             ytf=f"bestvideo[height<={raw_text1}]"

    #         if ytf == f'bestvideo[height<={raw_text1}][ext=mp4]+bestaudio[ext=m4a]':
    #             cmd = f'yt-dlp -o "{res_name}.mp4" -f "{ytf}" "{res_link}"'
    #         elif raw_text1 == "no":
    #             cmd=f'yt-dlp -o "{res_name}.mp4" "{res_link}"'
    #         elif "jwplayer" in res_link and raw_text1 in ["144", "240","360", "480","720","no"]:
    #             cmd=f'yt-dlp -o "{res_name}.mp4" "{res_link}"'    
    #         elif "google" in res_link and raw_text1 in ["144", "240","360", "480","720","no"]:
    #             await m.reply_text(f'**{res_name}**\n\n```{res_link}```')
    #         elif "upload/books" in res_link:
    #             await m.reply_text("not a valid link")
    #                 # elif f'{res_id}' in res_link:
    #                 #     await m.reply_text(res_id)
    #         else:
    #             cmd = f'yt-dlp -o "{res_name}.mp4" -f "{ytf}+bestaudio" "{res_link}"'
                    
    #         print(res_link)
            
                
    # #             cc = f"**Title** : {res_name}\n**Batch Title :** {topic_name}\n\n**Index - {count}**"
    # #             show = f"**Downloading:-\n\n{res_name}\n\nLink:-** ```{res_link}```"
    # #             prog = await m.reply_text(show)
    # #                 # os.system(cmd)
    # #             try:
    # #                 download_cmd = f"{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args 'aria2c: -x 16 -j 32'"
    # #                 os.system(download_cmd)

    # #                 filename = f"{res_name}.mp4"
    # #                 subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:20 -vframes 1 "{filename}.jpg"', shell=True)
    # #                 await prog.delete (True)

    # #                 reply = await m.reply_text(f"Uploading Video - ```{res_name}```")

    # #                 try:
    # #                     if thumb == "no":
    # #                        thumbnail = f"{filename}.jpg"
    # #                     else:
    # #                          thumbnail = thumb
    # #                 except Exception as e:
    # #                     await m.reply_text(str(e))

    # #                 dur = int(helper.duration(filename))
    # #                 start_time = time.time()
    # #                 await m.reply_video(f"{res_name}.mp4",caption=cc, supports_streaming=True,height=720,width=1280,thumb=thumbnail,duration=dur, progress=progress_bar,progress_args=(reply,start_time))
    # #                 count+=1
    # #                 os.remove(f"{res_name}.mp4")
    # #                 os.remove(f"{filename}.jpg")
    # #                 await reply.delete (True)

    # #             except Exception as e:
    # #                 await m.reply_text(f'**Video downloading failed\nor not a valid video link** ❌\n**Name :** {res_name}\n\n**Link :** ```{res_link}```\n\n{e}')
    # #                 continue
    # #                 time.sleep(1)
    except Exception as e:   
        await m.reply_text(f'{e}')     
    await m.reply_text('Done')   



bot.run()           
            


