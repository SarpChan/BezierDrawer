from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
import numpy as np
import glfw

"""Autor: Sarp Can"""

class RenderWindow:
    def __init__(self):
        """Init Fenster"""
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # Fenster Variablen

        self.width, self.height = 640, 480
        self.aspect = self.width / float(self.height)
        self.window = glfw.create_window(self.width, self.height, "Das ist aber eien schöne BSpline", None, None)
        self.exitNow = False
        self.resizing = False
        self.showPolygon = True
        self.m = 20
        self.k = 4

        self.knotenvektor = []
        self.controlpoints = []
        self.bSplinePoints = []

        self.pointVBO = vbo.VBO(np.array(self.controlpoints, 'f'))
        self.bSplineVBO = vbo.VBO(np.array(self.bSplinePoints, 'f'))

        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)

        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)

    def calcKnotenVek(self):
        """Berechne Knotenvektoren: Start- und Endvektor k mal
        am Anfrang/Ende der Kontrollpunkte, sonst beginnt die Linie woanders."""
        self.knotenvektor = []

        for i in range(self.k):
            self.knotenvektor.append(0)

        for n in range(1, len(self.controlpoints) -1 - (self.k -2)):
            self.knotenvektor.append(n)

        for m in range(self.k):
            self.knotenvektor.append(len(self.controlpoints) - (self.k -1))


    def findR(self, t):
        """Findet das größte Intervall in dem t drin ist"""
        for i in range(len(self.knotenvektor) - 1):
            if self.knotenvektor[i] > t:
                return i - 1


    def drawBSplineCurve(self):
        """Algo zum Bestimmen der Kurvenpunkte"""
        self.calcKnotenVek()
        if len(self.controlpoints) >= self.k -1 :
            t = 0
            #print(self.knotenvektor)
            while t < self.knotenvektor[-1]:
                r = self.findR(t)
                b = self.deBoor(self.controlpoints, self.knotenvektor, t, r, self.k - 1)

                self.bSplinePoints.append(b)
                t += 1 / float(self.m)

            self.bSplinePoints.append(self.controlpoints[-1])

            self.bSplineVBO = vbo.VBO(np.array(self.bSplinePoints, 'f'))

    def deBoor(self,controlpoints, knotenvektor, t, i, recursion):
        """DeBoor Algorithmus - recursion startet als Grad (Ordnung -1), i ist das betrachtete Intervall"""
        if recursion == 0:
            return controlpoints[i]
        alpha = (t - knotenvektor[i]) / (knotenvektor[i - recursion + self.k] - knotenvektor[i])
        return (1 - alpha) * self.deBoor(controlpoints, knotenvektor, t, i - 1, recursion - 1) + alpha * self.deBoor(controlpoints, knotenvektor, t, i, recursion - 1)


    def framebuffer_size_callback(self, win, width, height):
        """Mac ViewPort Fix"""
        glViewport(0,0, width, height)

    def onMouseButton(self, win, button, action, mods):
        """ Setze neuen Punkt"""

        if (button == glfw.MOUSE_BUTTON_LEFT):
            if action == glfw.PRESS:
                self.bSplinePoints = []
                xpos,ypos = glfw.get_cursor_pos(win)
                self.controlpoints.append(np.array([xpos, self.height - ypos]))
                self.pointVBO = vbo.VBO(np.array(self.controlpoints, 'f'))
                self.lineVBO = vbo.VBO(np.array(self.controlpoints, 'f'))

                self.drawBSplineCurve()



                #Draw Point

    def onKeyboard(self, win, key, scancode, action, mods):
        """ Verändert Ordnung und Anzahl der Punkt die in einem Intervall (bzw. pro Bezier) berechnet wird"""
        if action == glfw.PRESS:

            # Keys, die immer funktionieren sollen, auch wenn mod gedrueckt wird
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True

            if mods == glfw.MOD_SHIFT:
                if key == glfw.KEY_K:
                    self.k += 1

                    self.bSplinePoints = []
                    self.drawBSplineCurve()
                if key == glfw.KEY_M:
                    self.m += 1
                    self.bSplinePoints = []
                    self.drawBSplineCurve()
            if mods != glfw.MOD_SHIFT:
                if key == glfw.KEY_K:
                    if self.k > 2:
                        self.k -= 1

                        self.bSplinePoints = []
                        self.drawBSplineCurve()
                if key == glfw.KEY_M:
                    if self.m > 1:
                        self.m -= 1
                        self.bSplinePoints = []
                        self.drawBSplineCurve()

                if key == glfw.KEY_R:
                    self.bSplinePoints = []
                    self.controlpoints = []
                    self.knotenvektor = []
                if key == glfw.KEY_P:
                    self.showPolygon = not self.showPolygon

    def run(self):
        """ Main Loop"""
        while not glfw.window_should_close(self.window) and not self.exitNow:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
            glLoadIdentity()  # reset position

            #glViewport(0, 0, self.width, self.height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(0.0, self.width, 0.0, self.height, 0.0, 1.0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            glColor3f(1.0, 0.0, 0.0)  # set color to blue

            if len(self.controlpoints) > 0:
                if(self.showPolygon):
                    # Kontrollpunkte zeichnen
                    self.pointVBO.bind()
                    glEnableClientState(GL_VERTEX_ARRAY)
                    glPointSize(4)
                    glVertexPointerf(self.pointVBO)
                    glDrawArrays(GL_POINTS, 0, len(self.controlpoints))

                    # Kontrollpunkte verbinden


                    glColor3f(0.0, 0.0, 1.0)

                    glEnableClientState(GL_VERTEX_ARRAY)
                    glLineWidth(2)
                    glVertexPointerf(self.pointVBO)
                    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                    glDrawArrays(GL_POLYGON, 0, len(self.controlpoints))


                    self.pointVBO.unbind()
                    glDisableClientState(GL_VERTEX_ARRAY)

                if len(self.bSplinePoints) >= 1:
                    self.bSplineVBO.bind()

                    if(self.showPolygon):
                        glEnableClientState(GL_VERTEX_ARRAY)
                        glColor3f(1.0, 1.0, 0.0)
                        glPointSize(10)
                        glVertexPointerf(self.bSplineVBO)
                        glDrawArrays(GL_POINTS, 0, len(self.bSplinePoints))

                    glEnableClientState(GL_VERTEX_ARRAY)
                    glColor3f(1.0, 0.0, 0.0)
                    glLineWidth(8)
                    glVertexPointerf(self.bSplineVBO)
                    glDrawArrays(GL_LINE_STRIP, 0, len(self.bSplinePoints))

                    self.bSplineVBO.unbind()
                    glDisableClientState(GL_VERTEX_ARRAY)


                #self.lineVBO.bind()


                #self.lineVBO.unbind()




            glfw.swap_buffers(self.window)
            glfw.poll_events()
        glfw.terminate()


def main():

    rw = RenderWindow()
    rw.run()


# call main
if __name__ == '__main__':
    main()