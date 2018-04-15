# conding: utf-8

"""
SNMPGET example:
snmpget -v 2c -c demopublic test.net-snmp.org sysUpTime.0
system.sysUpTime.0 = Timeticks: (586752671) 67 days, 21:52:06.71


"""

from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

import datetime
from pysnmp.hlapi import *
import snmpbulkwalkv2 as bulk

class SNMPTools():
    def __init__(self, root):
        """Construtor da classe"""

        # Consts
        self.community = ''
        self.agent = ''
        self.OID = ''

        self.root = root # Root widget
        self.root.geometry("650x450") # Screen's initial size
        #self.root.minsize(width=530, height=320) # Screen's minimum size
        self.root.resizable(False, False) # Resizing disabled
        self.root.title('SNMPTools') # Screen's title

        # Icons imports
        self.icon_community_agent = PhotoImage(file='icons/community_agent.png')
        self.icon_send_snmpget = PhotoImage(file='icons/send_snmpget.png')
        self.icon_send_snmpbulkwalk = PhotoImage(file='icons/send_snmpbulkwalk.png')
        self.icon_sair = PhotoImage(file='icons/exit.png')

        # Menu
        self.menu = Menu(self.root) # Create a Menu widget
        self.main_menu = Menu(self.menu, tearoff=False) # Menu Item
        self.main_menu.add_command(label='Endereço e comunidade do agente',
                                   accelerator='Ctrl+A', compound='left',
                                   image=self.icon_community_agent,
                                   underline=0, command=self.address_agent)
        self.menu.add_separator() # Add a separator        
        self.main_menu.add_command(label='Enviar uma mensagem SNMPGET',
                                   accelerator='Ctrl+B', compound='left',
                                   image=self.icon_send_snmpget,
                                   underline=1, command=lambda : self.get_oid('snmpget'))
        self.menu.add_separator() # Add a separator
        self.main_menu.add_command(label='Enviar uma mensagem SNMPBULKWALK',
                                   accelerator='Ctrl+C', compound='left',
                                   image=self.icon_send_snmpbulkwalk,
                                   underline=2, command=lambda : self.get_oid('snmpbulkwalk'))
        self.menu.add_separator() # Add a separator
        self.main_menu.add_command(label='Sair',
                                   accelerator='Ctrl+D', compound='left',
                                   image=self.icon_sair,
                                   underline=3, command=self.sair)
        # Add item to menu
        self.menu.add_cascade(label="Opções", menu=self.main_menu)

        # Add menu to the app
        self.root.config(menu=self.menu)

        # Information bar
        self.barra_informacoes = Frame(root, height=25)
        self.barra_informacoes.pack(expand=0, fill='x')

        self.barra_informacoes_esq = Frame(self.barra_informacoes, height=25)
        self.barra_informacoes_esq.pack(expand=0, fill='x', side='left')

        self.barra_informacoes_dir = Frame(self.barra_informacoes, height=25)
        self.barra_informacoes_dir.pack(expand=0, fill='x', side='right')

        self.label_community = Label(self.barra_informacoes_esq, text='Community: ')
        self.label_community.grid(row=1, column=1, pady=2)

        self.label_community_value = Label(self.barra_informacoes_esq, text=self.community)
        self.label_community_value.grid(row=1, column=2, pady=2)
        
        self.label_agent = Label(self.barra_informacoes_esq, text='Agent address: ')
        self.label_agent.grid(row=2, column=1, pady=2)

        self.label_agent_value = Label(self.barra_informacoes_esq, text=self.agent)
        self.label_agent_value.grid(row=2, column=2, pady=2)
        
        self.clear_button = Button(self.barra_informacoes_dir, text='Clear', width=5, height=2,
                           padx=5, command=self.clear_state)
        self.clear_button.pack()

        self.separator = ttk.Separator(self.barra_informacoes, orient='horizontal')
        self.separator.pack()

        # Text Component
        self.text_messages = scrolledtext.ScrolledText(self.root, state='disabled')
        self.text_messages.pack(side='left')


    def clear_state(self):
        self.community = ''
        self.agent = ''
        self.OID = ''
        self.label_community_value.config(text=self.community)
        self.label_agent_value.config(text=self.agent)
        self.text_messages.config(state='normal')
        self.text_messages.delete(1.0, 'end')

    def write_message(self, message):
        self.text_messages.config(state='normal')
        self.text_messages.insert(END, message+'\n\n')

        self.text_messages.tag_configure('line', foreground='red', background='white')
        self.text_messages.insert(END, '='*78, 'line')
        self.text_messages.insert(END, '\n\n')

        self.text_messages.config(state='disabled')
        

    def address_agent(self):        
        address_agent_screen = Tk()
        address_agent_screen.title('Endereço e comunidade do agente')
        address_agent_screen.geometry("265x150") # Screen's initial size
        address_agent_screen.resizable(False, False) # Resizing disabled

        label = Label(address_agent_screen, text='Informe o endereço e \
a comunidade do agente\n', fg='green', font=('Arial', 8, 'bold'))
        label.grid(row=1, column=1, columnspan=2, pady=2)

        label_address = Label(address_agent_screen, text='Endereço: ')
        label_address.grid(row=2, column=1, pady=2)
        
        label_community = Label(address_agent_screen, text='Comunidade: ')
        label_community.grid(row=3, column=1, pady=2)        
        
        address = Entry(address_agent_screen)
        address.grid(row=2, column=2)
        
        community = Entry(address_agent_screen)        
        community.grid(row=3, column=2)
        community.focus_set()

        ok_button = Button(address_agent_screen, text='Ok', width=6, height=2,
                           command=lambda : self.read_content(address.get(), community.get(),
                                                              address_agent_screen.destroy()))
        ok_button.grid(row=4, column=2, columnspan=2, pady=6)

        address_agent_screen.mainloop()

    def get_oid(self, method):
        oid_screen = Tk()
        oid_screen.title('OID')
        oid_screen.geometry("220x40") # Screen's initial size
        oid_screen.resizable(False, False) # Resizing disabled
        

        label_oid = Label(oid_screen, text='OID: ')
        label_oid.grid(row=1, column=1, pady=2)
                        
        oid = Entry(oid_screen)
        oid.grid(row=1, column=2)            

        ok_button = Button(oid_screen, text='Ok', width=2, height=1,
                           command=lambda : self.read_oid(oid.get(), method, oid_screen.destroy()))
        ok_button.grid(row=1, column=3, columnspan=2, padx=4)

        oid_screen.mainloop()

    def read_oid(self, *args):            
            self.OID = args[0]
            if args[1] == 'snmpget':
                self.send_snmpget()
            if args[1] == 'snmpbulkwalk':
                self.send_snmpbulkwalk()

    def read_content(self, *args):                        
            self.agent, self.community = args[0], args[1]
            self.label_community_value.config(text=self.community)
            self.label_agent_value.config(text=self.agent)
            

    def snmp_get(self):        
        g = getCmd(SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.agent, 161)),
                   ContextData(),
                   #ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)))
                   ObjectType(ObjectIdentity(self.OID)))
        result= next(g) # A list of objects
        obj = result[-1] # The item of interest
        response = ''
        for x in obj:
            response = str(x) # Convert the data to str        
        
        return response
    
    def convert_time(self, time):
        scnds = time[:len(time)-2] # get the seconds
        milliscnds = time[len(time)-2:] # get the milliseconds        
        time_converted = str(datetime.timedelta(seconds=scnds)) # convert seconds to hours
            
        return time_converted+':'+milliscnds # add milliseconds to string
        
    
    def send_snmpget(self):        
        if len(self.community) == 0 or len(self.agent) == 0:
            messagebox.showwarning('Falha ao executar SNMPGET',
                                   'É preciso informar Comunidade e Endereço do Agente!')
        else:            
            try:                                
                if len(self.OID) == 0:
                    messagebox.showwarning('Falha ao ler o OID', 'É preciso informar OID!')
                else:                    
                    response = self.snmp_get()
                    if len(response) == 0:
                        raise Exception('Falha de comunicação')
                    self.write_message(response)
            except Exception as e:
                messagebox.showwarning('Falha ao executar SNMPGET', e)                

    def send_snmpbulkwalk(self):
        if len(self.community) == 0 or len(self.agent) == 0:
            messagebox.showwarning('Falha ao executar SNMPBULKWalk',
                                   'É preciso informar Comunidade e Endereço do Agente!')
        else:            
            try:                                
                if len(self.OID) == 0:
                    messagebox.showwarning('Falha ao ler o OID', 'É preciso informar OID!')
                else:
                    tuple_OID = tuple(str.split(self.OID, '.'))
                    list_temp = []
                    for i in tuple_OID:
                        list_temp.append(int(i))
                        
                    print(tuple(list_temp))
                    obj = bulk.SNMPBulkWalk(OID=tuple(list_temp))
                    obj.start()
                    response = obj.get_response()
                    
                    if len(response) == 0:
                        raise Exception('Falha de comunicação')
                    self.write_message(response)
            except Exception as e:
                messagebox.showwarning('Falha ao executar SNMPBULKWALK', e)   

    def sair(self):
        if messagebox.askokcancel(title="Sair", message="Deseja realmente sair?"):
            self.root.destroy()


# Application initialization
root = Tk() # A Tk object
app = SNMPTools(root) # SNMPTools object
root.mainloop() 
        
        
                                   
        
        
