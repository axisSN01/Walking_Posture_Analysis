import csv

file=open('paciente.csv','wb')
writer=csv.writer(file,delimiter=',')
writer.writerow(['tiempo','velocidad','distancia','tobillos izq'])
writer.writerow([1,2,3,4])
writer.writerow([2.2,3.3,4.4,5.5])
file.close()
