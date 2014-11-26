import argparse
import urllib
import re

def get_firefox_version(url):
    files = urllib.urlopen(url).read()
    m = re.search('(firefox-[\d\.a-z]+.\w\w-\w\w)\.', files)
    if m:
        return m.groups()[0]
    m = re.search('(fennec-[\d\.a-z]+)\.', files)
    if m:
        return m.groups()[0]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                        help="URL to directory containing firefox installers",
                        action="store")
 
    args = parser.parse_args()
    print(get_firefox_version(args.url))
