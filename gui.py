import tkinter
from tkinter import *
from tkinter import ttk
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame


class GUI:
    def __init__(self, master):

        self.myFrame = Frame(master)
        self.myFrame.pack()
        self.table = None
        self.tableScrollView = None
        self.barGraph = None

        # taby do GUI
        tabControl = ttk.Notebook(master)
        self.tableTab = ttk.Frame(tabControl)
        self.graphTab = ttk.Frame(tabControl)
        self.machineLearningTab = ttk.Frame(tabControl)
        tabControl.add(self.tableTab, text='Tabele')
        tabControl.add(self.graphTab, text='Wykresy')
        tabControl.add(self.machineLearningTab, text='Uczenie maszynowe')
        tabControl.pack(expand=True, fill="both")

        # część do tabu z tabelą
        self.tableTitle = Label(self.tableTab, text="", font=(None, 20))
        self.tableTitle. place(relx=.5, y=200, anchor=CENTER)
        label = Label(self.tableTab, text="Wybierz tabelę", font=(None, 20)).place(relx=.5, y=65, anchor=CENTER)
        # options menu na wybranie odpowiedniej tabeli
        tables = ["Stacje pomiarowe", "Stanowiska pomiarowe", "Dane pomiarowe", "Indeks jakości powietrza"]
        tkvar = StringVar(master)
        tkvar.set(tables[0])
        chooseTable = tkinter.OptionMenu(self.tableTab, tkvar, *tables, command=self.get_data)
        chooseTable.pack(pady=100)

        # część do tabu z wykresami

        # miejsce w którym udało się zaimplementować scrollowanie
        self.canvas = Canvas(self.graphTab)
        self.frame = Frame(self.canvas)
        self.vsb = Scrollbar(self.graphTab, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y", expand=0)
        self.canvas.pack(fill="both", expand=1)
        self.canvas.create_window((840, 0), window=self.frame, anchor=CENTER,
                                  tags="self.frame", width=1000)
        self.frame.bind("<Configure>", self.onFrameConfigure)




        self.graphTitle = Label(self.frame, text="", font=(None, 17))
        self.graphTitle.place(relx=.5, y=200, anchor=CENTER)


        label = Label(self.frame, text="Wybierz stację pomiarową", font=(None, 20)).place(relx=.5, y=65, anchor=CENTER)
        tkvar = StringVar(master)

        stacjePomiarowe = self.stacje_pomiarowe();
        tkvar.set(stacjePomiarowe[0][0]) # tutaj stacje pomiarowe
        chooseTable = tkinter.OptionMenu(self.frame, tkvar, *stacjePomiarowe[0], command=self.stanowiska_pomiarowe)
        chooseTable.pack(pady=100)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    #pobiera nazwy stacji pomiarowych
    def stacje_pomiarowe(self):
        nazwy_stacji = []
        id_stacji = []
        response = requests.get("https://api.gios.gov.pl/pjp-api/rest/station/findAll")
        json = response.json()
        for x in json:
            nazwy_stacji.append((x['stationName']))
            id_stacji.append((x['id']))
        return nazwy_stacji,id_stacji


    #pobiera stanowiska pomiarowe dla id danej stacji pomiarowej
    def stanowiska_pomiarowe(self, selection):

        self.graphTitle.configure(text=selection)
        print(selection)

        lista_stacji = self.stacje_pomiarowe();
        ilosc_stacji = len(lista_stacji[0]);

        for x in range(ilosc_stacji):
            if lista_stacji[0][x] == selection:
                id = lista_stacji[1][x]

        path = "https://api.gios.gov.pl/pjp-api/rest/station/sensors/" + str(id)
        response = requests.get(path)
        json = response.json()

        id_stanowiska = []

        for x in json:
            id_stanowiska.append((x['id']))
        self.create_graph(id_stanowiska)

    # metoda na pobranie danych z odpowiedniego api i ustawienie ich do tabeli
    def get_data(self, selection):

        if self.table is not None:
            self.delete_table()

        self.tableTitle.configure(text=selection)
        # słownik zawierający nazwy tabel wraz z odpowiednimi api
        tables = {"Stacje pomiarowe": "https://api.gios.gov.pl/pjp-api/rest/station/findAll",
                  "Stanowiska pomiarowe": "https://api.gios.gov.pl/pjp-api/rest/station/sensors/14",
                  "Dane pomiarowe": "https://api.gios.gov.pl/pjp-api/rest/data/getData/92",
                  "Indeks jakości powietrza": "https://api.gios.gov.pl/pjp-api/rest/aqindex/getIndex/52"}

        # pobieranie danych z odpowiedniego api i wywołanie funkcji na tworzenie tabel z tych danych
        for key in tables:
            if key == selection:
                response = requests.get(tables[key])
                json = response.json()
                if type(json) is list:
                    jsonKeys = json[0]
                else:
                    jsonKeys = json
                self.create_table(jsonKeys, json)

    # metoda na stworzenie tabeli z danymi
    def create_table(self, jsonKeys, json):

        i = 0
        # dodanie ilości kolumn w tabeli
        columns = list(range(0, len(jsonKeys)))

        # tworzenie tabeli
        self.table = ttk.Treeview(self.tableTab, columns=columns, show='headings', height=30)

        # dodanie nazw kolumn do tabeli
        for key in jsonKeys:
            self.table.heading("#" + str(i + 1), text=key)
            i += 1

        # dodanie danych do tabeli
        if type(json) is list:
            for row in json:
                self.table.insert("", END, values=(list(row.values())))
        else:
            self.table.insert("", END, values=(list(json.values())))
        self.table.pack(side=BOTTOM)

        # dodanie scroll horyzontalny do tabeli
        self.tableScrollView = Scrollbar(self.tableTab, orient='horizontal')
        self.tableScrollView.pack(side=BOTTOM, fill='x')
        self.tableScrollView.config(command=self.table.xview)
        self.table.configure(xscrollcommand=self.tableScrollView.set)

    # metoda na usunięcie tabeli z danymi
    def delete_table(self):
        self.table.destroy()
        self.tableScrollView.destroy()

    # metoda na stworzenie wykresu (tu macie przykładowe wykresy na których możecie się wzorować)
    def create_graph(self, dane):

        if self.barGraph is not None:
            self.delete_graph()

        ilosc = len(dane);
        i = 0;

        for x in range(ilosc):
            i = i + 1;
            id = str(dane[x])
            path = "https://api.gios.gov.pl/pjp-api/rest/data/getData/" + id;
            response = requests.get(path);
            json = response.json()

            values = json["values"]
            key = json["key"]
            date = []
            value = []

            for x in values:
                date.append(x["date"])
                value.append(x["value"])

            d1 = {'Date' : date, 'Value' : value}
            df1 = DataFrame(d1, columns=['Date', 'Value'])

            figure1 = plt.Figure(figsize=(4, 3), dpi=100)
            ax1 = figure1.add_subplot(111)
            self.barGraph = FigureCanvasTkAgg(figure1, self.frame)
            self.barGraph.get_tk_widget().pack()
            df1 = df1[['Date', 'Value']].groupby('Date').sum()
            df1.plot(kind='bar', legend=True, ax=ax1)
            ax1.set_title(key)

    # metoda na usunięcie wykresu
    def delete_graph(self):
        self.barGraph.get_tk_widget().destroy()
        self.barGraph = None

def main():
    window = Tk()
    window.title('Big data i hurtownie danych')
    window.geometry('1660x900')
    e = GUI(window)
    window.mainloop()


if __name__ == "__main__":
    main()