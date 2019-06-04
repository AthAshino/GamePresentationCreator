# coding=utf-8
import codecs
import optparse
import re
from datetime import date

import bs4 as BeautifulSoup
import requests
from dependencies.html2phpbbcode.parser import HTML2PHPBBCode as HTML2BBCode

VERSION = '1.0'


class ValueToChange:
    STANDALONE = ''
    RELEASE_NAME = ''
    GAME_URL = ''
    GAME_HEADER_IMG = ''
    GAME_TITLE = ''
    GAME_GENDER = ''
    GAME_DEVELOPER = ''
    GAME_EDITOR = ''
    GAME_RELEASE_DATE = ''
    MINIMAL_CONF = ''
    RECOMMENDED_CONF = ''
    GAME_DESCRIPTION = ''
    GAME_IMG1 = ''
    GAME_IMG2 = ''
    INSTALL_FORMAT = ''
    INTERFACE_LANG = ''
    CRACK_STATE = ''
    INSTALL_GUIDE = ''
    GAME_SIZE = ''
    FILE_NUMBERS = ''


class LANGUAGE:
    LANGS = {
        'FR' : 'Français [img]https://img.streetprez.com/flag/fr_FR.png[/img]',
        'DE' : 'Allemand [img]http://www.ledrakkarnoir.com/prez/images/flag_lang/Allemand.png[/img]',
        'EN' : 'Anglais [img]https://i.goopics.net/NDNVg.png[/img]',
        'ETC': 'ETC...'
    }


class CRACKSTATE:
    INCLUDED = 'Inclus'
    DRMFREE = 'Pas de crack : DRM Free'


class INSTALLGUIDE:
    FROM_ISO_WITH_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Monter l'iso. Exécuter setup.exe.<br>" \
                          "[color=#e69138]2)[/color] Installer le jeu<br>" \
                          "[color=#e69138]3)[/color] Copiez le contenu du dossier Crack dans le dossier du jeu<br>" \
                          "[color=#e69138]4)[/color] Jouer[/size]<br>" \
                          "[/size]"
    
    FROM_ISO_WITHOUT_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Monter l'iso. Exécuter setup.exe.<br>" \
                             "[color=#e69138]2)[/color] Installer le jeu<br>" \
                             "[color=#e69138]3)[/color] Jouer[/size]<br>" \
                             "[/size]"
    
    FROM_EXE_WITH_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Exécuter setup.exe.<br>" \
                          "[color=#e69138]2)[/color] Installer le jeu<br>" \
                          "[color=#e69138]3)[/color] Copiez le contenu du dossier Crack dans le dossier du jeu<br>" \
                          "[color=#e69138]4)[/color] Jouer[/size]<br>" \
                          "[/size]"
    
    FROM_EXE_WITHOUT_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Exécuter setup.exe.<br>" \
                             "[color=#e69138]2)[/color] Installer le jeu<br>" \
                             "[color=#e69138]3)[/color] Jouer[/size]<br>" \
                             "[/size]"


IS_STANDALONE = "[b][size=200]Cette version est standalone, elle contient le jeu et tout son contenu jusqu'au %s ![/size][/b]<br><br>"


def get_tab_without_navigable_string(my_list):
    for item in my_list:
        if type(item) == BeautifulSoup.NavigableString:
            my_list.remove(item)
    return my_list


def get_language_from_html(html):
    available_langs = {'FR': {'trad': ['Français', 'French'], 'available': False}, 'EN': {'trad': ['English', 'Anglais'], 'available': False}, 'DE': {'trad': ['German', 'Allemand'], 'available': False}}
    actual_lang = ''
    etc = False
    for item in html:
        txt = str(item.text).replace('\n', '').replace('\r', '').replace('\t', '')
        for lang in available_langs:
            if txt in available_langs[lang]['trad']:
                actual_lang = lang
                break
        else:
            if '✔' not in txt:
                actual_lang = ''
            else:
                etc = True
        if '✔' in txt and available_langs.get(actual_lang, None):
            available_langs[actual_lang]['available'] = True
    final_text = ', '.join([LANGUAGE.LANGS.get(lang) for lang in available_langs if available_langs[lang]['available']])
    if etc and available_langs['FR']['available']:
        final_text = "%s, %s" % (final_text, LANGUAGE.LANGS.get('ETC'))
    return final_text


def steam_image_to_1080p(string):
    match = re.search('([0-9]+x[0-9]+)', string)
    return string.replace(match[0], '1920x1080')


def get_game_description(desc_list):
    to_return = ""
    i = 0
    while i < len(desc_list):
        desc_part = str(desc_list[i])
        future_desc_part = str(desc_list[i + 1]) if i + 1 < len(desc_list) else ""
        if to_return:
            to_return = "%s<br>%s" % (to_return, desc_part)
        else:
            to_return = desc_part
        if not i == 0 and (future_desc_part.startswith('<h1') or future_desc_part.startswith('<h2') or future_desc_part.startswith('<h3')):
            to_return = "%s<br>" % to_return
        i += 1
    return to_return


def get_informations_from_steam(link):
    # Let's start to make some illegal cookies
    cookies = {'birthtime': '568022401', 'mature_content': '1'}
    headers = {"Accept-Language": "fr-FR,fr"}
    # GO !
    r = requests.get(link, cookies=cookies, headers=headers)
    html = r.content
    
    soup = BeautifulSoup.BeautifulSoup(html)
    
    # Now we need to find some informations about the game, thanks god, steam developers name properly all of their informations <3
    ValueToChange.GAME_HEADER_IMG = soup.find('img', {'class': 'game_header_image_full'}).get('src', 'NO_IMAGE_FOUND')
    ValueToChange.GAME_TITLE = soup.find('div', {'class': 'apphub_AppName'}).text
    genders = get_tab_without_navigable_string(soup.find('div', {'class': 'glance_tags popular_tags'}).contents)
    ValueToChange.GAME_GENDER = ', '.join([str(txt).strip().replace('\r', '').replace('\n', '').replace('\t', '') for txt in genders[1:5]])
    ValueToChange.GAME_DEVELOPER = ', '.join([str(txt).strip() for txt in get_tab_without_navigable_string(soup.find('div', {'id': 'developers_list'}).contents)])
    ValueToChange.GAME_EDITOR = ', '.join([str(txt).strip() for txt in get_tab_without_navigable_string(soup.findAll('div', {'class': 'dev_row'})[3].contents[2:])])
    ValueToChange.GAME_RELEASE_DATE = soup.find('div', {'class': 'date'}).text
    ValueToChange.MINIMAL_CONF = '\n'.join([str(txt).strip() for txt in get_tab_without_navigable_string(soup.find('div', {'class': 'game_area_sys_req_leftCol'}).find("ul").find("ul").contents)])
    ValueToChange.RECOMMENDED_CONF = '\n'.join([str(txt).strip() for txt in get_tab_without_navigable_string(soup.find('div', {'class': 'game_area_sys_req_rightCol'}).find("ul").find("ul").contents)])
    ValueToChange.GAME_DESCRIPTION = get_game_description(soup.find('div', {'id': 'game_area_description', 'class': 'game_area_description'}).contents)
    ValueToChange.GAME_IMG1 = steam_image_to_1080p(get_tab_without_navigable_string(soup.findAll('div', {'class': 'highlight_strip_item highlight_strip_screenshot'})[0].contents)[0].get('src', 'NO_IMAGE_FOUND'))
    ValueToChange.GAME_IMG2 = steam_image_to_1080p(get_tab_without_navigable_string(soup.findAll('div', {'class': 'highlight_strip_item highlight_strip_screenshot'})[1].contents)[0].get('src', 'NO_IMAGE_FOUND'))
    ValueToChange.INTERFACE_LANG = get_language_from_html(soup.find('table', {'class': 'game_language_options'}).findAll('td'))


def create_presentation(destination_file):
    template_file = codecs.open('pres_template', 'r', "utf-8")
    template = template_file.read()
    html_parser = HTML2BBCode()
    
    for value in [attr for attr in dir(ValueToChange) if not callable(getattr(ValueToChange, attr)) and not attr.startswith("__")]:
        if value == '__doc__' or value == '__dict__' or value == '__class__':
            continue
        to_add = str(html_parser.feed(getattr(ValueToChange, value, '')))
        to_replace = "%%%s%%" % value
        template = template.replace(to_replace, to_add)

    file_to_write = codecs.open(destination_file, 'w+', "utf-8")
    file_to_write.write(template)


if __name__ == '__main__':
    parser = optparse.OptionParser("%prog ", version="%prog: " + VERSION, description='This tool help you to create french presentation for games torrents from steam link')
    parser.add_option('--name', dest='release_name', help="Name of your release")
    parser.add_option('-l', '--link', dest='steam_link', help="Steam link of your game")
    parser.add_option('-s', '--size', dest="files_size", help="Size of your files")
    parser.add_option('-n', '--files-numbers', dest="files_numbers", type='int', help="How many files your release is composed. 1 by default", default=1)
    parser.add_option('-f', '--format', dest='file_format', help="Format of your game file(s). Can be ISO or EXE. Default = ISO", default="ISO")
    parser.add_option('--drm-free', dest='drm_free', action="store_true", help="Does your release=")
    parser.add_option('-d', '--dest', dest='dest', help="Destination file, default = ./final_presentation.txt", default="./final_presentation.txt")
    parser.add_option('--is-standalone', action="store_true", dest='is_standalone', help='Is your version standalone and contains dlc/update ?')
    parser.add_option('--is-french', action="store_true", dest="is_french")
    
    opts, args = parser.parse_args()
    
    if not opts.release_name:
        print("The release name is needed.")
    if not opts.steam_link:
        print("The steam_link is needed.")
    if not opts.files_size:
        print("The file size is needed.")
    if opts.file_format not in ['ISO', 'EXE']:
        print("The %s format doesn't exist" % opts.file_format)

    steam_link = opts.steam_link
    if opts.is_french:
        steam_link = "%sl=french" % steam_link
    dest = opts.dest
    
    ValueToChange.RELEASE_NAME = opts.release_name
    ValueToChange.FILE_NUMBERS = str(opts.files_numbers)
    ValueToChange.GAME_SIZE = opts.files_size
    ValueToChange.INSTALL_FORMAT = opts.file_format
    ValueToChange.CRACK_STATE = CRACKSTATE.INCLUDED if not opts.drm_free else CRACKSTATE.DRMFREE
    if opts.drm_free:
        if opts.file_format == 'ISO':
            ValueToChange.INSTALL_GUIDE = INSTALLGUIDE.FROM_ISO_WITHOUT_CRACK
        elif opts.file_format == 'EXE':
            ValueToChange.INSTALL_GUIDE = INSTALLGUIDE.FROM_EXE_WITHOUT_CRACK
    else:
        if opts.file_format == 'ISO':
            ValueToChange.INSTALL_GUIDE = INSTALLGUIDE.FROM_ISO_WITH_CRACK
        elif opts.file_format == 'EXE':
            ValueToChange.INSTALL_GUIDE = INSTALLGUIDE.FROM_EXE_WITH_CRACK
    if opts.is_standalone:
        ValueToChange.STANDALONE = IS_STANDALONE % date.today()
    ValueToChange.GAME_URL = steam_link
    
    get_informations_from_steam(steam_link)
    
    create_presentation(dest)
    print ("IT'S DONE !")
