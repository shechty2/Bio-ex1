import numpy as np
import matplotlib.pyplot as plt
import csv

# Define for static sizes
AUTO_SIZE = 200  # NXN board
P = 0.7  # RO
HEALTHY = 1
SICK = 2
FILE = "Run_1.csv"


# -------------------------------------------------------------------------
class Board(object):
    """ Initialize the board with zeros and random ones and two accordind to user input N"""

    def __init__(self, N,k, isolation_i):
        self.state = np.zeros(AUTO_SIZE * AUTO_SIZE)
        self.state[:N] = HEALTHY
        self.state[:1] = SICK
        np.random.shuffle(self.state)
        self.state = self.state.reshape((AUTO_SIZE, AUTO_SIZE))
        if isolation_i == 0 or isolation_i == 1:
            self.engine = Engine(self, k)
        else:
            self.engine = Engine(self, 0)
        self.iteration = 0
        self.loop = True
        self.N = N
        self.start_iso = isolation_i
        self.k = k

    def animate(self):
        def handle_close(evt):
            csv_file.close()
            self.loop = False

        sick = []
        index = []
        i = self.iteration
        im = None
        csv_file = open(FILE, 'w')
        writer = csv.writer(csv_file, dialect='excel')
        plt.title("COVID-19 Spreading\n N= " + str(np.sum(self.state != 0)) + " K= " + str(self.engine.k))
        while self.loop:
            if i == 0:
                im = plt.imshow(self.state, vmin=0, vmax=2, cmap=plt.cm.bwr)
                plt.gca().invert_yaxis()
            else:
                if i == self.start_iso:
                    self.engine.k = self.k
                im.set_data(self.state)
                im.figure.canvas.mpl_connect('close_event', handle_close)
            i += 1
            self.engine.move_creatures()
            status = (i, self.engine.nHealthy, self.engine.nSick)
            print('Life Cycle: {} Healthy: {} Sick: {}'.format(i, self.engine.nHealthy, self.engine.nSick))
            writer.writerow(status)
            sick.append(int(self.engine.nSick))
            index.append(i)
            plt.pause(0.01)
            yield self

        self.plot(sick, index)

    def plot(self, sick, index):
        ''' Ploting the sick count vs life cycle '''
        plt.plot(index, sick, label='Sick throw time')
        plt.ylim(0, self.N)
        plt.xlabel('Life Cycle')
        plt.ylabel('Sick count')
        plt.title('Sick count per life cycle')
        plt.legend()
        plt.show()
        exit(0)


# -------------------------------------------------------------------------

class Engine(object):
    def __init__(self, board, k):
        self.state = board.state
        self.k = k
        self.nSick = 0
        self.nHealthy = 0

    "Check the all 8 cells around given value."

    def valid_cell(self, cell):
        if cell[0] < 0:
            cell[0] += AUTO_SIZE
        if cell[1] < 0:
            cell[1] += AUTO_SIZE
        if cell[0] >= AUTO_SIZE:
            cell[0] -= AUTO_SIZE
        if cell[1] >= AUTO_SIZE:
            cell[1] -= AUTO_SIZE
        return cell

    def sick_neighbors(self, move_list):
        ''' Count all sick neighbors of a cell to give correct probability'''
        state = self.state
        n = 0
        for i, move in enumerate(move_list.values()):
            "An isolation method depended on K, optional"
            if i >= self.k:
                move = self.valid_cell(move)
                if state[move[0], move[1]] == 2:
                    n += 1
        return n

    def check_next_cell(self, cell, auto, i, j, next):
        """"" check if next cell is free and change it according to
        methods:if there are sick neighbours
        in probability P the cell it self will be sick """
        move_list = {1: [i - 1, j - 1], 2: [i - 1, j], 3: [i - 1, j + 1], 4: [i, j + 1], 5: [i + 1, j + 1],
                     6: [i + 1, j], 7: [i + 1, j - 1], 8: [i, j - 1]}

        def prob_sick():
            ''' check the probability of a creature to be sick
                according to number of sick neighbours'''
            n = self.sick_neighbors(move_list)
            p = np.random.uniform(0, 1)
            if n * P > p:
                return SICK
            else:
                return cell

        next_value = self.valid_cell(move_list[next])
        '''******************************************************************************
            Check the next cell, if free- move the creature in
                                 else- check probability to be sick and change if needed
            ******************************************************************************'''
        if auto[next_value[0], next_value[1]] == 0:
            auto[next_value[0], next_value[1]] = prob_sick()
            auto[i, j] = 0
        else:
            auto[i, j] = prob_sick()

        return auto

    def move_creatures(self):
        """
            Run over all the cell (in one generation)
            and move it randomly for one of the
            neighbours, include stay in place
            """
        auto = self.state
        for y, line in enumerate(auto):
            for x, cell in enumerate(line):
                'no creature cell'
                if cell == 0:
                    continue
                next_cell = np.random.randint(0, 8)
                'Stay in place'
                if next_cell == 0:
                    continue
                ' check next cell'
                auto = self.check_next_cell(cell, auto, y, x, next_cell)

        self.nHealthy = np.sum(self.state == 1)
        self.nSick = np.sum(self.state == 2)
        return auto


# -------------------------------------------------------------------------


def main():
    ''' Opens a tkinter window for user inputs, collect them and run the board function'''
    import tkinter as tk

    def run():
        if int(e1.get()) > AUTO_SIZE * AUTO_SIZE or int(e1.get()) < 0:
            raise ValueError("illegal N Value, only 0-" + str(AUTO_SIZE * AUTO_SIZE) + " try again")
        if int(e2.get()) > 8 or int(e2.get()) < 0:
            raise ValueError("illegal K Value, only 0-8 try again")
        board = Board(int(e1.get()), int(e2.get()),int(e3.get()))
        master.destroy()
        for _ in board.animate():
            pass

    master = tk.Tk()
    master.title('COVID-19 Spreading')
    master.geometry("200x200")

    tk.Label(master,
             text="N").grid(row=0)
    tk.Label(master,
             text="K").grid(row=1)
    tk.Label(master,
             text="Life cycle for isolation").grid(row=2)

    e1 = tk.Entry(master)
    e2 = tk.Entry(master)
    e3 = tk.Entry(master)

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    tk.Button(master,
              text='Run', command=run).grid(row=3,
                                            column=1,
                                            sticky=tk.W,
                                            pady=2)

    tk.mainloop()


# -------------------------------------------------------------------------

if __name__ == '__main__':
    main()
