import math
import re
from pathlib import Path
from PIL import Image

import config

IMAGE_DIRECTORY = config.IMAGE_DIRECTORY
OUTPUT_CSS = config.OUTPUT_CSS
OUTPUT_HTML = config.OUTPUT_HTML
PAGE_TITLE = config.PAGE_TITLE
THUMBNAIL_DIRECTORY = config.THUMBNAIL_DIRECTORY
THUMBNAIL_SIZE = config.THUMBNAIL_SIZE

def get_images(image_directory, thumbnail_directory, thumbnail_size):
    thumbnail_directory = Path(thumbnail_directory)

    for file in [file for file in thumbnail_directory.glob('*')]:
        file.unlink()

    thumbnail_directory.mkdir(mode=0o755, exist_ok=True)

    files = [file for file in Path(image_directory).glob('*')]

    images = []

    for file in files:
        thumbnail_name = Path(thumbnail_directory, file.stem + '.jpg')

        image = Image.open(file)
        image.thumbnail(THUMBNAIL_SIZE)

        top_left = (0, 0)

        if image.width < THUMBNAIL_SIZE[0]:
            top_left = (math.floor(abs(image.width - THUMBNAIL_SIZE[0]) / 2), top_left[1])

        if image.height < THUMBNAIL_SIZE[1]:
            top_left = (top_left[0], math.floor(abs(image.height - THUMBNAIL_SIZE[1]) / 2))

        final_image = Image.new('RGB', THUMBNAIL_SIZE, (0, 0, 0))
        final_image.paste(image, top_left)
        final_image.save(thumbnail_name, 'jpeg')

        if '_' in file.stem:
            description = file.stem.split('_', maxsplit=1)[1]
        else:
            description = file.stem

        images.append({
                'path': str(file),
                'thumbnail': thumbnail_name,
                'description': description,
                'stem': file.stem
            })

    def get_image_file_number(image):
        if re.match(r'^(\d+)', image['stem']) is not None:
            return int(re.split(r'^(\d+)', image['stem'])[1])
        else:
            return 999

    images = sorted(images, key=get_image_file_number)

    return images

def write_html(file, images):
    file.write(f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{PAGE_TITLE}</title>
  <link rel="stylesheet" type="text/css" href="album.css">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
</head>
<body>
  <h1>{PAGE_TITLE}</h1>
  <div id="album">
    \
''')

    # write thumbnails
    for image, idx in zip(images, range(1, len(images) + 1)):
        file.write(f'''\
<p id="thumbnail-{idx}" class="thumbnail"><img src="{image['thumbnail']}" alt="{image['description']}" width="{THUMBNAIL_SIZE[0]}" height="{THUMBNAIL_SIZE[1]}"></p>\
''')

    file.write(f'''\

    <div id="large-view">
      <p id="instructions" class="image">Hover over an image</p>
''')

    # write images
    for image, idx in zip(images, range(1, len(images) + 1)):
        file.write(f'''\
      <p id="image-{idx}" class="image"><img src="{image['path']}" alt="{image['description']}"><br>{image['description']}</p>
''')

    file.write(f'''\
    </div>
  </div>
</body>
</html>
''')

def write_css(file, images):
    file.write('''\
@media print {
    body {
        font-family: sans-serif;
    }

    .thumbnail {
        display: none;
    }

    #instructions {
        display: none;
    }

    .image img {
        max-width: 100%;
        margin-bottom: 1em;
    }
}

@media
    screen and (max-width: 768px),

    /* Tablets and smartphones */
    screen and (hover: none)
{
    body {
        background: #333;
        color: #eee;
        font-family: sans-serif;
        margin: 1em;
        padding: 0;
    }

    h1 {
        margin-top: 0;
    }

    .thumbnail {
        display: none;
    }

    #instructions {
        display: none;
    }

    .image:nth-child(2) img {
        margin-top: 0;
    }

    .image img {
        max-width: calc(100vw - 3em);
    }
}

@media
    screen and (min-width: 769px) and (hover: hover),

    /* IE10 and IE11 (they don't support (hover: hover) */
    screen and (min-width: 769px) and (-ms-high-contrast: none),
    screen and (min-width: 769px) and (-ms-high-contrast: active)
{
    body {
        background: #333;
        color: #eee;
        font-family: sans-serif;
        margin: 2em 60% 2em 4em;
        padding: 0;
    }

    .album {
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
    }

    .thumbnail {
        display: inline-block;;
        margin: 0 .5em .2em 0;
    }

    .image {
        background: #333;
        display: none;
        position: fixed;
        top: 2em;
        left: 40%;
        text-align: center;
        height: 90vh;
        width: calc(60% - 4em);
    }

    .image img {
        display: block;
        max-height: 92%;
        max-width: 100%;
        margin: 0 auto;
    }

    #instructions {
        display: block;
        top: 4em;
    }

''')

    if len(images) > 0:
        for idx in range(1, len(images) + 1):
            file.write(f'''\
    #thumbnail-{idx}:hover ~ #large-view #image-{idx}\
''')

            if idx < len(images):
                file.write('''\
,
''')

        file.write('''\
 {
        display: block;
    }
''')

    file.write('''\
}
''')

def main():
    out_html = open(OUTPUT_HTML, 'w')
    out_css = open(OUTPUT_CSS, 'w')

    images = get_images(IMAGE_DIRECTORY, THUMBNAIL_DIRECTORY, THUMBNAIL_SIZE)

    write_html(out_html, images)
    write_css(out_css, images)

    out_html.close()
    out_css.close()

if __name__ == '__main__':
    main()