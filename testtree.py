#Recursive Tree Challenge - www.101computing.net/recursive-tree-challenge
from turtle import *
from random import randint

#Recursive function to draw a tree, branch by branch
def drawTree(level,size,angle,ratio):
    if level >= 0:
        forward(size)
        left(angle)
        drawTree(level-1,size/ratio,angle,ratio)
        right(2*angle)
        #Draw right branch of the tree
        drawTree(level-1,size/ratio,angle,ratio)
        left(angle)
        forward(-size)
    else:
        #Stop the recursion
        return

#Main Program Starts Here
speed(0)
penup()
goto(0,-180)
left(90)
pendown()

#Draw a tree using a recursive function
size = randint(80,120)
angle = randint(20,40)
ratio = randint(14,18)/10
level = randint(4,6)

drawTree(level,size,angle,ratio)