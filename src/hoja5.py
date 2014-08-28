"""
Hoja de trabajo 5

Este programa tiene como propósito principal simular el trabajo de un sistema
operativo, realizando instrucciones y esperando espacio en memoria RAM y en CPU

Sergio Cancinos, 13062
Angel Basegoda, 13256

"""
import random

import simpy


RANDOM_SEED = 42
NEW_PROCESS = 25  # Numero de procesos
INTERVAL_PROCESS = 10  # Genera el intervalo en el cual se crearan los procesos
number = 25

def source(env, NEW_PROCESS, interval, RAM, CPU, WAITING):
    #se crean los procesos a realizar
    for i in range(number):
        instrucciones = random.randint(1,10)
        memoria = random.randint(1,10)
        c = proceso(env, 'ID%03d' % i, memoria, RAM, CPU, WAITING, instrucciones)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


#se define lo que tendra cada proceso
def proceso(env, processID, memoria, RAM, CPU, WAITING, instrucciones):
    arrive = env.now
    print ('%7.4f %s: NUEVO (esperando RAM %s), RAM disponible: %s' % (arrive, processID, memoria, RAM.level))

    with RAM.get(memoria) as req:
        yield req

        #se notifica el momento en el que llega el proceso a esperar RAM
        wait = env.now - arrive
        
        print ('%7.4f %s: READY Se espero RAM %6.3f' % (env.now, processID, wait))

        #se realizan las instrucciones que necesita realizar el proceso
        while instrucciones > 0:
            with CPU.request() as reqCPU:
                yield reqCPU
                #print ('%7.4f %s: RUNNING instrucciones %6.3f' % (env.now, processID))

                #solamente se le dedica una unidad de tiempo en el CPU
                yield env.timeout(1)

                if instrucciones > 3:
                    instrucciones = instrucciones - 3
                else:
                    instrucciones = 0
                
            if instrucciones > 0:
                siguiente = random.choice(("ready","waiting"))
                if siguiente == "waiting":
                    with WAITING.request() as reqWAITING:
                        yield reqWAITING
                        print('%7.4f %s: WAITING' % (env.now, processID))

                        yield env.timeout(1)

                print('%7.4f %s: READY' % (env.now, processID))

        tiempoProceso = env.now - arrive
        global tiempoPromedio
        tiempoPromedio = tiempoPromedio + tiempoProceso
        print('%7.4f %s: TERMINATED tiempo de ejecucion: %s' % (env.now, processID, tiempoProceso))

        with RAM.put(memoria) as reqDevolverRAM:
            yield reqDevolverRAM
            print('%7.4f %s: Regresando RAM %s' % (env.now, processID, memoria))

random.seed(RANDOM_SEED)
env = simpy.Environment()

CPU = simpy.Resource(env, capacity=1)
RAM = simpy.Container(env, init=100, capacity=100)
WAITING = simpy.Resource(env, capacity=1)
env.process(source(env, NEW_PROCESS, INTERVAL_PROCESS, RAM, CPU, WAITING))
tiempoPromedio = 0
env.run()
print('TIEMPO PROMEDIO: %6.3f' % (tiempoPromedio/25))





















                
