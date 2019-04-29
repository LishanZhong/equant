import matplotlib.pyplot as plt

"""
回测报告的事件处理类
"""

X_OFFSET_PIXELS = 15
Y_OFFSET_PIXELS = 15


# TODO: 将EventHandler类分成父类和子类实现
class EventHandler(object):
    def __init__(self, figure, canvas, axes):
        self.fig = figure
        self.canvas = canvas
        self.axes = axes
        self.press = None

        self.x = 0
        self.flag = False
        self.ref_line = None
        self.text = None
        self.set_ref_line()
        self.set_annotate()
        self.temp = None

    def set_border(self):
        # 获取到x轴的初始范围并赋值给self.minX和self.maxX
        self.minX, self.maxX = self.axes.get_xlim()

    def set_x_labels(self, label):
        # 将x轴的时间label传进来
        self.xlabels = label

    def set_ref_line(self):
        # 新建一条垂直参考线
        self.ref_line = self.axes.axvline(x=round(self.x))
        self.ref_line.set_visible(False)

    def set_annotate(self):
        self.text = self.axes.annotate('时间：' + '\n' + '动态权益：',
                                       xy=(0, 0),
                                       xycoords='data',
                                       xytext=(X_OFFSET_PIXELS, Y_OFFSET_PIXELS),
                                       textcoords='offset pixels', horizontalalignment='left',
                                       verticalalignment='bottom')

    def _get_y_extreme(self, orig_x, orig_y, local_minX, local_maxX):
        # 获取到当前坐标轴范围内y的最大值和最小值
        # if条件不满足程序会报错
        if local_minX in orig_x and local_maxX in orig_x:
            temp = orig_y[int(local_minX): int(local_maxX+1)]
            return min(temp), max(temp)

    def _set_vertical_axis_lim(self, miny, maxy):
        # a = miny * 0.9 if miny > 0 else miny * 1.1
        b = maxy * 0.1 if maxy > 0 else maxy * (-0.1)
        self.axes.set_ylim(miny - b, maxy + b)

    def connect(self):
        'connect to all the events we need'
        self.press_id = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.release_id = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.motion_id = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.scroll_id = self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.aleave_id = self.canvas.mpl_connect('axes_leave_event', self.on_axe_leave)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes is None: return

        self.press = event.xdata
        # a = self.axes.get_xticklabels()
        # print(a)
        if self.flag:
            self.flag = False
            if self.ref_line:
                self.ref_line.set_visible(False)
            if self.text:
                self.text.set_visible(False)
            return
        else:
            self.flag = True

        self.x = event.xdata

        del self.ref_line
        del self.text
        self.ref_line = self.axes.axvline(x=round(self.x), color='g')
        self.ref_line.set_visible(True)

        orig_x = event.inaxes.lines[0].get_xdata(orig=True)  # 取得原始x数据
        orig_y = event.inaxes.lines[0].get_ydata(orig=True)  # 取得原始y数据
        distance0 = list(abs(orig_x - event.xdata))
        distance = min(distance0)
        inde = distance0.index(distance)

        bbox_props = dict(boxstyle="square", fc="w", ec="0.5", alpha=0.5, lw=1, pad=0.5)
        self.text = self.axes.annotate('时间：' + '{:.2f}'.format(orig_x[inde]) + '\n'
                                       + '动态权益：' + '{:.2f}'.format(orig_y[inde]),
                                       xy=(orig_x[inde], orig_y[inde]),
                                       xycoords='data',
                                       xytext=(X_OFFSET_PIXELS, Y_OFFSET_PIXELS),
                                       textcoords='offset pixels',
                                       horizontalalignment='left', verticalalignment='bottom',
                                       bbox=bbox_props)
        self.text.set_visible(True)

        self.fig.canvas.draw()
        self.canvas.draw()

    def on_motion(self, event):
        'on motion we will move the line in the axe'
        if event.inaxes is None: return

        self.x = event.xdata
        self.ref_line.set_visible(False)

        orig_x = event.inaxes.lines[0].get_xdata(orig=True)  # 取得原始x数据
        orig_y = event.inaxes.lines[0].get_ydata(orig=True)  # 取得原始y数据
        ex_y_min, ex_y_max = self._get_y_extreme(orig_x, orig_y, event.inaxes.viewLim.x0, event.inaxes.viewLim.x1)

        if self.flag:
            del self.ref_line
            self.ref_line = self.axes.axvline(x=round(self.x), color='g')
            self.ref_line.set_visible(True)

            distance0 = list(abs(orig_x - event.xdata))
            distance = min(distance0)
            if distance < 100:
                inde = distance0.index(distance)
                if self.text:
                    self.text.set_visible(False)

                bbox_props = dict(boxstyle="square", fc="w", ec="0.5", alpha=0.5, lw=1, pad=0.5)
                self.text = self.axes.annotate('时间：' + '{:.2f}'.format(orig_x[inde]) + '\n'
                                               + '动态权益：' + '{:.2f}'.format(orig_y[inde]),
                                               xy=(orig_x[inde], orig_y[inde]),
                                               xycoords='data',
                                               xytext=(X_OFFSET_PIXELS, Y_OFFSET_PIXELS),
                                               textcoords='offset pixels', horizontalalignment='left',
                                               verticalalignment='bottom',
                                               bbox=bbox_props)
                self.text.set_visible(True)

                if self.temp:
                    del self.temp
                    self.fig.canvas.draw()
                    self.canvas.draw()
                # TODO: 移动鼠标时点的效果也跟着改变：
                # TODO：方案1：直接重新绘制曲线
                # TODO：方案2：将原来的点描掉，再绘制新点
                self.temp = self.axes.scatter(orig_x[inde], orig_y[inde], c='white', edgecolors='blue')
                #print(self.temp)
            # -----------------------------------------------------------------------------

        self.fig.canvas.draw()
        self.canvas.draw()

        if self.press is None: return

        dx = int(event.xdata - self.press)
        x_min, x_max = self.axes.get_xlim()

        if x_min <= self.minX and x_max >= self.maxX:
            return
        if x_min - dx < self.minX:
            self.axes.set_xlim(self.minX, x_max)
            self._set_vertical_axis_lim(ex_y_min, ex_y_max)
        elif x_max - dx > self.maxX:
            self.axes.set_xlim(x_min, self.maxX)
            self._set_vertical_axis_lim(ex_y_min, ex_y_max)
        else:
            self.axes.set_xlim(x_min - dx, x_max - dx)
            self._set_vertical_axis_lim(ex_y_min, ex_y_max)

        self.fig.canvas.draw()
        self.canvas.draw()

    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        self.fig.canvas.draw()
        self.canvas.draw()

    def on_scroll(self, event):
        if event.inaxes is None: return

        if self.text:
            self.text.set_visible(False)
        if self.ref_line:
            self.text.set_visible(False)
        self.fig.canvas.draw()
        self.canvas.draw()

        orig_x = event.inaxes.lines[0].get_xdata(orig=True)  # 取得原始x数据
        orig_y = event.inaxes.lines[0].get_ydata(orig=True)  # 取得原始y数据
        ex_y_min, ex_y_max = self._get_y_extreme(orig_x, orig_y, event.inaxes.viewLim.x0, event.inaxes.viewLim.x1)

        x_min, x_max = self.axes.get_xlim()
        zoom = (x_max - x_min) // 5
        if event.button == 'up':
            if x_max - x_min <= 6:
                return
            self.axes.set_xlim(x_min + zoom, x_max - zoom)
            self._set_vertical_axis_lim(ex_y_min, ex_y_max)
        elif event.button == 'down':
            if x_min <= self.minX:
                if x_max >= self.maxX:
                    return
                elif x_max + zoom <= self.maxX:
                    self.axes.set_xlim(self.minX, x_max + zoom)
                else:
                    self.axes.set_xlim(self.minX, self.maxX)
                self._set_vertical_axis_lim(ex_y_min, ex_y_max)
            elif x_max >= self.maxX:
                if x_min <= self.minX:
                    return
                elif x_min - zoom >= self.minX:
                    self.axes.set_xlim(x_min - zoom, self.maxX)
                else:
                    self.axes.set_xlim(self.minX, self.maxX)
                self._set_vertical_axis_lim(ex_y_min, ex_y_max)
            else:
                if x_min - zoom >= self.minX and x_max + zoom <= self.maxX:
                    self.axes.set_xlim(x_min - zoom, x_max + zoom)
                elif x_min - zoom >= self.minX and x_max + zoom > + self.maxX:
                    self.axes.set_xlim(x_min - zoom, self.maxX)
                elif x_min - zoom < self.minX and x_max + zoom <= self.maxX:
                    self.axes.set_xlim(self.minX, x_max + zoom)
                else:
                    self.axes.set_xlim(self.minX, self.maxX)
                self._set_vertical_axis_lim(ex_y_min, ex_y_max)

        self.fig.canvas.draw()
        self.canvas.draw()

    def on_axe_leave(self, event):
        # TODO: 如果离开坐标轴的速度过快，matplotlib反应不过来，没有检测到这个事件
        # TODO：下面这些就不会执行
        self.flag = False
        if self.ref_line.get_visible():
            self.ref_line.set_visible(False)
        if self.text.get_visible():
            self.text.set_visible(False)
        self.fig.canvas.draw()
        self.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.fig.canvas.mpl_disconnect(self.press_id)
        self.fig.canvas.mpl_disconnect(self.release_id)
        self.fig.canvas.mpl_disconnect(self.motion_id)
        self.fig.canvas.mpl_disconnect(self.scroll_id)
        self.fig.canvas.mpl_disconnect(self.aleave_id)
