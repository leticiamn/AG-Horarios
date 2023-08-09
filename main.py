import random
import tkinter as tk
from tkinter import ttk

POPULATION_SIZE = 100
NUM_GENERATIONS = 500
MUTATION_RATE = 0.05

professores = {
    "professor1": "disciplina1",
    "professor2": "disciplina2",
    "professor3": "disciplina3",
    "professor4": "disciplina4",
    "professor5": "disciplina5",
    "professor6": "disciplina6",
    "professor7": "disciplina7",
    "professor8": "disciplina8",
}

HORARIOS_POR_DIA = 4
dias_semana = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira"]
horarios = [f"{i}º horário" for i in range(1, HORARIOS_POR_DIA+1)]
semestres_quantidade = 5
semestres = [f"semestre {i}" for i in range(1, semestres_quantidade+1)]


# Função para criar um indivíduo aleatório
def create_individual():
    individual = {f"semestre {i + 1}": {dia: [] for dia in dias_semana} for i in range(semestres_quantidade)}

    for semestre in individual.keys():
        for dia in dias_semana:
            for _ in range(HORARIOS_POR_DIA):
                professor = random.choice(list(professores.keys()))
                individual[semestre][dia].append(professor)

    return individual


# Contar choques de horário
def count_collisions(individual):
    collision_count = 0
    collisions = []

    for semester_1, days_1 in individual.items():
        for day, professors_1 in days_1.items():
            for position, professor in enumerate(professors_1):
                for semester_2, days_2 in individual.items():
                    if semester_2 != semester_1:
                        for other_day, professors_2 in days_2.items():
                            if other_day == day:
                                if professor in professors_2 and position < len(professors_2):
                                    collision_count += 1
                                    collision_info = {
                                        'professor': professor,
                                        'semestre 1': semester_1,
                                        'semestre 2': semester_2,
                                        'dia': day,
                                        'horario': position
                                    }
                                    collisions.append(collision_info)

    return collision_count


# Função para realizar o cruzamento entre dois indivíduos (crossover)
# Define um ponto de corte "CUTOFF" aleatoriamente e troca os horários antes e depois desse corte entre os individuos
def crossover(individual1, individual2):
    child1 = {}
    child2 = {}
    for semestre in individual1.keys():
        child1[semestre] = {}
        child2[semestre] = {}
        for dia in dias_semana:
            horarios1 = individual1[semestre][dia]
            horarios2 = individual2[semestre][dia]

            cutoff = random.randint(1, HORARIOS_POR_DIA - 1)
            child1[semestre][dia] = horarios1[:cutoff] + horarios2[cutoff:]
            child2[semestre][dia] = horarios2[:cutoff] + horarios1[cutoff:]
    return child1, child2


# Função para aplicar uma mutação em um indivíduo
def mutate(individual):
    for _ in range(int(len(semestres) * len(dias_semana) * HORARIOS_POR_DIA * MUTATION_RATE)):
        semestre = random.choice(semestres)
        dia = random.choice(dias_semana)
        professor_to_mutate = random.choice(list(professores.keys()))
        horarios = individual[semestre][dia]
        index_to_mutate = random.randint(0, len(horarios) - 1)
        horarios[index_to_mutate] = professor_to_mutate
    return individual


# Função para executar o algoritmo genético
def genetic_algorithm():
    # Inicializar a população
    population = [create_individual() for _ in range(POPULATION_SIZE)]

    # Executar as gerações
    for generation in range(NUM_GENERATIONS):
        population = sorted(population, key=lambda x: count_collisions(x))
        if count_collisions(population[0]) == 0:
            break  # Encontrou uma solução ótima, pode parar
        new_generation = population[:10]  # Elitismo: mantém os 5 melhores indivíduos
        while len(new_generation) < POPULATION_SIZE:
            # realiza o cruzamento entre dois individuos aleatórios
            parent1 = random.choice(population[:50])
            parent2 = random.choice(population[:50])
            child1, child2 = crossover(parent1, parent2)
            # aplica mutação e incluir os dois novos individuos na nova geração
            child1 = mutate(child1)
            new_generation.append(child1)
            child2 = mutate(child2)
            new_generation.append(child2)
        print(f"Geração: {generation}")
        population = new_generation
        population = sorted(population, key=lambda x: count_collisions(x))
        print(f"Choques: {count_collisions(population[0])}")

    # Ordenar a população novamente e selecionar o melhor indivíduo
    population = sorted(population, key=lambda x: count_collisions(x))
    best_individual = population[0]
    return best_individual

def buscar_disciplina_por_professor(professor):
    if professor in professores:
        return professores[professor]
    else:
        return ""


# Função para criar um dicionário com o melhor resultado, contendo as disciplinas
def create_result_dict(individual):
    for semestre, dias in individual.items():
        for dia, professores in dias.items():
            for i in range(len(professores)):
                professor = professores[i]
                disciplina = buscar_disciplina_por_professor(professor)
                professores[i] = f"{professor} - {disciplina}"
    return individual


# Função para criar a interface com o melhor resultado
def criar_tabela(frame, dados):
    tabela = ttk.Treeview(frame, show='headings')
    tabela['columns'] = tuple(dados.keys())

    for col in dados.keys():
        tabela.heading(col, text=col)
        tabela.column(col, width=150)

    for i, dia in enumerate(dados['segunda-feira']):
        row_data = [dados[col][i] for col in dados.keys()]
        tabela.insert("", "end", values=row_data)

    return tabela


# Gerar o melhor resultado
best_result = create_result_dict(genetic_algorithm())

# Avaliar o numero de choques do melhor resultado
collisions = count_collisions(best_result)
print(f"Choques do melhor individuo --------> {collisions}")

# Criar a interface
root = tk.Tk()
root.title("Horários")

# cria uma label para exibir na tela os choques
choques_label = tk.Label(root, text="", font=("Helvetica", 12))
choques_label.config(text=f"Choques de horário: {collisions}")
choques_label.pack(pady=20)

# Criar barras de rolagem
scrollbar_vertical = tk.Scrollbar(root, orient=tk.VERTICAL)
scrollbar_horizontal = tk.Scrollbar(root, orient=tk.HORIZONTAL)
scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)

# Criar um canvas para conter o frame com barras de rolagem
canvas = tk.Canvas(root, yscrollcommand=scrollbar_vertical.set, xscrollcommand=scrollbar_horizontal.set)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar_vertical.config(command=canvas.yview)
scrollbar_horizontal.config(command=canvas.xview)

# Adicionar o frame dentro do canvas
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor='nw')

# Criar as tabelas para cada semestre
for semestre, dados in best_result.items():
    semestre_frame = ttk.LabelFrame(frame, text=semestre)
    tabela = criar_tabela(semestre_frame, dados)
    semestre_frame.pack(padx=10, pady=10)
    tabela.pack()

# Permitir que o frame seja rolado
frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

root.mainloop()


