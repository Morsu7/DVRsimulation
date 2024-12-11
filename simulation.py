class Node:
    def __init__(self, name):
        # Inizializza un nodo con il suo nome e una tabella di routing vuota
        self.name = name
        self.routing_table = {}  # Tabella di routing: Destinazione -> (Distanza, Prossimo Nodo)

    def update_routing_table(self, neighbor, neighbor_table, weight):
        """
        Aggiorna la tabella di routing del nodo utilizzando i dati ricevuti dal nodo vicino.
        L'algoritmo si basa sull'aggiornamento delle distanze alle destinazioni in base ai percorsi
        attraverso il nodo vicino.
        """
        updated = False  # Flag per verificare se ci sono aggiornamenti nella tabella
        for dest, (dist, _) in neighbor_table.items():
            new_dist = weight + dist  # Calcola la nuova distanza aggiungendo il peso del collegamento
            # Se non c'è una rotta o se questa è più breve, aggiorna la tabella
            if dest not in self.routing_table or new_dist < self.routing_table[dest][0]:
                self.routing_table[dest] = (new_dist, neighbor)  # Aggiorna la destinazione con la nuova distanza e il prossimo hop
                updated = True  # Segnala che è stato fatto un aggiornamento
        return updated

    def __str__(self):
        """
        Rappresentazione leggibile della tabella di routing del nodo in formato stringa.
        Mostra tutte le destinazioni, le distanze e i rispettivi prossimi hop.
        """
        table = f"Routing Table for {self.name}:\n"
        table += f"{'Destination':<15} {'Distance':<10} {'Next-Hop'}\n"
        table += "-" * 40 + "\n"
        # Aggiunge le righe per ogni destinazione e la distanza a quella destinazione
        for dest, (dist, next_hop) in self.routing_table.items():
            table += f"{dest:<15} {dist:<10} {next_hop}\n"
        return table


class Network:
    def __init__(self):
        # Inizializza la rete con una lista di nodi e una lista di collegamenti
        self.nodes = {}  # Dizionario di nodi: nome del nodo -> Oggetto Node
        self.links = {}  # Dizionario di collegamenti: (Nodo1, Nodo2) -> Peso del collegamento

    def add_node(self, name):
        """
        Aggiunge un nodo alla rete con il nome specificato.
        """
        self.nodes[name] = Node(name)  # Crea un oggetto Node e lo aggiunge alla rete

    def add_link(self, node1, node2, weight):
        """
        Aggiunge un collegamento bidirezionale tra due nodi con il peso specificato.
        Un collegamento tra nodo1 e nodo2 viene aggiunto in entrambe le direzioni.
        """
        self.links[(node1, node2)] = weight  # Collega nodo1 a nodo2 con il peso
        self.links[(node2, node1)] = weight  # Collega nodo2 a nodo1 con lo stesso peso (bidirezionale)

    def initialize_routing_tables(self):
        """
        Inizializza le tabelle di routing per tutti i nodi della rete.
        Ogni nodo conosce la distanza a sé stesso (0), ai nodi vicini diretti (peso del collegamento)
        e a tutti gli altri nodi (distanza infinita inizialmente).
        """
        for node in self.nodes.values():  # Per ogni nodo della rete
            for other in self.nodes:  # Per ogni altro nodo della rete
                if other == node.name:
                    # La distanza a sé stesso è zero
                    node.routing_table[other] = (0, other)
                elif (node.name, other) in self.links:
                    # La distanza al nodo vicino è il peso del collegamento
                    node.routing_table[other] = (self.links[(node.name, other)], other)
                else:
                    # La distanza agli altri nodi è inizialmente infinita
                    node.routing_table[other] = (float('inf'), None)

    def run_distance_vector(self):
        """
        Esegue l'algoritmo di Distance Vector Routing fino a convergenza.
        Ogni nodo scambia informazioni con i suoi vicini per aggiornare le tabelle di routing.
        Questo processo continua fino a che nessun nodo effettua più aggiornamenti alle tabelle.
        """
        self.initialize_routing_tables()  # Inizializza le tabelle di routing
        print("Tabella di routing iniziale prima dello scambio dei Distance Vectors:")
        self.print_routing_tables()  # Stampa le tabelle di routing iniziali
        print("\nInizio simulazione Distance Vector Routing...\n")

        converged = False  # Flag per verificare se la rete ha raggiunto la convergenza
        iteration = 0  # Contatore delle iterazioni

        # Salva le tabelle di routing precedenti per confrontare i cambiamenti
        prev_routing_tables = {node.name: dict(node.routing_table) for node in self.nodes.values()}

        # Ciclo fino a che la rete non converge
        while not converged:
            print(f"\nIterazione {iteration}:\n")
            converged = True  # Presuppone che la rete sia convergente a meno che non vengano fatti aggiornamenti
            for (node1, node2), weight in self.links.items():
                n1 = self.nodes[node1]  # Ottieni il nodo1
                n2 = self.nodes[node2]  # Ottieni il nodo2

                # Aggiorna le tabelle di routing in entrambe le direzioni
                updated1 = n1.update_routing_table(node2, n2.routing_table, weight)  # Aggiorna nodo1
                updated2 = n2.update_routing_table(node1, n1.routing_table, weight)  # Aggiorna nodo2

                if updated1 or updated2:
                    converged = False  # Se almeno un nodo ha aggiornato la sua tabella, la rete non è ancora convergente

            # Confronta e stampa le differenze tra la tabella di routing attuale e quella precedente
            self.print_routing_tables(prev_routing_tables)
            # Salva le tabelle di routing attuali per il confronto nella prossima iterazione
            prev_routing_tables = {node.name: dict(node.routing_table) for node in self.nodes.values()}
            iteration += 1  # Incrementa il numero delle iterazioni

        print("\nConvergenza raggiunta dopo", iteration, "iterazioni!")

    def print_routing_tables(self, prev_routing_tables=None):
        """
        Stampa le tabelle di routing di tutti i nodi.
        Se 'prev_routing_tables' è fornito, confronta le tabelle attuali con quelle precedenti
        e evidenzia le differenze.
        """
        for node in self.nodes.values():  # Per ogni nodo nella rete
            print(node)  # Stampa la tabella di routing del nodo
            if prev_routing_tables:
                print(f"\nDifferenze rispetto alla tabella precedente per {node.name}:")

                current_table = node.routing_table  # Tabella di routing attuale
                prev_table = prev_routing_tables.get(node.name, {})  # Tabella di routing precedente

                # Confronta le tabelle per ogni destinazione
                for dest, (dist, next_hop) in current_table.items():
                    if dest in prev_table:  # Se la destinazione era presente anche nella tabella precedente
                        prev_dist, prev_next_hop = prev_table[dest]
                        if dist != prev_dist:  # Se la distanza è cambiata
                            print(f"Dest: {dest}, Dist: {dist} (cambiato da {prev_dist}), Next-Hop: {next_hop}")
                    else:
                        # Se la destinazione è nuova
                        print(f"Dest: {dest}, Dist: {dist}, Next-Hop: {next_hop} (Nuovo)")

            print("-" * 40)  # Separatore visivo tra le tabelle dei nodi


# Esempio di utilizzo con 6 nodi
if __name__ == "__main__":
    network = Network()

    # Aggiungi nodi
    for i in range(1, 7):
        network.add_node(f"Node{i}")

    # Aggiungi collegamenti tra nodi
    network.add_link("Node1", "Node2", 1)
    network.add_link("Node2", "Node3", 2)
    network.add_link("Node3", "Node4", 1)
    network.add_link("Node4", "Node5", 3)
    network.add_link("Node5", "Node6", 1)

    # Aggiungi alcuni collegamenti non lineari per aumentare la complessità
    network.add_link("Node1", "Node3", 5)
    network.add_link("Node2", "Node5", 4)
    network.add_link("Node3", "Node6", 2)

    # Esegui la simulazione
    network.run_distance_vector()
