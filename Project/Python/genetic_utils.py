import numpy as np

def crossover(par1, par2):
    dim_size = len(par1)

    sel = np.random.choice(dim_size, np.random.randint(dim_size), replace=False)

    ch1 = np.zeros(dim_size)
    ch2 = np.zeros(dim_size)

    for ix in range(dim_size):
        if ix in sel:
            ch1[ix] = 0.5 * (par1[ix] + par2[ix])
            ch2[ix] = par1[ix]

        else:
            ch1[ix] = par2[ix]
            ch2[ix] = 0.5 * (par1[ix] + par2[ix])

    ch1[0] = min(3, max(1, int(ch1[0])))
    ch2[0] = min(3, max(1, int(ch1[0])))

    return ch1, ch2


def mutate(par1):
    noise = np.random.normal(0, 5, par1.shape)
    noise[-1] /= 20
    noise[0] /= 20
    mut = par1 + noise
    mut[0, 0] = min(3, max(1, int(mut[0, 0])))
    return mut[0]


def create_new_population(genomes, fitness, par_pct, child_pct, mut_pct):
    # Size of the population
    N = len(genomes)

    # Apply softmax probability calculation
    prob_distro = fitness / np.sum(fitness)

    # Allocate places in the population according to the given probabilities
    num_par = int(np.floor(N * par_pct))
    num_child = int(np.floor(N * child_pct / 2))
    num_mut = int(N - num_par - num_child * 2)

    new_pop = []

    # Add best parents
    best_par = np.random.choice(N, num_par, replace=False, p=prob_distro)
    for ix in best_par:
        # print(fitness[ix])
        new_pop.append(genomes[ix])

    # Match parents and add children
    for ix in range(num_child):
        idx = np.random.choice(N, 2, replace=False, p=prob_distro)
        (ch1, ch2) = crossover(genomes[idx[0]], genomes[idx[1]])
        new_pop.append(ch1)
        new_pop.append(ch2)

    # Add mutants
    for ix in range(num_mut):
        par1_idx = np.random.choice(N, 1)
        new_pop.append(mutate(genomes[par1_idx]))

    return new_pop, np.ones(N) / N