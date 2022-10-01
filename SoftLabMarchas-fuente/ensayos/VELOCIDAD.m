%% Velocidad vs tiempo
dX=diff(DISTANCIA_TOBILLOS_mts);

for i=2:140
    dT(i-1)=TIEMPO_seg(i,1)-TIEMPO_seg(i-1,1);
end
VELOCIDAD=dX./dT;
