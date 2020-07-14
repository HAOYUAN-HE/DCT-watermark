# -*- coding: utf-8 -*-
"""
信息安全
-108
"""

import numpy as np
from matplotlib.figure import Figure

import PIL
from PIL import Image
import cv2
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Tkinter import *
import tkFileDialog as dialog
import tkMessageBox
import ttk

np.seterr(divide='ignore', invalid='ignore')


class WaterMark(object):
    def __init__(self, parent):
        self.parent = parent
        self.size = 256
        self.N = 32
        self.K = 8
        self.Key1 = np.array([1, 2, 3, 4, 5, 6, 7, 8])
        self.Key2 = np.array([8, 7, 6, 5, 4, 3, 2, 1])
        self.state = 0
        fig = Figure() # 定义fig为Figure()方法
        self.axe_1 = fig.add_subplot(221)  # 在2列2行的第一个位置绘制坐标轴axe_1
        self.axe_1.set_title(u'Orginal')   # axe_1标题为Orginal,u用Unicode编码防止乱码(若使用中文)
        self.axe_2 = fig.add_subplot(222)
        self.axe_2.set_title(u'Mark')
        self.axe_3 = fig.add_subplot(223)
        self.axe_3.set_title(u'Marked')
        self.axe_4 = fig.add_subplot(224)
        self.axe_4.set_title(u'DrawMark')

        self.canvas = FigureCanvasTkAgg(fig, self.parent)  # 绘制画布
        self.canvas._tkcanvas.config(bg='gainsboro', highlightthickness=0)
        self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=YES, padx=0)
        self.canvas.show()

        frame = Frame(self.parent) # 定义一个框架frame
        frame.pack(fill=X)  # 当窗体大小变化时，widget在X方向跟随窗体变化

        label = Label(frame, text='Save as：')   # 定义标签label,值为Save as：
        label.pack(side=LEFT) # 定义框架位置

        self.filename = StringVar()  # 用 StringVar()接受获取用户输入
        entry = Entry(frame, textvariable=self.filename) # 定义一个输出框
        entry.pack(side=LEFT)  # 定义位置
        button2 = Button(frame, text='Add watermark', command=self.insert_mark)  # 定义按钮，点击执行insert_mark方法
        button2.pack(side=LEFT)  # 定义位置

        frame2 = Frame(frame)  # 定义框架2
        frame2.pack(side=RIGHT)  # 定义框架2位置
        button1 = Button(frame2, text='Seperate watermark', command=self.seperate_mark)  # 定义按钮，点击执行seperate_mark方法
        button1.pack(side=LEFT, padx=20)  # 定义位置
        button3 = Button(frame2, text='Attack', command=self.noise_test)  # 定义按钮，点击执行noise_test方法
        button3.pack(side=LEFT)  # 定义位置
        variable = [u'WhiteNoise', u'Gaussian'] # 定义选项
        self.comboBox = ttk.Combobox(frame2, value=variable, width=10)
        self.comboBox.set(u'WhiteNoise')  # comboBox默认值为WhiteNoise
        self.comboBox.pack(side=LEFT)  # 定义comboBox位置

        menubar = Menu(self.parent)  # 定义菜单栏
        filemenu = Menu(menubar)  # 定义filemenu
        filemenu.add_command(label='open', command=self.open_image)  # 定义点击菜单栏单位所执行方法
        filemenu.add_command(label='open mark', command=self.open_mark)  # 定义点击菜单栏单位所执行方法
        filemenu.add_command(label='open picture', command=self.open_picture)  # 定义点击菜单栏单位所执行方法
        menubar.add_cascade(label='File', menu=filemenu)  # 构造一个下拉的menu
        self.parent.config(menu=menubar)  # 显示菜单

    def open_image(self):
        self.image = dialog.askopenfilename(parent=self.parent, filetypes=[('*', '*.*')], title='Open ')
        # 使用tkinter.filedialong模块中的askopenfilename函数实现 打开文件对话框
        print self.image # 打印图片名
        if self.image != '':  # 文件不为空
            self.image = cv2.imread(self.image.encode('gbk'))  # 导入图片编码为gbk
            self.image = cv2.resize(self.image, (self.size, self.size))  # 图片缩放
            image = self.change_channals(self.image) # 图片执行change_channals方法
            self.axe_1.imshow(image)  # 显示在axe_1坐标轴
            self.canvas.show()  # 界面显示

    def open_mark(self):
        self.mark = dialog.askopenfilename(parent=self.parent, filetypes=[('*', '*.*')], title='Open ')
        # 使用tkinter.filedialong模块中的askopenfilename函数实现 打开文件对话框
        print type(self.mark)  # 打印水印图片类型
        if self.mark != '': # 文件不为空
            self.mark = cv2.imread(self.mark.encode('gbk'))  # 导入图片编码为gbk
            self.mark = cv2.resize(self.mark, (self.N, self.N)) # 缩放图片到指定大小
            self.axe_2.imshow(self.mark)  # 显示在axe_2坐标轴
            self.canvas.show() # 界面显示

    def open_picture(self):
        self.picture = dialog.askopenfilename(parent=self.parent, filetypes=[('*', '*.*')], title='Open ')
        # 使用tkinter.filedialong模块中的askopenfilename函数实现 打开文件对话框
        if self.picture != '': # 文件不为空
            self.picture = cv2.imread(self.picture.encode('gbk'))  # 导入图片编码为gbk
            self.picture = cv2.resize(self.picture, (self.size, self.size))  # 缩放图片到指定大小
            picture = self.change_channals(self.picture)  # 图片执行change_channals方法
            self.axe_3.imshow(picture)  # 显示在axe_3坐标轴
            self.canvas.show()  # 界面显示

    def change_channals(self, image):
        image = image
        image = PIL.Image.fromarray(np.uint8(image))  # PLI array转化成image
        r, g, b = image.split()  # 图像分割
        image = PIL.Image.merge('RGB', (b, g, r))  # 将b,r两个通道翻转 opencv储存顺序bgr
        return image



    def insert_mark(self):
        if self.filename.get() == '':
            firstwarning = tkMessageBox.showwarning(message='Error:Input can not be empty!!!')

        else:
            # print self.filename.get()
            self.image = cv2.resize(self.image, (self.size, self.size))  #缩放
            D = self.image.copy()

            alfa = 10   # 尺度因子,控制水印添加的强度,决定了频域系数被修改的幅度

            # 将256*256分别除以8得到图像总的字节数，range（图像的范围）
            #  一
            #  把图片分成8*8的块，进行DCT变换，得到频域系数矩阵
            for p in range(self.size / self.K):
                for q in range(self.size / self.K):
                    x = p * self.K
                    y = q * self.K
                    # print  type(D[0,0,0])
                    img_B = np.float32(D[x:x + self.K, y:y + self.K,0])

                    print 1, img_B[3, 3]
                    I_dct1 = cv2.dct(img_B)  #定义一个I_dct，进行dct

                    if self.mark[p, q, 0] < 100:
                        Key = self.Key1
                    else:
                        Key = self.Key2

                    I_dct_A = I_dct1.copy()

                    #  二：
                    #   F'=F+a W公式 F修改前频域系数  F'修改后频域系数  W表示嵌入水印信息 a表示水印嵌入强度 决定了频率系数被修改的幅度
                    I_dct_A[0, 7] = I_dct1[0, 7] + alfa * Key[0]
                    I_dct_A[1, 6] = I_dct1[1, 6] + alfa * Key[1]
                    I_dct_A[2, 5] = I_dct1[2, 5] + alfa * Key[2]
                    I_dct_A[3, 4] = I_dct1[3, 4] + alfa * Key[3]
                    I_dct_A[4, 3] = I_dct1[4, 3] + alfa * Key[4]
                    I_dct_A[5, 2] = I_dct1[5, 2] + alfa * Key[5]
                    I_dct_A[6, 1] = I_dct1[6, 1] + alfa * Key[6]
                    I_dct_A[7, 0] = I_dct1[7, 0] + alfa * Key[7]

                    # 三
                    # 对新的频域系数矩阵进行IDCT得到含水印的8*8图像块，取代原来的图像块
                    I_dct_A = np.array(I_dct_A)
                    I_dct_a = cv2.idct(I_dct_A)   #将dct变换后的数组进行逆dct变换

                    # I_dct_a = I_dct_a

                    # max_point = np.max(I_dct_a)
                    # min_point = np.min(I_dct_a)

                    # print max_point,I_dct_a[7,7]
                    # I_dct_a = np.uint8(I_dct_a/ max_point*255) -1
                    # I_dct_a = np.uint8(I_dct_a)
                    # print max_point,min_point,I_dct_a[3,3]

                    # E[x:x+self.K,y:y+self.K,0] = I_dct_a

                    #                    I_dct_a=np.float32(I_dct_a-min_point+0.0001)/np.float32(max_point-min_point+0.0001)*255.0

                    D[x:x + self.K, y:y + self.K, 0] = I_dct_a

            self.picture = D
            E = D.copy()
            filename = 'watermarked/' + self.filename.get()  # 定义存放文件位置
            cv2.imwrite(filename.encode('gbk'), E)  # 读取编码为gbk的图像文件
            E = self.change_channals(E)
            E = np.uint8(E)

            self.axe_3.imshow(E)
            self.canvas.show()

    def seperate_mark(self):

        self.Pmark = np.zeros((32, 32, 3)) # 32*32的图像  - 3 通道数

        pp = np.zeros(8)  # 8位数组
        for p in range(self.size / self.K):
            for q in range(self.size / self.K):
                x = p * self.K
                y = q * self.K
                img_B = np.float32(self.picture[x:x + self.K, y:y + self.K, 0])   # float32是单精度浮点数

                #                max_point = np.max(img_B)
                #                min_point = np.min(img_B)
                #                img_B=np.float32(img_B-min_point+0.0001)/np.float32(max_point-min_point+0.0001)*255.0

                I_dct1 = cv2.dct(img_B)  # 将img_B进行dct变换存到I_dct1

                pp[0] = I_dct1[0, 7]   # 提取之前改变过数值的点的数值出来 存到pp数组
                pp[1] = I_dct1[1, 6]
                pp[2] = I_dct1[2, 5]
                pp[3] = I_dct1[3, 4]
                pp[4] = I_dct1[4, 3]
                pp[5] = I_dct1[5, 2]
                pp[6] = I_dct1[6, 1]
                pp[7] = I_dct1[7, 0]

                if np.corrcoef(pp, self.Key1)[0][1] <= np.corrcoef(pp, self.Key2)[0][1]: # 通过相对系数corrcoef比较两个序列的相识度
                     self.Pmark[p, q, 0] = 1
                     self.Pmark[p, q, 1] = 1
                     self.Pmark[p, q, 2] = 1  # 3通道重叠

        if self.state == 0:  # 如1为含有噪声 无法提取 0无 可提取
            self.axe_4.imshow(self.Pmark)
            self.canvas.show()

    def whitenoise(self, image):
        image = image
        noise = 10 * np.random.randn(self.size, self.size, 3)  #增加白噪声
        self.WImage = image + noise  #原图加噪声

    def gaussian(self, image):
        self.WImage = cv2.GaussianBlur(image, (5, 5), 1.5)  # 调用cv2函数进行高斯低通滤波 根据窗口大小（5,5）计算高斯函数标准差

    def noise_test(self):
        self.state = 1

        filter_name = self.comboBox.get()  # 定义一个comboBox下拉菜单为fileter_name
        # print filter_name
        #        self.whitenoise(self.picture)
        if filter_name == u'WhiteNoise':
            self.whitenoise(self.picture)  # 执行相应方法
        elif filter_name == u'Gaussian':
            self.gaussian(self.picture)  # 执行相应方法

        figure = Toplevel(self.parent)  # Toplevel类似Frame 内含窗体属性(title)

        fig = Figure()  # 绘图

        self.seperate_mark()  # 调用seperate_mark()方法

        canvas = FigureCanvasTkAgg(fig, figure)
        canvas._tkcanvas.config(bg='gainsboro', highlightthickness=0)  # 背景颜色,指定高亮边框亮度，0位不带高亮边框
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=YES, padx=0)  # 窗体位置相关
        axe1 = fig.add_subplot(211)  # 定义一个坐标轴axe1位于2列1行的第1个位置
        axe1.set_title(filter_name)  # 坐标轴1命名
        WImage = self.change_channals(self.WImage)
        axe1.imshow(WImage)  # 显示处理后图片
        axe2 = fig.add_subplot(212)  # 定义一个坐标轴axe1位于2列1行的第2个位置
        axe2.imshow(self.Pmark)  # 显示提取的水印
        self.state = 0
        canvas.show()


if __name__ == '__main__':
    root = Tk()  # 成一个底层窗口，开始进程
    root.title(u'信息安全技术-基于DCT变换域鲁棒性数字水印应用设计')

    watermark = WaterMark(root)

    root.mainloop()  # 令根空间进入主循环,开始监听事件和执行人机交互命令，开始进程
























