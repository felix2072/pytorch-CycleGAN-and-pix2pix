from tkinter import *
import threading

pause = 1
seconds = 1

def threadmain():
    root = Tk()
    root.title("Pix2Pix")
    root.geometry("100x300")

    mylabelpause = Label(root, text="Pix2Pix")
    mylabelpause.pack(pady=20)

    def pausePix2Pix():
        global pause
        pause *= -1
        if pause == -1:
            mylabelpause.config(text="Stop Pix2Pix: %s" % pause)
        else:
            mylabelpause.config(text="Run Pix2Pix: %s" % pause)

    button = Button(root, text="Run Pix2Pix", command=pausePix2Pix)
    button.pack(pady=20)

    def sel():
        global seconds
        seconds = 1/var.get()
        selection = "Value = %s" % seconds
        label.config(text=selection)

    var = DoubleVar()
    scale = Scale(root, variable=var, from_=1, to=10, tickinterval=0.25)
    scale.pack(anchor=CENTER)

    button1 = Button(root, text="Get Scale Value", command=sel)
    button1.pack(anchor=CENTER)

    label = Label(root)
    label.pack()

    root.mainloop()


if __name__ == '__main__':
    x = threading.Thread(target=threadmain)
    x.start()