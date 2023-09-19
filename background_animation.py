# do hlavního modulu tutorial 62 multiple animation dím from ball import *

class Back:


    def __init__(self, canvas, x, y, diameter, xVelocity, yVelocity, color):
        self.canvas = canvas
        self.image = canvas.create_image(x, y, diameter, diameter, fill=color)
        self.xVelocity = xVelocity
        self.yVelocity = yVelocity

    def move(self):
        coordinates = self.canvas.coords(self.image)
        print(coordinates)
        if(coordinates[2]>=(self.canvas.winfo_width()) or coordinates[0]<0):  # když narazí na okraj tak..
            self.xVelocity = -self.xVelocity
        if (coordinates[3] >= (self.canvas.winfo_width()) or coordinates[1] < 0):  # když narazí na okraj tak..
            self.yVelocity = -self.yVelocity


        self.canvas.move(self.image, self.xVelocity, self.yVelocity)

