import time
import sklearn.mixture
from PIL import Image, ImageFont, ImageDraw
import numpy
import torch
import requests

class PassCheck():

    def __init__(self) -> None:
        #使用cpu运行，方便没有gpu放入服务器运行
        self.net = torch.load("resources/zheye.pt", map_location=torch.device('cpu'))
        self.net.eval()


    def CAPTCHA_to_data(self,filename, width, height):
        '''
        convert CAPTCHA image to 7 chinese character image data.
        kind of slow because of GMM iteration.
        return a 7 * 40 * 40 array
        '''
        padding = 20
        padding_color = 249

        captcha = Image.open(filename)

        bg = numpy.full((height + padding * 2, width + padding * 2), padding_color, dtype='uint8')
        fr = numpy.asarray(captcha.convert('L'))
        bg[padding:padding + height, padding:padding + width] = fr

        black_pixel_indexes = numpy.transpose(numpy.nonzero(bg <= 150))
        gmm = sklearn.mixture.GaussianMixture(n_components=5, covariance_type='tied', reg_covar=1e2, tol=1e3, n_init=9)
        gmm.fit(black_pixel_indexes)

        indexes = gmm.means_.astype(int).tolist()
        new_indexes = []
        for [y, x] in indexes:
            new_indexes.append((y - padding, x - padding))

        data = numpy.empty((0, 40, 40), 'float32')
        full_image = self.data_to_image(bg)

        for [y, x] in new_indexes:
            cim = full_image.crop((x, y, x + padding * 2, y + padding * 2))
            X = numpy.asarray(cim.convert('L')).astype('float32')
            X[X <= 150] = -1
            # black
            X[X > 150] = 1
            # white
            data = numpy.append(data, X.reshape(1, 40, 40), axis=0)

        return data, new_indexes


    def mark_points(self,image, points):
        '''
        mark locations on image
        '''

        im = image.convert("RGB")
        bgdr = ImageDraw.Draw(im)
        for [y, x] in points:
            bgdr.ellipse((x - 3, y - 3, x + 3, y + 3), fill="red", outline='red')
        return im

    def data_to_image(self,d):
        '''
        convert 2darray to image object.
        '''

        return Image.fromarray(numpy.uint8(d))

    # Load net from file on CPU.

    def predict_result(self,filename, width, height):
        '''
        given a captcha image file,
        return the upside-down character indexes.
        '''

        data, indexes = self.CAPTCHA_to_data(filename, width, height)
        inputs = torch.from_numpy(data.reshape(5, 1, 40, 40))
        outputs = self.net(inputs)
        _, predicted = torch.max(outputs.data, 1)
        predicted = predicted.tolist()

        return [i for (i, p) in zip(indexes, predicted) if not p]

    def get_daoli_xy_list(self,filename, width, height):
        ps = self.predict_result(filename, width, height)
        ps = [(y, x) for (x, y) in ps]
        return ps

    def getnow(self):
        t = time.time()
        return str(int(round(t * 1000)))

    def get_captcha_pos(self,sid):
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 12; Redmi K30 Pro Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/111.0.5563.116 Mobile Safari/537.36 XWEB/5235 MMWEBSDK/20230701 MMWEBID/9650 MicroMessenger/8.0.40.2420(0x28002855) WeChat/arm64 Weixin NetType/5G Language/zh_CN ABI/arm64",
            "accept": "image/wxpic,image/tpg,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "cookie": f"wps_sid={sid}"
        }
        url=f"https://vip.wps.cn/checkcode/signin/captcha.png?platform=8&encode=0&img_witdh=336&img_height=84&v={self.getnow()}"
        
        content = requests.get(url=url, headers=headers).content

        with open(f"./captcha.jpg", "wb") as f:
            f.write(content)

        zuobiao_list = self.get_daoli_xy_list(f"./captcha.jpg", 350, 88)
        captcha_pos = '|'.join([f"{x},{y}" for x, y in zuobiao_list])
        return captcha_pos