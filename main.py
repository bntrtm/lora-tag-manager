from graphics import TrainLoraWin

def main():
    win = TrainLoraWin(900, 600)
    win.redraw()

    win.wait_for_close()

main()