#!/usr/bin/python
from __future__ import print_function
import sys
import os
import hashlib

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


MOVIE_EXTS = (".avi", ".mkv", ".mp4", ".wmv")
SUB_EXTS = (".srt", ".sub", ".mpl")

def find_movies(movie_dir):
    # Traverse the directory tree and select all movie files
    movies = []
    subtitles = set()

    for root, _, files in os.walk(movie_dir):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext.lower() in SUB_EXTS:
                subtitles.add(os.path.join(root, name))
            if ext.lower() in MOVIE_EXTS:
                movies.append(os.path.join(root, f))

    return filter(lambda m : os.path.splitext(m)[0] not in subtitles, movies)


def search_subtitles(moviefiles, lang_id="en"):
    '''Search OpenSubtitles for matching subtitles'''
    template = "http://napiprojekt.pl/unit_napisy/dl.php?l=%s&f=%s&t=%s&v=dreambox&kolejka=false&nick=&pass=&napios=Linux"

    print("NapiProjekt.pl Subtitle Downloader".center(78))
    print("===================================".center(78))

    for movie in moviefiles:

        print("Found movie: " + movie, end=" ")
        file_md5, file_hash = hashFile(movie)
        query = template % (lang_id.upper(), file_md5, file_hash)

        url = urlopen(query).read()
        if not url or url == "NPc0" or len(url) < 10:
            print("[ERR]")
            continue
        print("[OK]")

        basename = os.path.splitext(movie)[0]
        zname = basename + ".srt"
        file = open(zname, "wb")
        file.write(url)
        file.close()


def hashFile(name):
    '''Calculates the hash value of a movie.

    '''

    hash_sample_size = 10485760
    # thanks to gim,krzynio,dosiu,hash 2oo8 for this function
    def secondaryHash(data):
        idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
        mul = [   2,   2,    5,   4,   3 ]
        add = [   0, 0xd, 0x10, 0xb, 0x5 ]

        b = []
        for i in range(len(idx)):
            a = add[i]
            m = mul[i]
            i = idx[i]

            t = a + int(data[i], 16)
            v = int(data[t:t+2], 16)
            b.append( ("%x" % (v*m))[-1] )

        return ''.join(b)

    try:
        with open(name, "rb") as f:
            filesize = os.path.getsize(name)

            if filesize < hash_sample_size:
                raise Exception("Not enough data to hash")
            data = f.read(hash_sample_size)
            d = hashlib.md5(data).hexdigest()

        return (d, secondaryHash(d))
    except:
        print ("Error")
        return ("","")


if __name__ == '__main__':
    import os
    cwd = os.getcwd()
    if len(sys.argv) > 1:
        cwd = sys.argv[1]
    # in order to download non english subtitles add second argument
    # second language argument such as 'fr' or 'po'
    file_list = find_movies(cwd)
    search_subtitles(file_list, 'pl')
