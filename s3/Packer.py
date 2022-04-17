import os


def packFolder(fold, zip):
    files = os.listdir(fold)

    for f in files:
        filepath = fold+'\\'+f

        if os.path.isfile(filepath):
            zip.write(filepath, f)
            os.unlink(filepath)
        else:
            packFolder(f, zip)
