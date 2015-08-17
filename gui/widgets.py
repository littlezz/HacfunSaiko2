from tkinter import ttk
import tkinter
import webbrowser
from concurrent.futures import ThreadPoolExecutor
__author__ = 'zz'



_thread_pool = ThreadPoolExecutor(5)


class VarGetSetMixin:
    def get(self):
        return self.var.get()

    def set(self, value):
       self.var.set(value=value)




class StringVarMixin(VarGetSetMixin):
    def __init__(self, *args, **kwargs):
        value = kwargs.pop('value', None)
        self.var = tkinter.StringVar(value=value)
        kwargs.update(textvariable=self.var)
        super().__init__(*args, **kwargs)


class HelpTextMixin:
    def __init__(self, *args, **kwargs):
        self.help_text = kwargs.pop('help_text','')
        super().__init__(*args, **kwargs)


class HyperMixin:
    def __init__(self, *args, **kwargs):
        self._link = kwargs.pop('link', '')
        super().__init__(*args, **kwargs)
        self.bind('<1>', self._click)

    def _click(self, event):
        webbrowser.open(self._get_url())

    def _get_url(self):
        return self._link





class CheckButton(HelpTextMixin, VarGetSetMixin, ttk.Checkbutton):
    def __init__(self, master, value=1, **kwargs):
        self.var = tkinter.IntVar(value=value)
        kwargs.update(variable=self.var)
        super().__init__(master, **kwargs)


class Button(HelpTextMixin, ttk.Button):
    pass


class Entry(HelpTextMixin, StringVarMixin, ttk.Entry):
    pass


class NumberEntry(HelpTextMixin, VarGetSetMixin, ttk.Entry):
    def __init__(self, master, value=None, **kwargs):
        super().__init__(master, **kwargs)
        self.var = tkinter.IntVar(value=value)
        vcmd = (self.register(self.validating), '%S')

        cf = dict()
        cf.update(textvariable=self.var)
        cf.update(validatecommand=vcmd)
        cf.update(validate='key')
        self.configure(**cf)


    def validating(self, text):
        allow = '0123456789'
        if all(c in allow for c in text):
            return True
        return False


class InfoLabel(HelpTextMixin, StringVarMixin, ttk.Label):
    pass


class HyperLabel(HyperMixin, ttk.Label):
    pass


class ImageFrame(ttk.Frame):
    height = 128
    width = 128
    def __init__(self, *args, **kwargs):
        self.image_url = kwargs.pop('image_url', None)

        kwargs.update({
            'height':self.height,
            'width': self.width
        })
        super().__init__(*args, **kwargs)
        self.grid_propagate(0)

        if self.image_url:
            self.label = ttk.Label(self, text='downloading...')
            _thread_pool.submit(self.download_image)

        else:
            self.label = ttk.Label(self, text='No Image')

        self.label.grid(column=0, row=0)

    def download_image(self):
        pass


class ExtraDataComboBox(HelpTextMixin, ttk.Combobox):
    def __init__(self, *args, **kwargs):
        values_pair = kwargs.pop('values_pair', [])
        values = []
        self._maps = dict()
        for pair in values_pair:
            value, extra = pair
            self._maps.update({value:extra})
            values.append(value)

        kwargs.update(values=values)
        super().__init__(*args, **kwargs)

    def get(self):
        value = super().get()
        return self._maps[value]



class BaseFrame(ttk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._init()

    def _init(self):
        raise NotImplementedError
