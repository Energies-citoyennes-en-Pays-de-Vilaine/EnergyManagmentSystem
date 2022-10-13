from file_reader import FileReader
from datetime import datetime
import matplotlib.pyplot as plt
fr = FileReader("../testData/courbe_SL.csv")
curve = fr.readData(0)

print(curve[:,0])
plt.plot(curve[:,0],curve[:,1])
plt.show()