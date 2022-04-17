import os
import re
import asyncio
import requests

from telethon import TelegramClient, events
from zipfile import ZipFile, ZIP_DEFLATED

import s3.Config as cfg
import s3.toDus as toDus
import s3.multiFile as multiFile


conf = cfg.Config()


async def text_progres(index, max):
    try:
        if max < 1:
            max += 1
        porcent = index / max
        porcent *= 100
        porcent = round(porcent)
        make_text = '(' + str(porcent) + '% '
        index_make = 1
        make_text += '100%)'
        make_text += '\n'
        while index_make < 21:
            if porcent >= index_make * 5:
                make_text += '█'
            else:
                make_text += '▒'
            index_make += 1
        make_text += '\n'
        make_text += '(' + str(index) + '/' + str(max) + ')'
        return make_text
    except Exception as ex:
        return ex


async def upload_to_todus(file, bot, ev, msg):
    try:
        todusUtils = toDus.toDus(conf.S3Token)
        file_size = os.stat(file)
        len = file_size.st_size
        req = ''
        try:
            req = todusUtils.Get_Upload_URL(file_size.st_size)
        except:
            print('Resubiendo...')
            conf.stepTokenIndex()
            conf.stepToken()
            # await asyncio.sleep(60 * 10)
            return await upload_to_todus(file, bot, ev, msg)
        get_link = ''
        if req != 'token error' and req != '':
            get, put = req[1], req[0]
            h = {
                "Host": "s3.todus.cu",
                "user-agent": "ToDus 0.39.4 HTTP-Upload",
                "authorization": "Bearer "+str(conf.S3Token),
                "content-type": "application/octet-stream",
                "content-length": str(len),
                "accept-encoding": "gzip"
            }
            try:
                f = open(file, 'rb')
                if put != '':
                    tmp = requests.put(put, data=f.read(), headers=h)
                    if tmp.status_code == 200:
                        get_link = get
                    else:
                        print('Resubiendo Error En el Put!')
                        return await upload_to_todus(file, bot, ev, msg)
                else:
                    print('Resubiendo...')
                    conf.stepTokenIndex()
                    conf.stepToken()
                    # await asyncio.sleep(60 * 10)
                    return await upload_to_todus(file, bot, ev, msg)
                f.close()
            except Exception as e:
                print('(toDus Server) \n' + str(e))
                return await upload_to_todus(file, bot, ev, msg)
        else:
            conf.stepTokenIndex()
            conf.stepToken()
            # await msg.edit("Error de Token Actualize Su Token OJO!")
            return await upload_to_todus(file, bot, ev, msg)
        return get_link
    except Exception as e:
        conf.stepTokenIndex()
        conf.stepToken()
        print('Resubiendo Error Comleto!')
        return await upload_to_todus(file, bot, ev, msg)
    return ''


def download_from_todus(url, name, bot, ev, msg):
    todusUtils = toDus.toDus(conf.S3Token)
    signed = todusUtils.Get_DOWNLOAD_URL(url)
    if signed != 'token error':
        h = {
            "Host": "s3.todus.cu",
            "user-agent": "ToDus 0.39.4 HTTP-Download",
            "authorization": "Bearer "+str(conf.S3Token),
            "accept-encoding": "gzip",
            'user-agent': 'LA PINGA MIA'
        }
        tmp = requests.get(signed, headers=h)
        if tmp.status_code == 200:
            path = str(name)
            f = open(str(name), 'wb')
            f.write(tmp.content)
            f.close()
            return path
        else:
            return ''
    else:
        msg.edit("Error de Token Actualize Su Token OJO!")


async def create_txt(txt_list, txt_name):
    txt_content = ''
    for e in txt_list:
        txt_content += str(txt_list[e]) + '\t' + str(e) + '\n'
    txt_name = txt_name+'.txt'
    txt_file = open(txt_name, 'w')
    try:
        txt_file.write(txt_content)
    except:
        print('Error al escribir el texto ' + str(txt_name))
    txt_file.close()
    return txt_name


async def get_file_size(file):
    file_size = os.stat(file)
    return file_size.st_size


def sizeof_fmt(num, suffix='B'):
    try:
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
    except:
        return ''


def req_file_size(req):
    try:
        return int(req.headers['content-length'])
    except:
        return 0


def get_name(file):
    return str(file).split('.')[0]


def get_url_file_name(url, req):
    try:
        if "Content-Disposition" in req.headers.keys():
            return str(re.findall("filename=(.+)", req.headers["Content-Disposition"])[0])
        else:
            tokens = str(url).split('/')
            return tokens[len(tokens)-1]
    except:
        tokens = str(url).split('/')
        return tokens[len(tokens)-1]
    return ''


def fixed_name(name):
    return str(name).replace('%20', ' ')


def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitio la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
        print(str(e))


async def down_chunked_fixed(url, bot, ev, msg):
    try:
        multiFile.files.clear()
        txt_list = {}
        chunk_size = 1024 * 1024 * conf.ChunkSize
        req = requests.get(url, stream=True, allow_redirects=True)
        file_size = req_file_size(req)
        if req.status_code == 200:
            file_name = get_url_file_name(url, req)
            file_name = file_name.replace('"', "")
            file_name = fixed_name(file_name)

            await msg.edit('Descargando \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            mult_file = multiFile.MultiFile(
                get_name(file_name)+'.7z', chunk_size)
            zip = ZipFile(mult_file,  mode='w', compression=ZIP_DEFLATED)

            iterator = 1
            file_wr = open(file_name, 'wb')
            print('Descargando...')
            for chunk in req.iter_content(chunk_size=1024 * 1024 * conf.ChunkFixed):
                if chunk:
                    file_wr.write(chunk)
            file_wr.close()

            await msg.edit('Comprimiendo \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            zip.write(file_name)
            zip.close()
            mult_file.close()
            os.unlink(file_name)

            for f in multiFile.files:
                progres = await text_progres(len(txt_list), len(multiFile.files))
                await msg.edit('Subiendo \n ' + str(f) + '\n' + progres + '\n' + str(sizeof_fmt(file_size)))
                get = await upload_to_todus(f, bot, ev, msg)
                if get == '':
                    return
                txt_list[f] = get
                os.unlink(f)

            txt_file = await create_txt(txt_list, get_name(file_name))
            await bot.send_file(ev.message.chat, txt_file)
            os.unlink(txt_file)
            await msg.edit('Proceso Finalizado!')
    except Exception as e:
        await msg.edit('(down_chunked) ' + str(e))
        print(str(e))


async def down_to_tel(url, bot, ev, msg):
    try:
        multiFile.files.clear()
        txt_list = {}
        req = requests.get(url, stream=True, allow_redirects=True)
        if req.status_code == 200:
            file_size = req_file_size(req)
            file_name = get_url_file_name(url, req)
            file_name = file_name.replace('"', "")
            file_name = fixed_name(file_name)

            await msg.edit('Descargando \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            file_wr = open(file_name, 'wb')
            print('Descargando...')
            for chunk in req.iter_content(chunk_size=1024 * 1024 * conf.ChunkFixed):
                if chunk:
                    file_wr.write(chunk)
            file_wr.close()

            await msg.edit('Comprimiendo \n' + str(file_name) + '\n' + str(sizeof_fmt(file_size)))

            mult_file = multiFile.MultiFile(
                get_name(file_name)+'.7z', 1024 * 1024 * 1800)
            zip = ZipFile(mult_file,  mode='w', compression=ZIP_DEFLATED)
            zip.write(file_name)
            zip.close()
            mult_file.close()
            os.unlink(file_name)

            last_progres = ''
            for f in multiFile.files:
                f_size = await get_file_size(f)
                current_progres = 'Subiendo a Telegram \n' + \
                    str(f) + '\n' + str(sizeof_fmt(f_size))
                if last_progres != current_progres:
                    await msg.edit(current_progres)
                    last_progres = current_progres
                await bot.send_file(ev.message.chat, f)
                os.unlink(f)
    except Exception as e:
        await msg.edit('(down_chunked) ' + str(e))
        print(str(e))
    await msg.edit('Proceso Finalizado!')


async def process_message(text, bot, ev, msg):
    if '#dtel' in text:
        await down_to_tel(text.replace('#dtel ', ''), bot, ev, msg)
    elif '#dtd ' in text:
        await down_chunked_fixed(text.replace('#dtd ', ''), bot, ev, msg)
    elif '#st ' in text:
        conf.setS3Token(text.replace('#st ', ''))
        await msg.edit('El Token Se A Configurado!')
    elif '#sc ' in text:
        conf.setChunkSize(int(text.replace('#sc ', '')))
        await msg.edit('El Tamaño de Los Zip ha Cambiado!')
    elif '#gc' in text:
        await msg.edit(conf.toStr())
    elif '#acc ' in text:
        conf.AdminUsers.append(text.replace('#acc ', ''))
        await msg.edit('Le a dado Acceso a ' + text.replace('#acc ', ''))
    elif '#ban ' in text:
        if text.replace('#ban ', '') in conf.AdminUsers and text.replace('#ban ', '') != conf.AdminUsers[0]:
            conf.AdminUsers.remove(text.replace('#ban ', ''))
            await msg.edit('El Usuario ' + text.replace('#ban ', '') + ' A Sido Baneado')
        else:
            await msg.edit('Ese Usuario es Fantasma!')
    else:
        await msg.edit('Eso no se Puede Procesar!')
    pass


def get_full_file_name(file):
    tokens = file.split('.')
    name = ''
    index = 0
    for t in tokens:
        if index < len(tokens):
            name += t + '.'
        index += 1
    return name


async def process_txt(file, bot, ev, msg):
    multiFile.files.clear()
    f = open(file, 'r')
    txt = f.read()
    f.close()
    links = str(txt).split('\n')
    files = []
    baseName = ''
    for l in links:
        if l == '':
            continue
        tokens = str(l).split('\t')
        baseName = tokens[1]
        url = tokens[0]
        saveFile = download_from_todus(url, baseName, bot, ev, msg)
        files.append(saveFile)
    if len(file) > 0:
        mult_file = multiFile.MultiFile(
            get_name(baseName)+'.7z', 1024 * 1024 * 1800)
        with ZipFile(mult_file,  mode='w') as zip:
            for f in files:
                zip.write(f)
                os.unlink(f)
        mult_file.close()
        for f in multiFile.files:
            f_size = await get_file_size(f)
            await bot.send_message(ev.chat_id, 'Subiendo a Telegram \n' + str(f) + '\n' + str(sizeof_fmt(f_size)))
            await bot.send_file(ev.message.chat, f)
    pass


def clear_cache():
    try:
        files = os.listdir(os.getcwd())
        for f in files:
            if '.' in f:
                if conf.ExcludeFiles.__contains__(f):
                    print('No Se Permitio la eliminacion de '+f)
                else:
                    os.remove(f)
    except Exception as e:
        print(str(e))


async def process_tdb(file, bot, ev, msg):
    try:
        conf.tokensdb.clear()
        f = open(file, 'r')
        dbcontent = f.read()
        f.close()
        tokens = str(dbcontent).split(',')
        for t in tokens:
            if t != '':
                conf.addToken(t)
        os.unlink(file)
        await msg.edit('Se Actualizaron ' + str(len(conf.tokensdb)) + " Tokens!")
    except Exception as ex:
        print(str(ex))
    pass


async def process_file(file, bot, ev, msg):
    try:
        multiFile.files.clear()
        txt_list = {}
        chunk_size = (1024 * 1024 * conf.ChunkSize)
        file_size = await get_file_size(file)

        await msg.edit('Comprimiendo \n' + str(file) + '\n' + str(sizeof_fmt(file_size)))

        mult_file = multiFile.MultiFile(file + '.7z', chunk_size)
        zip = ZipFile(mult_file,  mode='w', compression=ZIP_DEFLATED)
        zip.write(file)
        zip.close()
        mult_file.close()

        progres = await text_progres(len(txt_list), len(multiFile.files))
        last_progres = 'Subiendo \n ' + '\n' + \
            str(progres) + '\n' + str(sizeof_fmt(file_size))
        for f in multiFile.files:
            try:
                progres = await text_progres(len(txt_list), len(multiFile.files))
                current_progres = 'Subiendo \n ' + \
                    str(f) + '\n' + str(progres) + \
                    '\n' + str(sizeof_fmt(file_size))
                if last_progres != current_progres:
                    await msg.edit(current_progres)
                    last_progres = current_progres
            except Exception as ex:
                print(str(ex))
            get = await upload_to_todus(f, bot, ev, msg)
            txt_list[f] = get
            os.unlink(f)

        txt_file = await create_txt(txt_list, file.split('.')[0])
        await bot.send_file(ev.message.chat, txt_file)
        os.unlink(txt_file)
        os.unlink(file)
        await msg.edit('Proceso Finalizado!')
    except Exception as e:
        await msg.edit(str(e))


def is_accesible(user):
    return user in conf.AdminUsers


async def processAll(ev, bot):
    try:
        if is_accesible(ev.message.chat.username):
            if conf.procesing == False:
                clear_cache()
                text = ev.message.text
                conf.procesing = True
                message = await bot.send_message(ev.chat_id, 'Procesando...')
                if ev.message.file:
                    await message.edit('Archivo Econtrado Descargando...')
                    file_name = await bot.download_media(ev.message)
                    if '.txt' in file_name:
                        await process_txt(file_name, bot, ev, message)
                    elif '.tdb' in file_name:
                        await process_tdb(file_name, bot, ev, message)
                    else:
                        await process_file(file_name, bot, ev, message)
                elif text:
                    await process_message(text, bot, ev, message)
                conf.procesing = False
            else:
                await bot.send_message(ev.chat_id, 'Estoy trabajando Espere...')
    except Exception as e:
        await bot.send_message(str(e))
        conf.procesing = False


def init():
    try:
        bot = TelegramClient(
            'bot', api_id=int(os.environ('API_ID', 11029886)),
            api_hash=os.environ('API_HASH', '4e74899bfd41879c6a4b48cf6a07f456')
        ).start(
            bot_token=os.environ('BOT_TOKEN')
        )

        @bot.on(events.NewMessage())
        async def process(ev: events.NewMessage.Event):
            await processAll(ev, bot)

        loop = asyncio.get_event_loop()
        loop.run_forever()
    except:
        init()
        conf.procesing = False


if __name__ == '__main__':
    init()
