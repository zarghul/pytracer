import math
import numpy as np

from .math_utils import *

class Ray:
    def __init__(self,origin,direction):
        self.origin = np.array(origin)
        self.direction = normalize(np.array(direction))

class Light:
    def __init__(self,origin,color):
        self.origin = np.array(origin)
        self.color = np.array(color)


class Material:
    def __init__(self,diffuse_c,specular_c,specular_k,reflection):
        self.diffuse_c = diffuse_c
        self.specular_c = specular_c
        self.specular_k = specular_k
        self.reflection = reflection




class Camera:
    def __init__(self,origin,direction,up_dir,fov,ratio):
        self.origin = np.array(origin)
        self.direction = normalize(np.array(direction))
        self.up_dir = normalize(np.array(up_dir))
        self.fov = fov
        self.ratio=ratio
    
    def ray_generator(self,resolution_x,resolution_y):
        def gen():
            fov_x = self.fov
            fov_y = self.fov/self.ratio

            base_dir = self.direction
            y_dir = self.up_dir
            x_dir = cross(base_dir,y_dir)

            orig = self.origin

            for i in range(resolution_x):
                x = i-resolution_x/2
                alpha_x = x*fov_x/resolution_x
                dx = math.tan(alpha_x)
                for j in range(resolution_y):
                    y = j-resolution_y/2
                    alpha_y = y*fov_y/resolution_y
                    dy = math.tan(alpha_y)

                    dv = y_dir*dy+x_dir*dx
                    d = normalize(base_dir+dv)

                    yield i,j,Ray(orig,d)

        return gen


class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []
        self.camera = Camera([0.,0.,0.],[0., 0., -1.],[0.,1.,0.],math.pi/3,1)
        self.ambient = 0.


    def intersect(self,ray):
        # Find first point of intersection with the scene.
        t_min = np.inf
        obj_min = None
        for obj in self.objects:
            t_obj = obj.intersect(ray)
            if t_obj < t_min:
                t_min, obj_min = t_obj, obj
        # Return None if the ray does not intersect any object.
        if t_min == np.inf:
            return None
        # Find the point of intersection on the object.
        P = ray.origin + ray.direction * t_min
        #return object intersected and point of intersection
        return (obj_min,P)

    def trace_ray(self,ray):
        intersection = self.intersect(ray)
        if intersection == None:
            return None
        obj,P = intersection
        N = obj.normal(P)
        cameraDir = normalize(self.camera.origin- P) 

        # ambient light
        color = self.ambient
        
        for light in self.lights:
            lightDir = normalize(light.origin - P)
            lightIntersection = self.intersect(Ray(P+0.0001*N,lightDir))
            if lightIntersection == None:
                # Lambert shading (diffuse).
                color += obj.material.diffuse_c*max(np.dot(N,lightDir),0) * obj.get_color(P)
                # Blinn-Phong shading (specular).
                color += obj.material.specular_c * max(np.dot(N, normalize(lightDir + cameraDir)), 0) ** obj.material.specular_k * light.color

        return color,P,N,obj

        

    def draw(self,w,h,depth,antialias):
        W = w*antialias
        H = h*antialias
        r = float(W) / H
        color = np.zeros(3)
        IMG = np.zeros((H,W,3))
         
        rays = self.camera.ray_generator(W,H)
        # Loop through all pixels.
        oldperc = -1
        for i, j, ray in rays():
            perc = int((i*H+j)*100/(W*H))
            if perc % 5  == 0 and perc != oldperc:
                print (perc, "%")
                oldperc = perc
            color = np.zeros(3)
            reflection = 1.


            for k in range(depth):
                traced = self.trace_ray(ray)
                if traced == None:
                    break
                c,P,N,obj = traced
                color += reflection*c
                reflection *= obj.material.reflection
                
                #reflected ray
                O = P+N*0.0001
                D = normalize(ray.direction - 2*np.dot(ray.direction,N)*N)
                ray = Ray(O, D)

            IMG[H - j - 1, i, :] = np.clip(color, 0, 1)
         
        img = np.zeros((h,w,3))
        for i in range(h):
            for j in range(w):
                color = np.zeros(3)
                for k in range(antialias):
                    for l in range(antialias):
                        color += IMG[i*antialias+k,j*antialias+l]
                img[i,j] = color/(antialias**2)
        return img

