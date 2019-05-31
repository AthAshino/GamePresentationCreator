# coding=utf-8

import optparse
from datetime import date

import BeautifulSoup
import requests
import html2bbcode
import bbcode

VERSION = '1.0'


class VALUE_TO_CHANGE:
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
    FROM_ISO_WITH_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Monter l'iso. Exécuter setup.exe." \
                          "[color=#e69138]2)[/color] Installer le jeu" \
                          "[color=#e69138]3)[/color] Copiez le contenu du dossier Crack dans le dossier du jeu" \
                          "[color=#e69138]4)[/color] Jouer[/size]" \
                          "[/size]"
    
    FROM_ISO_WITHOUT_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Monter l'iso. Exécuter setup.exe." \
                             "[color=#e69138]2)[/color] Installer le jeu" \
                             "[color=#e69138]3)[/color] Jouer[/size]" \
                             "[/size]"
    
    FROM_EXE_WITH_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Exécuter setup.exe." \
                          "[color=#e69138]2)[/color] Installer le jeu" \
                          "[color=#e69138]3)[/color] Copiez le contenu du dossier Crack dans le dossier du jeu" \
                          "[color=#e69138]4)[/color] Jouer[/size]" \
                          "[/size]"
    
    FROM_EXE_WITHOUT_CRACK = "[size=100][color=#e69138][size=100]1)[/size][/color][size=100] Exécuter setup.exe." \
                             "[color=#e69138]2)[/color] Installer le jeu" \
                             "[color=#e69138]3)[/color] Jouer[/size]" \
                             "[/size]"


IS_STANDALONE = "[b][size=200]Cette version est standalone, elle contient le jeu et tout son contenu jusqu'au %s ![/size][/b]"


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
        txt = str(item.text)
        for lang in available_langs:
            if txt in available_langs[lang]['trad']:
                actual_lang = lang
                break
        else:
            if '&#10004;' not in txt:
                actual_lang = ''
            else:
                etc = True
        if '&#10004;' in txt and available_langs.get(actual_lang, None):
            available_langs[actual_lang]['available'] = True
    final_text = ', '.join([LANGUAGE.LANGS.get(lang) for lang in available_langs if available_langs[lang]['available']])
    if etc:
        final_text = "%s, %s" % (final_text, LANGUAGE.LANGS.get('ETC'))
    return final_text


def get_informations_from_steam(link):
    # Let's start to make some illegal cookies
    cookies = {'birthtime': '568022401', 'mature_content': '1'}
    
    # GO !
    r = requests.get(link, cookies=cookies)
    html = r.content
    
    soup = BeautifulSoup.BeautifulSoup(html)
    
    # Now we need to find some informations about the game, thanks god, steam developers name properly all of their informations <3
    VALUE_TO_CHANGE.GAME_HEADER_IMG = soup.find('img', {'class': 'game_header_image_full'}).get('src', 'NO_IMAGE_FOUND')
    VALUE_TO_CHANGE.GAME_TITLE = soup.find('div', {'class': 'apphub_AppName'}).text
    genders = soup.find('div', {'class': 'glance_tags popular_tags'})
    VALUE_TO_CHANGE.GAME_GENDER = ', '.join([txt.text for txt in get_tab_without_navigable_string(genders.contents)[1:5]])
    VALUE_TO_CHANGE.GAME_DEVELOPER = ', '.join([txt.text for txt in get_tab_without_navigable_string(soup.find('div', {'id': 'developers_list'}).contents)])
    VALUE_TO_CHANGE.GAME_EDITOR = ', '.join([txt.text for txt in get_tab_without_navigable_string(soup.findAll('div', {'class': 'dev_row'})[3].contents[1:])])
    VALUE_TO_CHANGE.GAME_RELEASE_DATE = soup.find('div', {'class': 'date'}).text
    VALUE_TO_CHANGE.MINIMAL_CONF = '\n'.join([txt.text for txt in get_tab_without_navigable_string(soup.find('div', {'class': 'game_area_sys_req_leftCol'}).find("ul").find("ul").contents)])
    VALUE_TO_CHANGE.RECOMMENDED_CONF = '\n'.join([txt.text for txt in get_tab_without_navigable_string(soup.find('div', {'class': 'game_area_sys_req_rightCol'}).find("ul").find("ul").contents)])
    VALUE_TO_CHANGE.GAME_DESCRIPTION = '\n'.join([txt.text for txt in get_tab_without_navigable_string(soup.find('div', {'class': 'game_area_description'}).contents)])
    VALUE_TO_CHANGE.GAME_IMG1 = get_tab_without_navigable_string(soup.findAll('div', {'class': 'highlight_strip_item highlight_strip_screenshot'})[0].contents)[0].get('src', 'NO_IMAGE_FOUND')
    VALUE_TO_CHANGE.GAME_IMG2 = get_tab_without_navigable_string(soup.findAll('div', {'class': 'highlight_strip_item highlight_strip_screenshot'})[1].contents)[0].get('src', 'NO_IMAGE_FOUND')
    VALUE_TO_CHANGE.INTERFACE_LANG = get_language_from_html(soup.find('table', {'class': 'game_language_options'}).findAll('td'))


def create_presentation(dest):
    template_file = open('pres_template', 'r')
    template = template_file.read()
    parser = bbcode.Parser()
    
    for value in dir(VALUE_TO_CHANGE):
        if callable(getattr(VALUE_TO_CHANGE, value)):
            continue
        to_add = str(parser.feed(getattr(VALUE_TO_CHANGE, value, '')))
        template.replace("\%%s\%" % value, to_add)
    
    file_to_write = open(dest, 'w+')
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
    parser.add_option('--is_standalone', action="store_true", dest='is_standalone', help='Is your version standalone and contains dlc/update ?')
    
    opts, args = parser.parse_args()
    
    if not opts.release_name:
        print "The release name is needed."
    if not opts.steam_link:
        print "The steam_link is needed."
    if not opts.files_size:
        print "The file size is needed."
    if opts.file_format not in ['ISO', 'EXE']:
        print "The %s format doesn't exist" % opts.file_format
    
    steam_link = opts.steam_link
    dest = opts.dest
    
    VALUE_TO_CHANGE.RELEASE_NAME = opts.release_name
    VALUE_TO_CHANGE.FILE_NUMBERS = opts.files_numbers
    VALUE_TO_CHANGE.GAME_SIZE = opts.files_size
    VALUE_TO_CHANGE.INSTALL_FORMAT = opts.file_format
    VALUE_TO_CHANGE.CRACK_STATE = CRACKSTATE.INCLUDED if not opts.drm_free else CRACKSTATE.DRMFREE
    if opts.drm_free:
        if opts.file_format == 'ISO':
            VALUE_TO_CHANGE.INSTALL_GUIDE = INSTALLGUIDE.FROM_ISO_WITHOUT_CRACK
        elif opts.file_format == 'EXE':
            VALUE_TO_CHANGE.INSTALL_GUIDE = INSTALLGUIDE.FROM_EXE_WITHOUT_CRACK
    else:
        if opts.file_format == 'ISO':
            VALUE_TO_CHANGE.INSTALL_GUIDE = INSTALLGUIDE.FROM_ISO_WITH_CRACK
        elif opts.file_format == 'EXE':
            VALUE_TO_CHANGE.INSTALL_GUIDE = INSTALLGUIDE.FROM_EXE_WITH_CRACK
    if opts.is_standalone:
        VALUE_TO_CHANGE.STANDALONE = IS_STANDALONE % date.today()
    VALUE_TO_CHANGE.GAME_URL = steam_link
    
    get_informations_from_steam(steam_link)
    
    create_presentation(dest)
    print ("IT'S DONE !")
