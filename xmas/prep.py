from PIL import Image
src='/mnt/user-data/uploads/'
m={'snowman':'c7853b9f-image.png','santa':'bd4c0780-image.png','reindeer':'630d5403-image.jpg','bear':'072ad6e8-image.png'}
for k,f in m.items():
    im=Image.open(src+f)
    if im.mode=='RGBA':
        bg=Image.new('RGB',im.size,'white'); bg.paste(im,mask=im.split()[3]); im=bg
    im=im.convert('RGB').resize((2400,2400),Image.LANCZOS)
    im.save(f'img/{k}.jpg',quality=92)
