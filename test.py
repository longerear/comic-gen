d = './s/'  # 图片所在路径，结尾必须带/，在文件夹里只能有漫画的内容，不能有封面封底
name = 'output.pdf'  # 输出pdf文件名
background_color = (255, 255, 255)  # 背景颜色
cover = ''
back_cover = ''
height, width = 3564, 2520  # A4纸的像素大小

import os
from PIL import Image


# 读取文件名
def get_name(d):
    ls = os.listdir(d)
    try:
        ls.sort(key=lambda x: int(x.split('.')[0]))
    except:
        pass
    print('num:', len(ls))
    return ls


# 读取图片，计算平均宽高
def get_aw_ah(d, ls):
    h, w = 0, 0
    imgs = []
    hw = {}
    for name in ls:
        img = Image.open(d + name)
        imgs.append(img)
        w += img.width
        h += img.height
        if hw.get(img.size):
            hw[img.size] = hw[img.size] + 1
        else:
            hw[img.size] = 1
    for key in hw.keys():
        if hw[key] > len(imgs) / 2:
            aw, ah = key
            break
    if 'aw' not in dir():
        aw = w // len(imgs)
        ah = h // len(imgs)
    print('average size:', aw, ah)
    return imgs, aw, ah


# 图片数量规格化
def num_4(imgs):
    t = (len(imgs) + 2) % 4
    for i in range(4 - t):
        imgs.append(Image.new("RGB", (aw, ah), (255, 255, 255)))

    # 封面
    if not cover:
        imgs.insert(0, Image.new("RGB", (aw, ah), (255, 255, 255)))
    else:
        imgs.insert(0, Image.open(cover).convert('RGB'))

    # 封底
    if not back_cover:
        imgs.append(Image.new("RGB", (aw, ah), (255, 255, 255)))
    else:
        imgs.append(Image.open(back_cover).convert('RGB'))

    print("final num:", len(imgs))


# 计算最终一张图片的宽高
def get_tw_th(aw, ah):
    global width, height
    t = ah / aw
    if ah < aw:  # 横版，调换宽高
        height, width = width, height
        t = aw / ah
    if t > 297 / 210:  # 以高为标准
        th = height / 4
        tw = int(th / ah * aw)
        th = int(th)
    else:  # 以宽为标准
        tw = width / 4
        th = int(tw / aw * ah)
        tw = int(tw)
    print('to size:', tw, th)
    return tw, th


# 图片大小规格化
def resize(imgs, tw, th):
    print('resizing...')
    for i in range(len(imgs)):
        img = Image.new("RGB", (tw, th), background_color)
        if imgs[i].height > imgs[i].width:
            timg = imgs[i].resize((int(th / imgs[i].height * imgs[i].width), th), Image.LANCZOS)
        else:
            timg = imgs[i].resize((tw, int(tw / imgs[i].width * imgs[i].height)), Image.LANCZOS)
        img.paste(timg, ((tw - timg.width) // 2, (th - timg.height) // 2))
        imgs[i] = img
    print('resized')
    return imgs


# 在front的(w,h)处开始贴img1,img2,img_2,img_1
def paste(front, back, img1, img2, img_2, img_1, w, h):
    front.paste(img2, (w, h))
    front.paste(img_2, (w + img2.width, h))
    back.paste(img1, (width - w - img1.width, h))
    back.paste(img_1, (width - w - img1.width - img_1.width, h))
    # front.show()
    # back.show()
    # input("press any key to continue...")


# 贴图
def paste_all(imgs, tw, th):
    imgls = []
    while len(imgs) >= 32:  # 一张A4纸打印32张图片
        batch = [imgs[:16], imgs[16:32]]
        imgs = imgs[32:]
        imgls.append(Image.new("RGB", (width, height), background_color))
        imgls.append(Image.new("RGB", (width, height), background_color))
        for j in range(2):  # 一张A4纸分上下两部分
            for i in range(4):  # 每4裁、4*2=8页、4*2*2=16张图片成一组
                w = (i % 2) * 2 * tw
                h = (i // 2) * th + 2 * j * th
                paste(imgls[-2], imgls[-1], batch[j][0], batch[j][1], batch[j][-2], batch[j][-1], w, h)
                batch[j] = batch[j][2:-2]
        # imgls[-2].show()
        # imgls[-1].show()
        # input("press any key to continue...")
    # 最后不足一页的全部归为一组
    if len(imgs) > 0:
        t = (len(imgs) + 2) // 4
        imgls.append(Image.new("RGB", (width, height), background_color))
        imgls.append(Image.new("RGB", (width, height), background_color))
        for i in range(t):
            w = (i % 2) * 2 * tw
            h = (i // 2) * th
            paste(imgls[-2], imgls[-1], imgs[0], imgs[1], imgs[-2], imgs[-1], w, h)
            imgs = imgs[2:-2]
        # imgls[-2].show()
        # imgls[-1].show()
        # input("press any key to continue...")
    if th < tw:  # 横版，整张纸在转回来
        for i in range(len(imgls)):
            imgls[i] = imgls[i].transpose(Image.ROTATE_90)
            # imgls[i].show()
    return imgls


if __name__ == "__main__":
    ls = get_name(d)
    imgs, aw, ah = get_aw_ah(d, ls)
    num_4(imgs)
    tw, th = get_tw_th(aw, ah)
    print(imgs[0].size)
    imgs = resize(imgs, tw, th)
    print(imgs[0].size)
    imgls = paste_all(imgs, tw, th)
    imgls[0].save(name, 'pdf', save_all=True, append_images=imgls[1:])
