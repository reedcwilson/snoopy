#!/usr/local/env python

from desktopmagic.screengrab_win32 import getDisplaysAsImages


def capture(directory):
    filenames = []
    for i, img in enumerate(getDisplaysAsImages()):
        filename = '{}.png'.format(i)
        filenames.append(filename)
        img.save(filename, format='png')
    return filenames


if __name__ == '__main__':
    print(capture('./'))
