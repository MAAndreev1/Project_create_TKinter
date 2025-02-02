import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, StringVar, simpledialog
from PIL import Image, ImageDraw


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Рисовалка с сохранением в PNG")

        self.image = Image.new("RGB", (600, 400), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.canvas = tk.Canvas(root, width=600, height=400, bg='white')
        self.canvas.pack()

        self.brush_size_scale = None

        self.last_x, self.last_y = None, None

        self.pen_size = StringVar(value="1")
        self.pen_size.trace("w", self.size_reload)

        self.pen_color = 'black'
        self.pen_color_last = 'black'

        self.eraser_button_name = StringVar(value='Ластик')

        self.setup_ui()

        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

        self.canvas.bind('<Button-3>', self.pick_color)

        self.root.bind('<Control-s>', self.save_image)
        self.root.bind('<Control-c>', self.choose_color)

    def setup_ui(self):
        """
        Этот метод отвечает за создание и расположение виджетов управления.
        """
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)

        clear_button = tk.Button(control_frame, text="Очистить", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT)

        color_button = tk.Button(control_frame, text="Выбрать цвет", command=self.choose_color)
        color_button.pack(side=tk.LEFT)

        save_button = tk.Button(control_frame, text="Сохранить", command=self.save_image)
        save_button.pack(side=tk.LEFT)

        self.brush_size_scale = tk.Scale(control_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.brush_size_scale.pack(side=tk.LEFT)

        size_button = tk.OptionMenu(control_frame, self.pen_size,'1', '2', '5', '10')
        size_button.pack(side=tk.LEFT)

        canvas_size = tk.Button(control_frame, text="Холст", command=self.choosing_canvas_size)
        canvas_size.pack(side=tk.LEFT)

        self.color_label = tk.Label(control_frame, background=self.pen_color, padx=20, borderwidth=5,
                                    highlightthickness=4, highlightbackground="#f0f0f0")
        self.color_label.pack(side=tk.RIGHT)

        eraser_button = tk.Button(control_frame, textvariable=self.eraser_button_name, command=self.choose_eraser)
        eraser_button.pack(side=tk.RIGHT)

    def choosing_canvas_size(self):
        """
        Обновляет размеры холста
        """
        choose_height = tk.simpledialog.askinteger("Input","Input Height",parent=self.root)
        choose_width = tk.simpledialog.askinteger("Input","Input Width",parent=self.root)

        self.canvas.config(width=int(choose_width), height=int(choose_height))
        self.canvas.delete("all")
        self.image = Image.new("RGB", (choose_width, choose_height), "white")
        self.draw = ImageDraw.Draw(self.image)

    def reload_label_color(self, *args):
        self.color_label.config(background=self.pen_color)

    def size_reload(self, *args):
        """
        Устанавливает значение слайдеру для изменения значения кисти.
        """
        print(f'Получил размер - {self.pen_size.get()}')
        self.brush_size_scale.set(self.pen_size.get())

    def choose_eraser(self, *args):
        """
        Функция изменяет цвет кисти имитируя ластик. Так же меняет титул кнопки в зависимости от активации ластика.
        """
        if self.eraser_button_name.get() == 'Ластик':
            self.pen_color_last = self.pen_color
            self.eraser_button_name.set('Кисть')
            self.pen_color = 'white'
            self.root.config(cursor="circle")
        elif self.eraser_button_name.get() == 'Кисть':
            self.pen_color = self.pen_color_last
            self.eraser_button_name.set('Ластик')
            self.root.config(cursor="arrow")

    def pick_color(self, event):
        """
        Функция получает пиксель и устанавливает цвет пикселя как используемый.
        """
        def get_rgb(rgb):
            return "#%02x%02x%02x" % rgb
        print(self.image.getpixel((event.x, event.y)))
        self.pen_color = get_rgb(self.image.getpixel((event.x, event.y)))
        self.reload_label_color()

    def paint(self, event):
        """
        Функция вызывается при движении мыши с нажатой левой кнопкой по холсту.
        Она рисует линии на холсте Tkinter и параллельно на объекте Image из Pillow.
        """
        if self.last_x and self.last_y:
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    width=self.brush_size_scale.get(), fill=self.pen_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)
            self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.pen_color,
                           width=int(self.brush_size_scale.get()))

        self.last_x = event.x
        self.last_y = event.y

    def reset(self, event):
        """
        Сбрасывает последние координаты кисти. Это необходимо для корректного начала новой линии после того,
        как пользователь отпустил кнопку мыши и снова начал рисовать.
        """
        self.last_x, self.last_y = None, None

    def clear_canvas(self, *args):
        """
        Очищает холст, удаляя все нарисованное, и пересоздает объекты Image и ImageDraw для нового изображения.
        """
        self.canvas.delete("all")
        self.image = Image.new("RGB", (600, 400), "white")
        self.draw = ImageDraw.Draw(self.image)

    def choose_color(self, *args):
        """
        Открывает стандартное диалоговое окно выбора цвета и устанавливает выбранный цвет как текущий для кисти.
        """
        self.pen_color = colorchooser.askcolor(color=self.pen_color)[1]
        if self.pen_color != 'white':
            self.eraser_button_name.set('Ластик')
        self.reload_label_color()

    def save_image(self, *args):
        """
        Позволяет пользователю сохранить изображение, используя стандартное диалоговое окно для сохранения файла.
        Поддерживает только формат PNG. В случае успешного сохранения выводится сообщение об успешном сохранении.
        """
        file_path = filedialog.asksaveasfilename(filetypes=[('PNG files', '*.png')])
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            self.image.save(file_path)
            messagebox.showinfo("Информация", "Изображение успешно сохранено!")


def main():
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
