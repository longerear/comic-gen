d = './哆啦A梦/'  # 图片所在路径，结尾必须带/，在文件夹里只能有漫画的内容，不能有封面封底
name = 'output.pdf'  # 输出pdf文件名
background_color = (255, 255, 255)  # 背景颜色
cover = './封面.png'
back_cover = './封底.png'
height, width = 3508, 2480  # A4纸的像素大小
th, tw = height // 4, width // 4
t = th / tw

import os
from PIL import Image
from PIL.Image import ROTATE_90


# 读取文件名
def get_name(d):
    ls = os.listdir(d)
    try:
        ls.sort(key=lambda x: int(x.split('.')[0]))
    except:
        pass
    print('num:', len(ls))
    return ls


# 读取图片，并将大小规格化
def get_imgs(d, ls):
    imgs = []
    for name in ls:
        img = Image.open(d + name)

        # 横版变竖版
        if img.height < img.width:
            img = img.transpose(ROTATE_90)

        # 等比例缩小适应
        if img.height / img.width > t:  # 图片比标准的高
            img = img.resize((int(img.width * th / img.height), th))
        else:
            img = img.resize((tw, int(img.height * tw / img.width)))

        # 大小规格化，将图片装进一个标准大小的盒子里
        timg = Image.new('RGB', (tw, th), (255, 255, 255))
        timg.paste(img, ((tw - img.width) // 2, (th - img.height) // 2))

        imgs.append(timg)
    return imgs


# 图片数量规格化
def num_4(imgs):
    t = (len(imgs) + 2) % 4
    for i in range(4 - t):
        imgs.append(Image.new("RGB", (tw, th), (255, 255, 255)))

    # 封面
    if not cover:
        imgs.insert(0, Image.new("RGB", (tw, th), (255, 255, 255)))
    else:
        img = Image.open(cover).convert('RGB')

        # 等比例缩小适应
        if img.height / img.width > t:  # 图片比标准的高
            img = img.resize((int(img.width * th / img.height), th))
        else:
            img = img.resize((tw, int(img.height * tw / img.width)))

        # 大小规格化，将图片装进一个标准大小的盒子里
        timg = Image.new('RGB', (tw, th), (255, 255, 255))
        timg.paste(img, ((tw - img.width) // 2, (th - img.height) // 2))

        imgs.insert(0, img)

    # 封底
    if not back_cover:
        imgs.append(Image.new("RGB", (tw, th), (255, 255, 255)))
    else:
        img = Image.open(back_cover).convert('RGB')

        # 等比例缩小适应
        if img.height / img.width > t:  # 图片比标准的高
            img = img.resize((int(img.width * th / img.height), th))
        else:
            img = img.resize((tw, int(img.height * tw / img.width)))

        # 大小规格化，将图片装进一个标准大小的盒子里
        timg = Image.new('RGB', (tw, th), (255, 255, 255))
        timg.paste(img, ((tw - img.width) // 2, (th - img.height) // 2))

        imgs.append(img)

    print("final num:", len(imgs))


# 在front的(w,h)处开始贴img1,img2,img_2,img_1
def paste(front, back, img1, img2, img_2, img_1, w, h):
    front.paste(img2, (w, h))
    front.paste(img_2, (w + tw, h))
    back.paste(img1, (width - w - tw, h))
    back.paste(img_1, (width - w - tw - tw, h))
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
    return imgls


if __name__ == "__main__":
    ls = get_name(d)
    imgs = get_imgs(d, ls)
    num_4(imgs)
    imgls = paste_all(imgs, tw, th)
    imgls[0].save(name, 'pdf', save_all=True, append_images=imgls[1:])
