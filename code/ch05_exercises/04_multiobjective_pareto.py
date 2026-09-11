"""计算信噪比最大、时间和损伤最小的Pareto前沿。"""
import numpy as np

power=np.linspace(.1,1,30); time=np.linspace(.1,2,35)
P,T=np.meshgrid(power,time,indexing="ij")
snr=np.sqrt(P*T)/(1+.2*P*T); damage=(P*T)**1.7; duration=T
points=np.c_[snr.ravel(),damage.ravel(),duration.ravel(),P.ravel(),T.ravel()]
keep=[]
for i,a in enumerate(points):
    dominated=np.any((points[:,0]>=a[0])&(points[:,1]<=a[1])&(points[:,2]<=a[2]) &
                     ((points[:,0]>a[0])|(points[:,1]<a[1])|(points[:,2]<a[2])))
    if not dominated: keep.append(i)
front=points[keep]
print("Pareto points:",len(front))
print("snr damage duration power time")
print(front[np.argsort(front[:,0])][::max(1,len(front)//10)].round(3))
