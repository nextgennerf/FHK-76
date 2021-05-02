''' 
Created on Apr 24, 2021

@author: Jeffrey Blum
'''
import sys, asyncio
import concurrent.futures as cf

class TerminalSimulator:
    '''
    A terminal call/response module that simulates the blaster.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.events = {}
    
    async def run(self):
        print("FHK-76 Terminal Simulator launched")
        while True:
            loop = asyncio.get_running_loop()
            with cf.ThreadPoolExecutor() as pool:
                command = await loop.run_in_executor(pool, lambda: input(''))
            cWords = command.split()
            if command == "help":
                print("The following are valid commands. If brackets are present, any one option can be used.")
                print("   trigger [touch, pull, relax, release]")
                print("   second trigger [pull, release]")
                print("   safety [on, off]")
                print("   [semi, burst, auto] press")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
                # print("Pull trigger")
            elif cWords[0] == "trigger":
                if cWords[1] == "pull":
                    self.events["trigger press"].set()
                else:
                    self.events[command].set()
            elif cWords[1] == "press":
                self.events[command].set()
            elif command == "second trigger pull":
                pass
            elif command == "second trigger release":
                pass
            elif command == "safety on":
                self.events["safety press"].set()
            elif command == "safety off":
                self.events["safety release"].set()
            elif command == "power off":
                sys.exit()
            else:
                print('Invalid command. To see a list of valid commands, enter "help".')
    
    def addEvent(self, name, event):
        self.events[name] = event