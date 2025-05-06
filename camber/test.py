import numpy as np
from scipy.optimize import curve_fit
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm


n_x = 11
n_y = 5
X0 = np.array([[198.15]*n_y, [223.15]*n_y,[248.15]*n_y,[273.15]*n_y,[298.15]*n_y,[323.15]*n_y,[348.15]*n_y,[373.15]*n_y,
              [398.15]*n_y,[423.15]*n_y,[448.15]*n_y,])
X = X0.flatten()


Y0 =np.array([16.0,17.0,18.0,19.0,20.0]*n_x).reshape((n_x,n_y))
Y= Y0.flatten()


Z0= np.array([[1.5,1.5040 ,1.4385 ,1.1440 ,1.005696],
            [1.3305,1.3374 ,1.2974 ,1.0936 ,1.004434],
            [1.1879,1.2089 ,1.1731 ,1.0625 ,1.003258],
            [1.0773,1.0906 ,1.0808 ,1.0297 ,1.002171],
            [1.000,1.0000 ,1.0000 ,1.0000 ,1.0000],
            [0.9073,0.9223 ,0.9285 ,0.9528 ,0.9999],
            [0.8422,0.8575 ,0.8548 ,0.9174 ,0.99943],
            [0.7922,0.7997 ,0.8133 ,0.8842 ,0.99869],
            [0.7438,0.7491 ,0.7630 ,0.8470 ,0.99804],
            [0.6918,0.7053 ,0.7212 ,0.8193 ,0.99748],
            [0.6536,0.6646 ,0.6818 ,0.7768 ,0.99700]])
Z= Z0.flatten()


#定义二元函数
#def func(xy, a,b,c,d,e,f):
def func(xy, a, c, d, e, f):
    x,y = xy
    # return a*x**2 + b*y**2 + c*x*y + d*x + e*y + f
    return a * x ** 2 + c * x * y + d * x + e * y + f


#准备数据
# X= np.linspace(0,10,10)
# Y= np.linspace(-10,5,10)
# Z = 5*X*X + 5*Y*Y + 5*X*Y + 5*X + 5*Y + 5 + 20*np.random.normal(size=(len(X)))


# 进行曲面拟合
#p0 = [5.e-06,3.77e-03,8.20e-04,-2.07e-02,-3.99e-01,8.2e+00] # 拟合参数的初始值
# params, pcov = curve_fit(func,(X,Y),Z, p0)
params, pcov = curve_fit(func,(X,Y),Z)
# a,b,c,d,e,f = params
a,c,d,e,f = params
print(f"拟合参数={params}")
print(pcov)


print(f"np.abs(pcov).max()= {np.abs(pcov).max()}")


def fit_surface(x,y):
    # return a*x**2 + b*y**2 + c*x*y + d*x + e*y + f
    return a * x ** 2  + c * x * y + d * x + e * y + f


print(f"fit_surface(298.15,20)= {fit_surface(298.15,20)}")
print(f"fit_surface(448.15,20)= {fit_surface(448.15,20)}")
np_fit_surface = np.frompyfunc(fit_surface,2,1) # nin, 输入参数的数量，nout 返回值的数量
z_fit = np_fit_surface(X,Y)
error = z_fit-Z
print(f"np.abs(error).sum()/len(error)= {np.abs(error).sum()/len(error)}")


z_fit = z_fit.reshape((n_x,n_y))


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X,Y,Z,c="red") # 原始数据
# ax.plot_surface(X0, Y0, z_fit, rcount=100,ccount=100,cmap='jet', alpha=0.99)
ax.plot_surface(X0, Y0, z_fit,cmap='jet', alpha=0.99)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title("曲面拟合")
plt.show()