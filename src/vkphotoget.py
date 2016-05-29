#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2016, Durachenko Aleksey V. <durachenko.aleksey@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import json
import datetime
import argparse
import shutil
import time
import urllib.request
import urllib.parse
import sys
import shlex
import re


def version():
    return 'v0.1.0'


def description():
    return 'Downloading the photos from the VKontakte social network'


def create_parser():
    parser = argparse.ArgumentParser(description=description())
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + version())
    parser.add_argument('--verbose', action='store_true',
                        help='print various debugging information')
    parser.add_argument('--access_token', action='store', default=None,
                        help='your access token')
    parser.add_argument('--dst', action='store', default="",
                        help='the output directory')
    parser.add_argument('url', help='the url of the photo album')
    return parser.parse_args()


def api_version():
    return "5.52"


def api_call(query, access_token=None, verbose=False):
    url = "https://api.vk.com/method/" + query
    url += "&v=%s" % (api_version())
    if access_token is not None:
        url += "&access_token=%s" % (access_token,)
    while True:
        if verbose:
            print("Query: %s" (url,))
        data = json.loads(urllib.request.urlopen(url).readall().decode('utf-8'))
        if "error" in data:
            # too many queries per second. wait and retry
            if data["error"]["error_code"] == 6:
                time.sleep(1)
                continue
            if verbose:
                print("Query: %s" (url,))
            return None
        return data["response"]


# return single response
def api_single_query(query, access_token=None, verbose=False):
    return api_call(query, access_token, verbose)


# return list of response
def api_multi_query(query, item_per_page, access_token=None, verbose=False):
    pages = []
    offset = 0
    while True:
        page_query = query + "&offset=%d&count=%d" % (offset, item_per_page)
        response = api_call(page_query, access_token, verbose)
        if response is None:
            return None
        pages.append(response)
        if response['count'] <= offset + item_per_page:
            break
        offset += item_per_page
    return pages


def api_user_name(user_id, access_token=None, verbose=False):
    result = api_single_query("users.get?user_ids=%s" % (user_id,),
                              access_token, verbose)
    return result[0]["first_name"] + " " + result[0]["last_name"]


def api_group_name(group_id, access_token=None, verbose=False):
    group_id = abs(int(group_id))
    result = api_single_query("groups.getById?group_ids=%s" % (group_id,),
                              access_token, verbose)
    return result[0]["name"]


def api_album_title_and_desc(owner_id, album_id, access_token=None, verbose=False):
    result = api_single_query(
            "photos.getAlbums?"
            "owner_id=%s&"
            "album_ids=%s" % (owner_id, album_id,), access_token, verbose)
    return {
        "title": result["items"][0]["title"],
        "desc": result["items"][0]["description"]
    }


def api_album_tags(owner_id, photo_id, access_token=None, verbose=False):
    return []
    # the code below is completely works but currently tags not saved to the jpeg
    #
    # if access_token is None:
    #     return []
    # result = api_single_query(
    #     "photos.getTags?"
    #     "owner_id=%s&"
    #     "photo_id=%s" % (owner_id, photo_id,), access_token, verbose)
    # if result is None:
    #     print("Can't fetch the tags. Access Denied!")
    #     return []
    # tags = []
    # for item in result:
    #     tags.append({
    #         "name": item["tagged_name"],
    #         "x1": item["x"],
    #         "y1": item["y"],
    #         "x2": item["x2"],
    #         "y2": item["y2"]
    #     })
    # return tags


# return list of photo objects:
# the object fields:
# - artist
# - album_title
# - album_desc
# - desc
# - date
# - lat (may not exists)
# - lon (may not exists)
# - link
# - tags - list of objects
#   - name
#   - x1
#   - y1
#   - x2
#   - y2
def api_photos_get(owner_id, album_id, access_token=None, verbose=False):
    photos_pages = api_multi_query(
            "photos.get?"
            "owner_id=%s&"
            "album_id=%s&"
            "rev=0&"
            "extended=1" % (owner_id, album_id,),
            1000, access_token, verbose)
    authors = dict()
    albums = dict()
    photos = []
    for photos_page in photos_pages:
        for item in photos_page["items"]:
            photo = dict()
            photo["date"] = item["date"]
            # desc
            photo["desc"] = item["text"]
            # gps coordinate
            if "lat" in item:
                photo["lat"] = item["lat"]
            if "long" in item:
                photo["lon"] = item["long"]
            # best image size
            if "photo_2560" in item:
                photo["link"] = item["photo_2560"]
            elif "photo_1280" in item:
                photo["link"] = item["photo_1280"]
            elif "photo_807" in item:
                photo["link"] = item["photo_807"]
            elif "photo_604" in item:
                photo["link"] = item["photo_604"]
            elif "photo_130" in item:
                photo["link"] = item["photo_130"]
            elif "photo_75" in item:
                photo["link"] = item["photo_75"]
            else:
                photo["link"] = None
            # owner name
            if "user_id" not in item:
                item["user_id"] = item["owner_id"]
            if item["user_id"] not in authors:
                if item["user_id"] == 100:
                    authors[item["user_id"]] = api_group_name(owner_id, access_token, verbose)
                else:
                    authors[item["user_id"]] = api_user_name(item["user_id"], access_token, verbose)
            photo["artist"] = authors[item["user_id"]]
            # album name and description
            if owner_id + "_" + album_id not in albums:
                albums[owner_id + "_" + album_id] = api_album_title_and_desc(owner_id, album_id, access_token, verbose)
            photo["album_title"] = albums[owner_id + "_" + album_id]["title"]
            photo["album_desc"] = albums[owner_id + "_" + album_id]["desc"]
            # tags
            if int(item["tags"]["count"]) > 0:
                photo["tags"] = api_album_tags(owner_id, item["id"], access_token, verbose)
            else:
                photo["tags"] = []
            photos.append(photo)
    return photos


def filename_from_photo(photo, dst_dir):
    return os.path.join(dst_dir,
                        str(photo["date"]) +
                        urllib.parse.urlparse(photo["link"]).path.replace("/", "_"))


def download_photo(url, dst_filename):
    dirname = os.path.dirname(dst_filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    try:
        tmp_filename, h = urllib.request.urlretrieve(url)
        if os.path.getsize(tmp_filename) < 1024:
            return False
        shutil.move(tmp_filename, dst_filename)
        return True
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        return False


def apply_metadata(dst_filename, photo, verbose=False):
    cmd = "exiftool" +                                          \
          " -overwrite_original" +                              \
          " -artist=" + shlex.quote(photo["artist"]) +          \
          " -title=" + shlex.quote(photo["album_title"]) +      \
          " -description=" + shlex.quote(photo["desc"]) +       \
          " -AllDates=" + shlex.quote(
            datetime.datetime.fromtimestamp(
                    int(photo["date"])).strftime("%Y:%m:%d %H:%M:%S")) + \
          " " + dst_filename
    if verbose:
        print("Execute: %s" % (cmd,))
    os.system(cmd)


def extract_owner_and_album_from_url(url):
    regexp = "(.{0,})album([-]{0,1}[0-9]{1,})_([0-9]{1,})(.{0,})"
    m = re.match(regexp, url)
    if m is None:
        print("Can't parse URL")
        sys.exit(1)
    return {
        "owner": m.group(2),
        "album": m.group(3)
    }


def main():
    parser = create_parser()
    access_token = parser.access_token
    verbose = parser.verbose
    dst_dir = parser.dst

    # try to read access token from config file
    if access_token is None:
        vk_filename = os.path.join(os.path.expanduser("~"), ".vk_access_token")
        if os.path.exists(vk_filename):
            access_token = open(vk_filename).readline().strip()

    value = extract_owner_and_album_from_url(parser.url)
    owner_id = value["owner"]
    album_id = value["album"]

    photos = api_photos_get(owner_id, album_id, access_token, verbose)
    current_photo_index = 1
    for photo in photos:
        print("Downloading the photo: %s of %s..." % (current_photo_index, len(photos),))
        dst_filename = filename_from_photo(photo, dst_dir)
        if not download_photo(photo["link"], dst_filename):
            print("... Failed!")
        else:
            apply_metadata(dst_filename, photo, verbose)
        current_photo_index += 1


if __name__ == "__main__":
    main()
